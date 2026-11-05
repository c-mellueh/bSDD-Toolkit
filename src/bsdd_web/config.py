from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default


@dataclass
class Settings:
    data_dir: Path = field(default_factory=lambda: Path(os.environ.get("DATA_DIR", "./data")))
    max_upload_mb: int = field(default_factory=lambda: _int_env("MAX_UPLOAD_MB", 50))
    #: delete projects not opened for this many days (0 = never)
    project_ttl_days: int = field(default_factory=lambda: _int_env("PROJECT_TTL_DAYS", 0))
    #: seconds of inactivity before an edited project is written to disk
    save_delay: float = field(default_factory=lambda: float(os.environ.get("SAVE_DELAY", "2")))
    #: keep a snapshot every N seconds while editing
    snapshot_interval: int = field(default_factory=lambda: _int_env("SNAPSHOT_INTERVAL", 600))
    max_snapshots: int = field(default_factory=lambda: _int_env("MAX_SNAPSHOTS", 20))
    #: unload projects from memory after N seconds without connected clients
    unload_after: int = field(default_factory=lambda: _int_env("UNLOAD_AFTER", 600))
    #: disable remote bSDD lookups (external class/property resolution)
    offline: bool = field(default_factory=lambda: os.environ.get("OFFLINE", "0") in ("1", "true"))
    static_dir: Path = field(
        default_factory=lambda: Path(
            os.environ.get("STATIC_DIR", str(Path(__file__).parent / "static")),
        ),
    )

    @property
    def projects_dir(self) -> Path:
        return self.data_dir / "projects"


settings = Settings()
