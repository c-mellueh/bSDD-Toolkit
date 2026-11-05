"""FastAPI application: REST API, WebSocket collaboration and the static frontend."""

from __future__ import annotations

import asyncio
import contextlib
import io
import json
import logging
import random
import time
import zipfile
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

from bsdd_json import BsddDictionary
from bsdd_json.utils.cache import configure as configure_cache
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ValidationError

from . import __version__
from . import access as acc
from .config import Settings, settings as default_settings
from .ops import Extras, OpError, format_validation_error
from .services import download as download_service
from .services import ifc as ifc_service
from .store import ClientInfo, Project, ProjectStore, _atomic_write, _json_bytes

logger = logging.getLogger("bsdd_web")

COLORS = ["#e6194b", "#3cb44b", "#4363d8", "#f58231", "#911eb4", "#42d4f4", "#f032e6", "#469990", "#9a6324", "#800000"]


class CreateProjectBody(BaseModel):
    dictionary: dict[str, Any] | None = None
    extras: dict[str, Any] | None = None
    sloppy: bool = False
    header: dict[str, Any] | None = None


class ExportBody(BaseModel):
    specs: list[str] | None = None  # LOIN spec keys; None = whole dictionary
    settings: dict[str, Any] = {}
    lang: str = "en"


class AuthBody(BaseModel):
    password: str = ""


class AccessBody(BaseModel):
    edit_password: str | None = None
    view_password: str | None = None
    view_enabled: bool | None = None
    regenerate_view: bool = False
    #: names of password fields that should be removed (sent as null otherwise means "unchanged")
    remove: list[str] = []


class DownloadBody(BaseModel):
    uri: str


