"""Link based access control: optional passwords and read-only links.

There are no user accounts. A project is reached through one of two links:

* the edit link ``/p/<project id>`` – full access, optionally protected by the *edit password*;
* the read-only link ``/v/<view id>`` – only if enabled; optionally protected by the *view
  password* (the edit password is accepted as well). The view id is unrelated to the project
  id, so a read-only link never reveals the edit link.

Passwords are stored as salted scrypt hashes in ``meta.json``. After a successful login the
client receives a signed token (HMAC with a server secret) bound to the project, the role and
the current access version. Changing any password or the read-only link bumps the version,
which invalidates every token issued before.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

Role = Literal["edit", "view"]

TOKEN_TTL = 60 * 60 * 24 * 90  # 90 days
SCRYPT = {"n": 2**14, "r": 8, "p": 1}
MIN_PASSWORD = 4


class AccessDenied(Exception):
    """Raised when a request lacks the required permission."""

    def __init__(self, reason: str, role: Role | None = None):
        super().__init__(reason)
        self.reason = reason  # "not_found" | "password_required" | "read_only" | "bad_password" | "rate_limited"
        self.role = role


# --------------------------------------------------------------------------- passwords


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, dklen=32, **SCRYPT)
    return "scrypt${n}${r}${p}${salt}${hash}".format(
        **SCRYPT, salt=base64.b64encode(salt).decode(), hash=base64.b64encode(digest).decode()
    )


def verify_password(password: str, stored: str | None) -> bool:
    if not stored:
        return False
    try:
        scheme, n, r, p, salt, digest = stored.split("$")
        if scheme != "scrypt":
            return False
        test = hashlib.scrypt(
            password.encode("utf-8"), salt=base64.b64decode(salt), dklen=32, n=int(n), r=int(r), p=int(p)
        )
        return hmac.compare_digest(test, base64.b64decode(digest))
    except (ValueError, TypeError):
        return False


# --------------------------------------------------------------------------- tokens


def load_secret(data_dir: Path) -> bytes:
    """Server secret for signing tokens: SECRET_KEY env var or ``<data>/secret.key`` (created once)."""
    env = os.environ.get("SECRET_KEY")
    if env:
        return env.encode("utf-8")
    path = data_dir / "secret.key"
    if path.exists():
        return path.read_bytes()
    data_dir.mkdir(parents=True, exist_ok=True)
    key = secrets.token_bytes(32)
    tmp = path.with_suffix(".tmp")
    tmp.write_bytes(key)
    os.chmod(tmp, 0o600)
    tmp.replace(path)
    return key


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def make_token(secret: bytes, pid: str, role: Role, version: int) -> str:
    payload = _b64(json.dumps({"p": pid, "r": role, "v": version, "t": int(time.time())}, separators=(",", ":")).encode())
    sig = _b64(hmac.new(secret, payload.encode(), hashlib.sha256).digest())
    return f"{payload}.{sig}"


def read_token(secret: bytes, token: str | None) -> dict[str, Any] | None:
    if not token or "." not in token:
        return None
    payload, sig = token.rsplit(".", 1)
    expected = _b64(hmac.new(secret, payload.encode(), hashlib.sha256).digest())
    if not hmac.compare_digest(sig, expected):
        return None
    try:
        data = json.loads(_unb64(payload))
    except (ValueError, json.JSONDecodeError):
        return None
    if time.time() - float(data.get("t", 0)) > TOKEN_TTL:
        return None
    return data


# --------------------------------------------------------------------------- per-project settings


def settings_of(meta: dict[str, Any]) -> dict[str, Any]:
    """The access block of a project's meta (created on demand)."""
    access = meta.setdefault("access", {})
    access.setdefault("edit_password", None)
    access.setdefault("view_password", None)
    access.setdefault("view_id", None)
    access.setdefault("version", 0)  # bumped when the edit password changes (signs out everybody)
    access.setdefault("view_version", 0)  # bumped when the read-only link or its password changes
    return access


def version_for(meta: dict[str, Any], role: Role) -> int:
    """Tokens of a role are valid as long as this number does not change."""
    a = settings_of(meta)
    return int(a["version"]) if role == "edit" else int(a["version"]) * 100000 + int(a["view_version"])


