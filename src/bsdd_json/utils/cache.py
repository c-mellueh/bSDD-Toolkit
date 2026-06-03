from __future__ import annotations

import json
import logging
from collections.abc import Callable
from pathlib import Path
from typing import ClassVar, TypeVar

from pydantic import BaseModel

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class BaseCache:
    """In-memory cache of external bSDD resources backed by an appdata JSON file.

    Subclasses set :attr:`cache_filename`, :attr:`model_cls` and :attr:`label`.
    The on-disk cache is loaded once on first access, updated whenever a new
    resource is resolved, and deleted only when :meth:`flush_data` is called.
    Each subclass gets its own ``data`` dict and ``_loaded`` flag.
    """

    cache_filename: ClassVar[str]
    model_cls: ClassVar[type[BaseModel]]
    label: ClassVar[str]

    data: ClassVar[dict[str, BaseModel | None]]
    _loaded: ClassVar[bool]

    def __init_subclass__(cls, **kwargs) -> None:
        """Give every subclass its own ``data`` dict and ``_loaded`` flag."""
        super().__init_subclass__(**kwargs)
        cls.data = {}
        cls._loaded = False

    @classmethod
    def _get_cache_path(cls) -> Path | None:
        """Path of the on-disk cache in appdata, or ``None`` if unavailable.

        Resolved lazily via the GUI's ``Appdata`` tool so that ``bsdd_json``
        keeps working standalone (e.g. in tests) where ``bsdd_gui`` may be
        missing; in that case disk caching is silently skipped.
        """
        try:
            from bsdd_gui import tool

            return Path(tool.Appdata.get_appdata_folder()) / cls.cache_filename
        except Exception:  # noqa: BLE001 - any import/runtime issue just disables disk cache
            return None

    @classmethod
    def _load_cache(cls) -> None:
        if cls._loaded:
            return
        cls._loaded = True
        path = cls._get_cache_path()
        if not path or not path.exists():
            return
        try:
            with path.open(encoding="utf-8") as f:
                raw = json.load(f)
        except (OSError, json.JSONDecodeError):
            logger.warning("Failed to read external %s cache at %s", cls.label, path)
            return
        for uri, value in raw.items():
            cls.data[uri] = cls._validate_cached(uri, value)

    @classmethod
    def _validate_cached(cls, uri: str, value) -> BaseModel | None:
        try:
            return cls.model_cls.model_validate(value)
        except Exception:  # noqa: BLE001 - skip individual corrupt entries
            logger.warning("Failed to load cached %s %s", cls.label, uri)
            return None

    @classmethod
    def _save_cache(cls) -> None:
        path = cls._get_cache_path()
        if not path:
            return
        # Persist only successfully resolved resources; ``None`` results (e.g.
        # offline / not found) stay in memory but must not poison the cache.
        serializable = {uri: obj.model_dump(mode="json", exclude_none=True) for uri, obj in cls.data.items() if obj is not None}
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8") as f:
                json.dump(serializable, f)
        except OSError:
            logger.warning("Failed to write external %s cache at %s", cls.label, path)

    @classmethod
    def _get(cls, key: str, loader: Callable[[], T | None]) -> T | None:
        """Return the cached resource for ``key``, loading it via ``loader`` on a miss."""
        if not key:
            return None
        cls._load_cache()
        if key in cls.data:
            return cls.data[key]
        result = loader()
        cls.data[key] = result
        if result is not None:
            cls._save_cache()
        return cls.data[key]

    @classmethod
    def flush_data(cls) -> None:
        cls.data = {}
        cls._loaded = False
        path = cls._get_cache_path()
        if path and path.exists():
            try:
                path.unlink()
            except OSError:
                logger.warning("Failed to delete external %s cache at %s", cls.label, path)