def default_dictionary(header: dict[str, Any] | None = None) -> BsddDictionary:
    data = {
        "OrganizationCode": "default",
        "DictionaryCode": "default",
        "DictionaryName": "New Dictionary",
        "DictionaryVersion": "0.0.1",
        "LanguageIsoCode": "en-GB",
        "LanguageOnly": False,
        "UseOwnUri": False,
        "Status": "Preview",
    }
    data.update({k: v for k, v in (header or {}).items() if v not in (None, "")})
    return BsddDictionary.model_validate(data)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or default_settings
    settings.projects_dir.mkdir(parents=True, exist_ok=True)
    configure_cache(cache_dir=settings.data_dir / "cache", offline=settings.offline)
    store = ProjectStore(settings)

    @contextlib.asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        task = asyncio.create_task(store.background_loop())
        try:
            yield
        finally:
            task.cancel()
            await store.flush_all()

    app = FastAPI(title="bSDD Toolkit", version=__version__, lifespan=lifespan)
    app.state.store = store
    app.state.settings = settings

    @app.exception_handler(HTTPException)
    async def http_error(_: Request, exc: HTTPException) -> JSONResponse:
        # structured errors (access control) are returned flat: {"detail", "reason", "role"}
        body = exc.detail if isinstance(exc.detail, dict) else {"detail": exc.detail}
        return JSONResponse(body, status_code=exc.status_code, headers=getattr(exc, "headers", None))

    secret = acc.load_secret(settings.data_dir)
    limiter = acc.RateLimiter()
    app.state.secret = secret

    async def open_link(ident: str, token: str | None) -> tuple[Project, acc.Grant, bool]:
        """Resolve an edit or read-only link id and check the caller's permission."""
        try:
            pid, via_view = store.resolve(ident)
            project = await store.get(pid)
        except KeyError as exc:
            raise acc.AccessDenied("not_found") from exc
        grant = acc.check(project.meta, project.id, via_view, acc.read_token(secret, token))
        return project, grant, via_view

    def _token(request: Request) -> str | None:
        return request.headers.get("x-project-token") or request.query_params.get("token")

    def _denied(exc: acc.AccessDenied) -> HTTPException:
        if exc.reason == "not_found":
            return HTTPException(404, "Project not found")
        if exc.reason == "read_only":
            return HTTPException(403, {"detail": "This link is read-only", "reason": "read_only"})
        if exc.reason == "rate_limited":
            return HTTPException(429, {"detail": "Too many attempts, try again later", "reason": "rate_limited"})
        if exc.reason == "bad_password":
            return HTTPException(401, {"detail": "Wrong password", "reason": "bad_password", "role": exc.role})
        return HTTPException(401, {"detail": "Password required", "reason": "password_required", "role": exc.role})

    async def project_for(ident: str, request: Request, *, edit: bool = False) -> tuple[Project, acc.Grant]:
        try:
            project, grant, _ = await open_link(ident, _token(request))
        except acc.AccessDenied as exc:
            raise _denied(exc) from exc
        if edit and grant.role != "edit":
            raise _denied(acc.AccessDenied("read_only"))
        return project, grant

    def _close_outdated(project: Project) -> None:
        """Disconnect websockets whose permission no longer matches the access settings."""
        for conn in list(project.connections):
            if conn["version"] != acc.version_for(project.meta, conn["role"]):
                conn["queue"].put_nowait({"type": "access_changed"})

    # ------------------------------------------------------------------ meta

    @app.get("/api/health")
    async def health() -> dict[str, Any]:
        return {"status": "ok", "version": __version__, "open_projects": len(store.projects)}

    @app.get("/api/config")
    async def config() -> dict[str, Any]:
        return {"version": __version__, "max_upload_mb": settings.max_upload_mb, "offline": settings.offline}

    # ------------------------------------------------------------------ projects

    @app.post("/api/projects")
    async def create_project(request: Request) -> JSONResponse:
        length = int(request.headers.get("content-length") or 0)
        if length > settings.max_upload_mb * 1024 * 1024:
            raise HTTPException(413, f"File too large (max {settings.max_upload_mb} MB)")
        raw = await request.body()
        if len(raw) > settings.max_upload_mb * 1024 * 1024:
            raise HTTPException(413, f"File too large (max {settings.max_upload_mb} MB)")
        try:
            body = CreateProjectBody.model_validate_json(raw or b"{}")
        except ValidationError as exc:
            raise HTTPException(400, format_validation_error(exc)) from exc
        try:
            if body.dictionary is not None:
                dictionary = await asyncio.to_thread(BsddDictionary.from_data, body.dictionary, sloppy=body.sloppy)
                source = "upload"
            else:
                dictionary = default_dictionary(body.header)
                source = "new"
            extras = Extras.model_validate(body.extras or {})
        except ValidationError as exc:
            return JSONResponse(
                {"detail": format_validation_error(exc), "can_sloppy": not body.sloppy, "error_count": exc.error_count()},
                status_code=422,
            )
        project = await asyncio.to_thread(store.create, dictionary, extras, source)
        return JSONResponse({"id": project.id, "meta": project.meta}, status_code=201)

    @app.get("/api/projects/{pid}")
    async def project_info(pid: str, request: Request) -> dict[str, Any]:
        project, grant = await project_for(pid, request)
        return {"meta": acc.public_meta(project.meta, grant.role), "role": grant.role, "version": project.version, "users": project.users()}

    # ------------------------------------------------------------------ access (passwords, read-only link)

    @app.post("/api/projects/{pid}/auth")
    async def authenticate(pid: str, body: AuthBody, request: Request) -> dict[str, Any]:
        """Exchange a password for an access token for this link."""
        try:
            real, via_view = store.resolve(pid)
            project = await store.get(real)
        except KeyError as exc:
            raise HTTPException(404, "Project not found") from exc
        host = request.client.host if request.client else "?"
        if not limiter.hit(f"{real}|{host}"):
            raise _denied(acc.AccessDenied("rate_limited"))
        try:
            role = acc.login(project.meta, via_view, body.password)
        except acc.AccessDenied as exc:
            raise _denied(exc) from exc
        return {"token": acc.make_token(secret, project.id, role, acc.version_for(project.meta, role)), "role": role}

    @app.get("/api/projects/{pid}/access")
    async def get_access(pid: str, request: Request) -> dict[str, Any]:
        project, _ = await project_for(pid, request, edit=True)
        return acc.public_settings(project.meta)

    @app.post("/api/projects/{pid}/access")
    async def set_access(pid: str, body: AccessBody, request: Request) -> dict[str, Any]:
        project, _ = await project_for(pid, request, edit=True)
        changes: dict[str, Any] = {}
        for key in ("edit_password", "view_password"):
            if key in body.remove:
                changes[key] = None
            elif getattr(body, key):
                changes[key] = getattr(body, key)
        if body.view_enabled is not None:
            changes["view_enabled"] = body.view_enabled
        if body.regenerate_view:
            changes["regenerate_view"] = True
        old_view = acc.settings_of(project.meta)["view_id"]
        try:
            acc.update(project.meta, changes)
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc
        new_view = acc.settings_of(project.meta)["view_id"]
        if new_view != old_view:
            store.update_view_id(project.id, old_view, new_view)
        await asyncio.to_thread(_write_meta, project)
        _close_outdated(project)
        # the caller keeps access with a fresh token
        return {**acc.public_settings(project.meta), "token": acc.make_token(secret, project.id, "edit", acc.version_for(project.meta, "edit"))}

    @app.get("/api/projects/{pid}/dictionary.json")
    async def download_json(pid: str, request: Request) -> Response:
        project, _ = await project_for(pid, request)
        data = json.dumps(project.doc["dictionary"], ensure_ascii=False, indent=2).encode("utf-8")
        d = project.dictionary
        name = f"{d.DictionaryCode}_{d.DictionaryVersion}.json"
        return Response(data, media_type="application/json", headers=_disposition(name))

    @app.get("/api/projects/{pid}/project.json")
    async def download_project(pid: str, request: Request) -> Response:
        """Dictionary plus editor data (LOIN etc.) to move a project to another server."""
        project, _ = await project_for(pid, request)
        data = json.dumps(project.doc, ensure_ascii=False).encode("utf-8")
        d = project.dictionary
        return Response(data, media_type="application/json", headers=_disposition(f"{d.DictionaryCode}_{d.DictionaryVersion}.project.json"))

    @app.post("/api/projects/{pid}/duplicate")
    async def duplicate(pid: str, request: Request) -> dict[str, Any]:
        project, _ = await project_for(pid, request, edit=True)
        async with project.lock:
            doc = json.loads(json.dumps(project.doc))
        dictionary = BsddDictionary.model_validate(doc["dictionary"])
        new = await asyncio.to_thread(store.create, dictionary, Extras.model_validate(doc["extras"]), f"copy:{pid}")
        # the copy keeps the edit password (but gets no read-only link)
        edit_hash = acc.settings_of(project.meta)["edit_password"]
        if edit_hash:
            acc.settings_of(new.meta)["edit_password"] = edit_hash
            await asyncio.to_thread(_write_meta, new)
        token = acc.make_token(secret, new.id, "edit", acc.version_for(new.meta, "edit"))
        return {"id": new.id, "token": token}

    # ------------------------------------------------------------------ exports

    @app.post("/api/projects/{pid}/export/{kind}")
    async def export(pid: str, kind: str, body: ExportBody, request: Request) -> Response:
        from .services import excel, ids, iso23386, revit
        from .services.loin import build_loin_xml, selection_from_state

        project, _ = await project_for(pid, request)
        async with project.lock:
            doc = project.doc
            d = BsddDictionary.model_validate(doc["dictionary"])
            loin_state = json.loads(json.dumps(doc["extras"].get("loin") or {}))
        selection = selection_from_state(loin_state, body.specs)
        base = f"{d.DictionaryCode}_{d.DictionaryVersion}"
        s = body.settings or {}
        try:
            if kind == "excel":
                data, count = await asyncio.to_thread(excel.export_excel, d, selection, body.lang)
                return _file(data, f"{base}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", count)
            if kind == "ids":
                data, count = await asyncio.to_thread(ids.export_ids, d, selection, s.get("settings"), s.get("metadata"))
                return _file(data, f"{base}.ids", "application/xml", count)
            if kind == "iso23386":
                data, count = await asyncio.to_thread(iso23386.export_iso23386, d, selection)
                return _file(data, f"{base}_ISO23386.xml", "application/xml", count)
            if kind == "iso7817":
                data, count = await asyncio.to_thread(build_loin_xml, loin_state, d, body.specs)
                return _file(data, f"{base}_LOIN.xml", "application/xml", count)
            if kind == "revit-psets":
                data, count = await asyncio.to_thread(revit.export_custom_psets, d, selection, s.get("text_or_label", "Text"))
                return _file(data, f"{base}_PropertySets.txt", "text/plain; charset=utf-8", count)
            if kind == "revit-shared":
                data, count = await asyncio.to_thread(revit.export_shared_parameters, d, selection, s.get("group_name"))
                return _file(data, f"{base}_SharedParameters.txt", "text/plain; charset=utf-16", count)
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc
        raise HTTPException(404, f"Unknown export '{kind}'")

    @app.post("/api/projects/{pid}/ids/candidates")
    async def ids_candidates(pid: str, body: ExportBody, request: Request) -> dict[str, Any]:
        from .services.ids import DEFAULT_SETTINGS, default_metadata, main_property_candidates
        from .services.loin import selection_from_state

        project, _ = await project_for(pid, request)
        async with project.lock:
            d = BsddDictionary.model_validate(project.doc["dictionary"])
            loin_state = json.loads(json.dumps(project.doc["extras"].get("loin") or {}))
        selection = selection_from_state(loin_state, body.specs)
        candidates = await asyncio.to_thread(main_property_candidates, d, selection)
        return {"candidates": candidates, "default_settings": DEFAULT_SETTINGS, "default_metadata": default_metadata(d)}

    # ------------------------------------------------------------------ bSDD download

    @app.get("/api/bsdd/dictionaries")
    async def bsdd_dictionaries() -> dict[str, Any]:
        cache = app.state.__dict__.setdefault("bsdd_cache", {})
        if cache.get("time", 0) > time.time() - 3600:
            return {"dictionaries": cache["data"]}
        try:
            data = await asyncio.to_thread(download_service.list_dictionaries)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(502, f"bSDD is not reachable: {exc}") from exc
        cache.update(time=time.time(), data=data)
        return {"dictionaries": data}

    @app.post("/api/download")
    async def start_download(body: DownloadBody) -> dict[str, Any]:
        def on_done(dictionary: BsddDictionary) -> str:
            return store.create(dictionary, None, f"bsdd:{body.uri}").id

        job = download_service.jobs.start(body.uri, on_done)
        return job.to_json()

    @app.get("/api/download/{job_id}")
    async def download_status(job_id: str) -> dict[str, Any]:
        job = download_service.jobs.get(job_id)
        if job is None:
            raise HTTPException(404, "Job not found")
        return job.to_json()

    @app.delete("/api/download/{job_id}")
    async def cancel_download(job_id: str) -> dict[str, Any]:
        job = download_service.jobs.get(job_id)
        if job is None:
            raise HTTPException(404, "Job not found")
        job.cancelled = True
        return job.to_json()

    # ------------------------------------------------------------------ static data

    @app.get("/api/ifc/classes")
    async def ifc_classes() -> Response:
        return JSONResponse(ifc_service.ifc_classes(), headers={"Cache-Control": "public, max-age=86400"})

    @app.get("/api/resources/{name}")
    async def resources(name: str) -> Response:
        files = {
            "units": "units_v1.json",
            "countries": "countries_v1.json",
            "languages": "language_iso_v1.json",
            "reference-documents": "refrence_document_v1.json",
        }
        if name not in files:
            raise HTTPException(404)
        return JSONResponse(ifc_service.resource_json(files[name]), headers={"Cache-Control": "public, max-age=86400"})

    @app.get("/api/shell/bsdd_json.zip")
    async def shell_package() -> Response:
        """The pure-Python bsdd_json package for the in-browser (Pyodide) shell."""
        cached = app.state.__dict__.get("shell_zip")
        if cached is None:
            cached = _zip_package()
            app.state.shell_zip = cached
        return Response(cached, media_type="application/zip", headers={"Cache-Control": "no-cache"})

    # ------------------------------------------------------------------ websocket

    @app.websocket("/api/projects/{pid}/ws")
    async def project_ws(ws: WebSocket, pid: str) -> None:
        await ws.accept()
        try:
            project, grant, _ = await open_link(pid, ws.query_params.get("token"))
        except acc.AccessDenied as exc:
            if exc.reason == "not_found":
                await ws.send_json({"type": "error", "error": "Project not found", "fatal": True})
            else:
                await ws.send_json({"type": "error", "error": exc.reason, "role": exc.role, "fatal": True, "auth": True})
            await ws.close()
            return
        client_id = (ws.query_params.get("client") or "")[:64] or f"anon-{random.randint(0, 1_000_000)}"
        name = (ws.query_params.get("name") or "Anonymous")[:40]
        client = project.clients.get(client_id)
        if client is None:
            used = {c.color for c in project.clients.values()}
            color = next((c for c in COLORS if c not in used), random.choice(COLORS))
            client = ClientInfo(client_id, name, color, role=grant.role)
            project.clients[client_id] = client
        else:
            client.name = name
            client.role = grant.role
        queue: asyncio.Queue = asyncio.Queue()
        client.queues.append(queue)
        conn = {"queue": queue, "role": grant.role, "version": grant.version}
        project.connections.append(conn)
        store.touch(project)
        await asyncio.to_thread(_write_meta, project)

        async with project.lock:
            queue.put_nowait(
                {
                    "type": "hello",
                    "version": project.version,
                    "doc": project.doc,
                    "meta": acc.public_meta(project.meta, grant.role),
                    "role": grant.role,
                    "you": client.public(),
                    "users": project.users(),
                    "history": project.history_info(client_id),
                },
            )
        await project.broadcast({"type": "users", "users": project.users()})

        async def sender() -> None:
            while True:
                msg = await queue.get()
                await ws.send_json(msg)
                if msg.get("type") == "access_changed":
                    # permissions changed: the client reconnects and is checked again
                    await ws.close(code=4001)
                    return

        send_task = asyncio.create_task(sender())
        try:
            while True:
                msg = await ws.receive_json()
                await handle_message(project, client_id, msg, queue.put_nowait, conn)
        except WebSocketDisconnect:
            pass
        except Exception:  # noqa: BLE001
            logger.exception("WebSocket error")
        finally:
            send_task.cancel()
            if conn in project.connections:
                project.connections.remove(conn)
            if queue in client.queues:
                client.queues.remove(queue)
            if not client.queues:
                project.clients.pop(client_id, None)
                await project.broadcast({"type": "users", "users": project.users()})
            project.last_seen = time.time()

    async def handle_message(project: Project, client_id: str, msg: dict[str, Any], reply, conn: dict[str, Any] | None = None) -> None:
        kind = msg.get("type")
        rid = msg.get("rid")
        if kind == "ping":
            reply({"type": "pong", "rid": rid})
            return
        if kind == "sync":
            async with project.lock:
                reply({"type": "doc", "version": project.version, "doc": project.doc})
            return
        if kind == "presence":
            client = project.clients.get(client_id)
            if client:
                if isinstance(msg.get("selection"), dict):
                    client.selection = msg["selection"]
                if isinstance(msg.get("name"), str) and msg["name"].strip():
                    client.name = msg["name"].strip()[:40]
            await project.broadcast({"type": "users", "users": project.users()})
            return
        if kind not in ("op", "undo", "redo"):
            reply({"type": "ack", "rid": rid, "ok": False, "error": f"Unknown message '{kind}'"})
            return
        if conn is not None:
            if conn["role"] != "edit":
                reply({"type": "ack", "rid": rid, "ok": False, "error": "This link is read-only"})
                return
            if conn["version"] != acc.version_for(project.meta, conn["role"]):
                reply({"type": "ack", "rid": rid, "ok": False, "error": "Access settings changed, please reconnect"})
                return
        async with project.lock:
            try:
                if kind == "op":
                    result, patch = await asyncio.to_thread(project.apply_op, client_id, msg.get("op", ""), msg.get("args") or {})
                    label = msg.get("op")
                elif kind == "undo":
                    label, patch = await asyncio.to_thread(project.undo_step, client_id)
                    result = label
                else:
                    label, patch = await asyncio.to_thread(project.redo_step, client_id)
                    result = label
            except OpError as exc:
                reply({"type": "ack", "rid": rid, "ok": False, "error": str(exc), "history": project.history_info(client_id)})
                return
            if patch:
                await project.broadcast({"type": "patch", "version": project.version, "patch": patch, "author": client_id, "label": label})
                store.schedule_save(project)
            reply({"type": "ack", "rid": rid, "ok": True, "result": result, "version": project.version, "history": project.history_info(client_id)})

    # ------------------------------------------------------------------ frontend

    static_dir = settings.static_dir
    if (static_dir / "index.html").exists():
        if (static_dir / "assets").exists():
            app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")

        @app.get("/{path:path}", include_in_schema=False)
        async def spa(path: str) -> Response:
            if path.startswith("api/"):
                raise HTTPException(404)
            candidate = (static_dir / path).resolve()
            if path and candidate.is_file() and static_dir.resolve() in candidate.parents:
                return FileResponse(candidate)
            return FileResponse(static_dir / "index.html", headers={"Cache-Control": "no-cache"})

    return app


def _write_meta(project: Project) -> None:
    if project.root.exists():
        _atomic_write(project.root / "meta.json", _json_bytes(project.meta))


def _disposition(filename: str) -> dict[str, str]:
    from urllib.parse import quote

    safe = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in filename)
    return {"Content-Disposition": f"attachment; filename=\"{safe}\"; filename*=UTF-8''{quote(filename)}"}


def _file(data: bytes, filename: str, media_type: str, count: int) -> Response:
    headers = _disposition(filename)
    headers["X-Export-Count"] = str(count)
    headers["Access-Control-Expose-Headers"] = "X-Export-Count, Content-Disposition"
    return Response(data, media_type=media_type, headers=headers)


def _zip_package() -> bytes:
    import bsdd_json

    root = Path(bsdd_json.__file__).resolve().parent
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in root.rglob("*.py"):
            rel = path.relative_to(root)
            if rel.parts[0] == "tests":
                continue
            zf.write(path, Path("bsdd_json") / rel)
        # pure-Python JSON patch helpers: the shell diffs its copy and sends only the changes
        zf.write(Path(__file__).resolve().parent / "jsonpatch.py", "bsdd_shell_jsonpatch.py")
    return buf.getvalue()


app = create_app()
