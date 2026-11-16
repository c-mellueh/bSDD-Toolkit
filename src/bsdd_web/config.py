from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _text_env(name: str) -> str:
    """Text from the environment; ``\\n`` in the value starts a new line (for compose files)."""
    return os.environ.get(name, "").replace("\\n", "\n").strip()


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
    #: public address of this installation, e.g. https://bsdd.example.org (used for the
    #: buildingSMART sign-in return address); empty = the address the browser uses
    public_url: str = field(default_factory=lambda: os.environ.get("PUBLIC_URL", "").strip().rstrip("/"))
    #: client ID registered with buildingSMART for "Sign in with buildingSMART" (single-page
    #: application); empty = sign-in and the full download are switched off
    bsdd_client_id: str = field(default_factory=lambda: os.environ.get("BSDD_CLIENT_ID", "").strip())
    bsdd_authority: str = field(
        default_factory=lambda: os.environ.get(
            "BSDD_AUTHORITY",
            "https://authentication.buildingsmart.org/buildingsmartservices.onmicrosoft.com/b2c_1a_signupsignin_c",
        ).rstrip("/"),
    )
    bsdd_scope: str = field(
        default_factory=lambda: os.environ.get("BSDD_SCOPE", "https://buildingSMARTservices.onmicrosoft.com/bsddapi/read"),
    )
    bsdd_api: str = field(default_factory=lambda: os.environ.get("BSDD_API", "https://api.bsdd.buildingsmart.org").rstrip("/"))
    #: operator of this installation, shown in the imprint and the privacy policy
    #: (empty name = the pages say that the operator has not entered the details yet)
    operator_name: str = field(default_factory=lambda: _text_env("OPERATOR_NAME"))
    operator_address: str = field(default_factory=lambda: _text_env("OPERATOR_ADDRESS"))
    operator_email: str = field(default_factory=lambda: _text_env("OPERATOR_EMAIL"))
    operator_phone: str = field(default_factory=lambda: _text_env("OPERATOR_PHONE"))
    #: additional text for the imprint (e.g. VAT ID, person responsible for the content)
    imprint_extra: str = field(default_factory=lambda: _text_env("IMPRINT_EXTRA"))
    #: additional text for the privacy policy (e.g. hosting provider, CDN or proxy in front)
    privacy_extra: str = field(default_factory=lambda: _text_env("PRIVACY_EXTRA"))
    static_dir: Path = field(
        default_factory=lambda: Path(
            os.environ.get("STATIC_DIR", str(Path(__file__).parent / "static")),
        ),
    )

    def legal(self) -> dict[str, object]:
        """Operator details and facts for the imprint and the privacy policy (all public)."""
        return {
            "name": self.operator_name,
            "address": self.operator_address,
            "email": self.operator_email,
            "phone": self.operator_phone,
            "imprint_extra": self.imprint_extra,
            "privacy_extra": self.privacy_extra,
            "project_ttl_days": self.project_ttl_days,
            "max_snapshots": self.max_snapshots,
            "bsdd_login": bool(self.bsdd_client_id),
            "offline": self.offline,
        }

    @property
    def projects_dir(self) -> Path:
        return self.data_dir / "projects"

    @property
    def bsdd_redirect_uri(self) -> str | None:
        """Return address after the buildingSMART sign-in (ASCII form of the domain)."""
        if not self.public_url:
            return None
        scheme, sep, rest = self.public_url.partition("://")
        host, slash, path = rest.partition("/")
        try:
            host = host.encode("idna").decode("ascii")
        except UnicodeError:
            pass
        base = f"{scheme}{sep}{host}{slash}{path}".rstrip("/")
        return f"{base}/auth/bsdd/callback"


settings = Settings()