def public_settings(meta: dict[str, Any]) -> dict[str, Any]:
    a = settings_of(meta)
    return {
        "edit_protected": bool(a["edit_password"]),
        "view_enabled": bool(a["view_id"]),
        "view_id": a["view_id"],
        "view_protected": bool(a["view_password"]),
    }


def public_meta(meta: dict[str, Any], role: Role) -> dict[str, Any]:
    """Meta sent to clients. Read-only clients never learn the project id or its origin."""
    out = {k: v for k, v in meta.items() if k not in ("access", "id", "source")}
    out["protected"] = bool(settings_of(meta)["edit_password"]) if role == "edit" else bool(settings_of(meta)["view_password"])
    if role == "edit":
        out["id"] = meta.get("id")
    return out


@dataclass
class Grant:
    role: Role
    version: int


def check(meta: dict[str, Any], pid: str, via_view_link: bool, token: dict[str, Any] | None) -> Grant:
    """Decide what a request for ``pid`` (reached via edit or read-only link) may do."""
    a = settings_of(meta)

    def valid(role: Role) -> bool:
        return token is not None and token.get("p") == pid and token.get("r") == role and int(token.get("v", -1)) == version_for(meta, role)

    if via_view_link:
        if not a["view_id"]:
            raise AccessDenied("not_found")
        if a["view_password"] and not (valid("view") or valid("edit")):
            raise AccessDenied("password_required", "view")
        return Grant("view", version_for(meta, "view"))
    if a["edit_password"] and not valid("edit"):
        raise AccessDenied("password_required", "edit")
    return Grant("edit", version_for(meta, "edit"))


def login(meta: dict[str, Any], via_view_link: bool, password: str) -> Role:
    a = settings_of(meta)
    if via_view_link:
        if not a["view_id"]:
            raise AccessDenied("not_found")
        if verify_password(password, a["edit_password"]):
            return "view"  # the edit password also opens the read-only link (still read-only)
        if a["view_password"] and verify_password(password, a["view_password"]):
            return "view"
        if not a["view_password"]:
            return "view"
        raise AccessDenied("bad_password", "view")
    if not a["edit_password"]:
        return "edit"
    if verify_password(password, a["edit_password"]):
        return "edit"
    raise AccessDenied("bad_password", "edit")


def update(meta: dict[str, Any], changes: dict[str, Any]) -> None:
    """Apply settings changes (edit role required). Bumps the version if anything security relevant changed."""
    a = settings_of(meta)
    bump_edit = bump_view = False
    for key in ("edit_password", "view_password"):
        if key in changes:
            value = changes[key]
            if value is None or value == "":
                if not a[key]:
                    continue
                a[key] = None
            else:
                if not isinstance(value, str) or len(value) < MIN_PASSWORD:
                    raise ValueError(f"The password must have at least {MIN_PASSWORD} characters")
                a[key] = hash_password(value)
            if key == "edit_password":
                bump_edit = True
            else:
                bump_view = True
    if "view_enabled" in changes:
        if changes["view_enabled"] and not a["view_id"]:
            a["view_id"] = secrets.token_urlsafe(16)
            bump_view = True
        elif not changes["view_enabled"] and a["view_id"]:
            a["view_id"] = None
            a["view_password"] = None
            bump_view = True
    if changes.get("regenerate_view") and a["view_id"]:
        a["view_id"] = secrets.token_urlsafe(16)
        bump_view = True
    if bump_edit:
        a["version"] = int(a["version"]) + 1  # also invalidates read-only tokens (see version_for)
    if bump_view:
        a["view_version"] = int(a["view_version"]) + 1


class RateLimiter:
    """Simple sliding window limit for password attempts (per project and client address)."""

    def __init__(self, attempts: int = 10, window: float = 300.0):
        self.attempts = attempts
        self.window = window
        self.hits: dict[str, deque[float]] = defaultdict(deque)

    def hit(self, key: str) -> bool:
        now = time.time()
        q = self.hits[key]
        while q and now - q[0] > self.window:
            q.popleft()
        if len(q) >= self.attempts:
            return False
        q.append(now)
        return True
