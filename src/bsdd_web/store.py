"""Project storage and the in-memory collaboration engine.

Each project lives in ``<data>/projects/<id>/``::

    dictionary.json   the bSDD JSON (always a valid, importable file)
    extras.json       editor-only data (temporary property sets, LOIN, export settings)
    meta.json         name, timestamps
    snapshots/        rolling copies of dictionary.json + extras.json

While somebody has a project open, it is held in memory. Every change is an
operation (see :mod:`bsdd_web.ops`); the resulting JSON patch is broadcast to all
connected clients. Undo/redo is tracked per client.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import secrets
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from bsdd_json import BsddDictionary

from . import jsonpatch
from .config import Settings
from .ops import Ctx, Extras, OpError
from .ops import run as run_op

logger = logging.getLogger(__name__)

ID_RE = re.compile(r"^[A-Za-z0-9_-]{16,64}$")
MAX_HISTORY = 100


def new_project_id() -> str:
    return secrets.token_urlsafe(16)


def _atomic_write(path: Path, data: bytes) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    tmp.replace(path)


def _json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, indent=1).encode("utf-8")


@dataclass
class HistoryEntry:
    patch: jsonpatch.Patch  # what to apply to undo/redo
    guards: list[Any]
    label: str


@dataclass
class ClientInfo:
    client_id: str
    name: str
    color: str
    queues: list[asyncio.Queue] = field(default_factory=list)
    selection: dict[str, Any] = field(default_factory=dict)
    role: str = "edit"

    def public(self) -> dict[str, Any]:
        return {"id": self.client_id, "name": self.name, "color": self.color, "selection": self.selection, "role": self.role}


class Project:
    def __init__(self, pid: str, root: Path, dictionary: BsddDictionary, extras: Extras, meta: dict[str, Any]):
        self.id = pid
        self.root = root
        self.dictionary = dictionary
        self.extras = extras
        self.meta = meta
        self.lock = asyncio.Lock()
        self.version = 0
        self.doc = self._dump()
        self.clients: dict[str, ClientInfo] = {}
        self.undo: dict[str, list[HistoryEntry]] = {}
        self.redo: dict[str, list[HistoryEntry]] = {}
        self.dirty = False
        self.last_change = 0.0
        self.last_snapshot = time.time()
        self.last_seen = time.time()
        self._save_task: asyncio.Task | None = None
        #: open websocket connections with the access version they were granted
        self.connections: list[dict[str, Any]] = []

    # ------------------------------------------------------------------ state

    def _dump(self) -> dict[str, Any]:
        return {
            "dictionary": self.dictionary.model_dump(mode="json", exclude_none=True),
            "extras": self.extras.model_dump(mode="json"),
        }

    def _load_doc(self, doc: dict[str, Any]) -> None:
        self.dictionary = BsddDictionary.model_validate(doc["dictionary"])
        self.extras = Extras.model_validate(doc.get("extras") or {})

    def _restore(self) -> None:
        """Roll back in-memory models to the last committed document."""
        self._load_doc(self.doc)

    def _commit(self, new_doc: dict[str, Any]) -> jsonpatch.Patch:
        patch = jsonpatch.diff(self.doc, new_doc)
        self.doc = new_doc
        if patch:
            self.version += 1
            self.dirty = True
            self.last_change = time.time()
            self.meta["name"] = self.dictionary.DictionaryName or self.dictionary.DictionaryCode
        return patch

    # ------------------------------------------------------------------ operations

    def apply_op(self, client_id: str | None, name: str, args: dict[str, Any] | None) -> tuple[Any, jsonpatch.Patch]:
        """Run an operation (synchronously; call while holding ``self.lock``)."""
        ctx = Ctx(dictionary=self.dictionary, extras=self.extras)
        try:
            result = run_op(ctx, name, args)
        except OpError:
            self._restore()
            raise
        except Exception as exc:
            logger.exception("Operation %s failed", name)
            self._restore()
            raise OpError(f"Internal error in '{name}': {exc}") from exc
        self.dictionary = ctx.dictionary
        self.extras = ctx.extras
        before = self.doc
        new_doc = self._dump()
        patch = self._commit(new_doc)
        if patch and client_id:
            inverse = jsonpatch.diff(new_doc, before)
            guards = jsonpatch.make_guards(new_doc, inverse, patch)
            stack = self.undo.setdefault(client_id, [])
            stack.append(HistoryEntry(inverse, guards, name))
            del stack[:-MAX_HISTORY]
            self.redo.pop(client_id, None)
        return result, patch

    def _history_step(self, client_id: str, source: dict, target: dict) -> tuple[str, jsonpatch.Patch]:
        stack = source.get(client_id) or []
        if not stack:
            raise OpError("Nothing to undo" if source is self.undo else "Nothing to redo")
        entry = stack[-1]
        try:
            new_doc = jsonpatch.apply_guarded(self.doc, entry.patch, entry.guards)
            before = self.doc
            self._load_doc(new_doc)
        except jsonpatch.PatchConflict as exc:
            stack.pop()
            raise OpError("This change was modified by someone else in the meantime and cannot be reverted") from exc
        except Exception as exc:
            stack.pop()
            self._restore()
            raise OpError(f"Cannot revert this change: {exc}") from exc
        stack.pop()
        new_doc = self._dump()  # normalised
        patch = self._commit(new_doc)
        inverse = jsonpatch.diff(new_doc, before)
        guards = jsonpatch.make_guards(new_doc, inverse, patch)
        target.setdefault(client_id, []).append(HistoryEntry(inverse, guards, entry.label))
        return entry.label, patch

    def undo_step(self, client_id: str) -> tuple[str, jsonpatch.Patch]:
        return self._history_step(client_id, self.undo, self.redo)

    def redo_step(self, client_id: str) -> tuple[str, jsonpatch.Patch]:
        return self._history_step(client_id, self.redo, self.undo)

    def history_info(self, client_id: str) -> dict[str, Any]:
        undo = self.undo.get(client_id) or []
        redo = self.redo.get(client_id) or []
        return {
            "undo": undo[-1].label if undo else None,
            "redo": redo[-1].label if redo else None,
        }

    # ------------------------------------------------------------------ clients

    def users(self) -> list[dict[str, Any]]:
        return [c.public() for c in self.clients.values()]

    async def broadcast(self, message: dict[str, Any], exclude: str | None = None) -> None:
        for client in list(self.clients.values()):
            if client.client_id != exclude:
                for queue in client.queues:
                    queue.put_nowait(message)

    # ------------------------------------------------------------------ persistence

    def write_to_disk(self, settings: Settings) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        doc = self.doc
        _atomic_write(self.root / "dictionary.json", _json_bytes(doc["dictionary"]))
        _atomic_write(self.root / "extras.json", _json_bytes(doc["extras"]))
        self.meta["updated"] = time.time()
        _atomic_write(self.root / "meta.json", _json_bytes(self.meta))
        self.dirty = False
        if time.time() - self.last_snapshot >= settings.snapshot_interval:
            self.snapshot(settings)

    def snapshot(self, settings: Settings) -> None:
        snap_dir = self.root / "snapshots"
        snap_dir.mkdir(exist_ok=True)
        stamp = time.strftime("%Y%m%d-%H%M%S")
        for name in ("dictionary.json", "extras.json"):
            src = self.root / name
            if src.exists():
                shutil.copy2(src, snap_dir / f"{stamp}_{name}")
        self.last_snapshot = time.time()
        files = sorted(snap_dir.glob("*_dictionary.json"))
        for old in files[: -settings.max_snapshots]:
            old.unlink(missing_ok=True)
            (snap_dir / old.name.replace("_dictionary.json", "_extras.json")).unlink(missing_ok=True)


class ProjectStore:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.projects: dict[str, Project] = {}
        self._load_lock = asyncio.Lock()
        self._bg: asyncio.Task | None = None
        self._view_index: dict[str, str] | None = None

    @property
    def root(self) -> Path:
        return self.settings.projects_dir

    def path(self, pid: str) -> Path:
        if not ID_RE.match(pid):
            raise KeyError(pid)
        return self.root / pid

    def exists(self, pid: str) -> bool:
        try:
            return pid in self.projects or (self.path(pid) / "dictionary.json").exists()
        except KeyError:
            return False

    def create(self, dictionary: BsddDictionary, extras: Extras | None = None, source: str = "new") -> Project:
        pid = new_project_id()
        now = time.time()
        meta = {
            "id": pid,
            "name": dictionary.DictionaryName or dictionary.DictionaryCode,
            "created": now,
            "updated": now,
            "last_access": now,
            "source": source,
        }
        project = Project(pid, self.path(pid), dictionary, extras or Extras(), meta)
        project.write_to_disk(self.settings)
        self.projects[pid] = project
        return project

    # ------------------------------------------------------------------ read-only links

    def _build_view_index(self) -> dict[str, str]:
        index: dict[str, str] = {}
        if self.root.exists():
            for meta_path in self.root.glob("*/meta.json"):
                try:
                    meta = json.loads(meta_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                view_id = (meta.get("access") or {}).get("view_id")
                if view_id:
                    index[view_id] = meta_path.parent.name
        for pid, project in self.projects.items():
            view_id = (project.meta.get("access") or {}).get("view_id")
            if view_id:
                index[view_id] = pid
        return index

    def resolve(self, ident: str) -> tuple[str, bool]:
        """Map a link id to ``(project id, via read-only link)``; raises KeyError if unknown."""
        if self.exists(ident):
            return ident, False
        if self._view_index is None:
            self._view_index = self._build_view_index()
        pid = self._view_index.get(ident)
        if pid is None or not self.exists(pid):
            raise KeyError(ident)
        return pid, True

    def update_view_id(self, pid: str, old: str | None, new: str | None) -> None:
        if self._view_index is None:
            self._view_index = self._build_view_index()
        if old:
            self._view_index.pop(old, None)
        if new:
            self._view_index[new] = pid

    async def get(self, pid: str) -> Project:
        if pid in self.projects:
            project = self.projects[pid]
            project.last_seen = time.time()
            return project
        async with self._load_lock:
            if pid in self.projects:
                return self.projects[pid]
            root = self.path(pid)
            if not (root / "dictionary.json").exists():
                raise KeyError(pid)
            project = await asyncio.to_thread(self._read, pid, root)
            self.projects[pid] = project
            return project

    def _read(self, pid: str, root: Path) -> Project:
        with (root / "dictionary.json").open(encoding="utf-8") as f:
            dictionary = BsddDictionary.model_validate(json.load(f))
        extras = Extras()
        if (root / "extras.json").exists():
            with (root / "extras.json").open(encoding="utf-8") as f:
                extras = Extras.model_validate(json.load(f))
        meta: dict[str, Any] = {"id": pid}
        if (root / "meta.json").exists():
            with (root / "meta.json").open(encoding="utf-8") as f:
                meta = json.load(f)
        meta["last_access"] = time.time()
        return Project(pid, root, dictionary, extras, meta)

    # ------------------------------------------------------------------ background work

    def schedule_save(self, project: Project) -> None:
        if project._save_task and not project._save_task.done():
            return

        async def _later() -> None:
            while True:
                await asyncio.sleep(self.settings.save_delay)
                if time.time() - project.last_change >= self.settings.save_delay:
                    break
            async with project.lock:
                if project.dirty:
                    await asyncio.to_thread(project.write_to_disk, self.settings)

        project._save_task = asyncio.create_task(_later())

    async def flush_all(self) -> None:
        for project in list(self.projects.values()):
            async with project.lock:
                if project.dirty:
                    await asyncio.to_thread(project.write_to_disk, self.settings)

    async def background_loop(self) -> None:
        """Unload idle projects and purge expired ones."""
        last_purge = 0.0
        while True:
            await asyncio.sleep(30)
            now = time.time()
            for pid, project in list(self.projects.items()):
                if project.clients or now - project.last_seen < self.settings.unload_after:
                    continue
                async with project.lock:
                    if project.dirty:
                        await asyncio.to_thread(project.write_to_disk, self.settings)
                    if not project.clients:
                        self.projects.pop(pid, None)
            if self.settings.project_ttl_days > 0 and now - last_purge > 3600:
                last_purge = now
                await asyncio.to_thread(self.purge_expired)

    def purge_expired(self) -> int:
        cutoff = time.time() - self.settings.project_ttl_days * 86400
        removed = 0
        if not self.root.exists():
            return 0
        for folder in self.root.iterdir():
            if not folder.is_dir() or folder.name in self.projects:
                continue
            meta_path = folder / "meta.json"
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
            except (OSError, json.JSONDecodeError):
                meta = {}
            last = max(float(meta.get("last_access") or 0), float(meta.get("updated") or 0), folder.stat().st_mtime)
            if last < cutoff:
                shutil.rmtree(folder, ignore_errors=True)
                removed += 1
        return removed

    def touch(self, project: Project) -> None:
        project.meta["last_access"] = time.time()
        project.last_seen = time.time()
