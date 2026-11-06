"""Download complete dictionaries from the buildingSMART bSDD API (background jobs)."""

from __future__ import annotations

import logging
import threading
import time
import uuid
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any

from bsdd_json import BsddDictionary
from bsdd_json.utils import class_utils
from bsdd_json.utils import dictionary_utils as dict_utils
from bsdd_json.utils import property_utils as prop_utils

logger = logging.getLogger(__name__)
_RENAME = {
    "organizationCodeOwner": "OrganizationCode",
    "code": "DictionaryCode",
    "version": "DictionaryVersion",
    "defaultLanguageCode": "LanguageIsoCode",
    "name": "DictionaryName",
    "changeRequestEmail": "ChangeRequestEmailAddress",
}


def _client():
    import bsdd

    return bsdd.Client()


def list_dictionaries() -> list[dict[str, Any]]:
    result = _client().get_dictionary("") or {}
    out = []
    for d in result.get("dictionaries", []) or []:
        out.append(
            {
                "uri": d.get("uri"),
                "name": d.get("name"),
                "version": d.get("version"),
                "organization": d.get("organizationNameOwner") or d.get("organizationCodeOwner"),
                "status": d.get("status"),
                "language": d.get("defaultLanguageCode"),
            },
        )
    return out


class FullDownloadError(Exception):
    """The complete-dictionary download failed; ``status`` is the HTTP status for our API."""

    def __init__(self, message: str, status: int = 502):
        super().__init__(message)
        self.status = status


def fetch_full(api: str, uri: str, token: str, timeout: float = 120) -> dict[str, Any]:
    """Download a complete dictionary as one bSDD JSON file (needs a buildingSMART sign-in).

    Uses ``/api/DictionaryDownload/bsdd/v1`` with the user's access token. The token is only
    passed on to buildingSMART, never stored or logged.
    """
    import io
    import json
    import urllib.error
    import urllib.parse
    import urllib.request
    import zipfile

    url = f"{api}/api/DictionaryDownload/bsdd/v1?" + urllib.parse.urlencode({"DictionaryUri": uri})
    request = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/octet-stream", "User-Agent": "bSDD-Toolkit"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = response.status
            body = response.read()
    except urllib.error.HTTPError as exc:
        if exc.code == 401:
            raise FullDownloadError("The buildingSMART sign-in has expired. Please sign in again.", 401) from exc
        if exc.code == 404:
            raise FullDownloadError(f"No dictionary found under '{uri}'", 404) from exc
        raise FullDownloadError(f"bSDD download failed ({exc.code})") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise FullDownloadError(f"bSDD is not reachable: {exc}") from exc
    if status == 204 or not body:
        raise FullDownloadError("bSDD returned no data for this dictionary")
    if body[:2] == b"PK":  # zipped export: take the JSON file inside
        with zipfile.ZipFile(io.BytesIO(body)) as archive:
            name = next((n for n in archive.namelist() if n.lower().endswith(".json")), None)
            if name is None:
                raise FullDownloadError("The downloaded archive contains no JSON file")
            body = archive.read(name)
    try:
        data = json.loads(body.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FullDownloadError("bSDD returned an unreadable file") from exc
    if not isinstance(data, dict):
        raise FullDownloadError("bSDD returned an unexpected file")
    return data


def fetch_header(client, uri: str) -> BsddDictionary:
    result = (client.get_dictionary(uri) or {}).get("dictionaries") or []
    if not result:
        raise ValueError(f"No dictionary found under '{uri}'")
    data = dict(result[0])
    data.pop("availableLanguages", None)
    for old, new in _RENAME.items():
        if old in data:
            data[new] = data.pop(old)
    data["LanguageOnly"] = False
    data["UseOwnUri"] = False
    return BsddDictionary.model_validate(data)


@dataclass
class Job:
    uri: str
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    status: str = "running"  # running | done | error | cancelled
    message: str = "Started"
    classes_done: int = 0
    classes_total: int = 0
    properties_done: int = 0
    properties_total: int = 0
    project_id: str | None = None
    error: str | None = None
    created: float = field(default_factory=time.time)
    cancelled: bool = False

    def to_json(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "uri": self.uri,
            "status": self.status,
            "message": self.message,
            "classes_done": self.classes_done,
            "classes_total": self.classes_total,
            "properties_done": self.properties_done,
            "properties_total": self.properties_total,
            "project_id": self.project_id,
            "error": self.error,
        }


def _paged(fetch: Callable[[int], dict], items_key: str, count_key: str, total_key: str, job: Job) -> list[dict]:
    items: list[dict] = []
    offset, total = 0, None
    while (total is None or offset < total) and not job.cancelled:
        page = fetch(offset) or {}
        batch = page.get(items_key) or []
        items.extend(batch)
        count = page.get(count_key) or len(batch)
        total = page.get(total_key) or 0
        if count == 0:
            break
        offset += count
    return items


def run_download(job: Job, on_done: Callable[[BsddDictionary], str], workers: int = 8) -> None:
    """Download everything for ``job.uri``; ``on_done`` stores the result and returns a project id."""
    try:
        uri = job.uri.strip()
        if not dict_utils.is_uri(uri):
            raise ValueError("Please enter a valid dictionary URI")
        client = _client()
        job.message = "Loading dictionary"
        dictionary = fetch_header(client, uri)

        job.message = "Listing classes and properties"
        class_infos = _paged(
            lambda o: client.get_classes(uri, use_nested_classes=False, limit=1000, offset=o),
            "classes",
            "classesCount",
            "classesTotalCount",
            job,
        )
        prop_infos = _paged(
            lambda o: client.get_properties(uri, limit=1000, offset=o),
            "properties",
            "propertiesCount",
            "propertiesTotalCount",
            job,
        )
        job.classes_total = len(class_infos)
        job.properties_total = len(prop_infos)
        job.message = "Downloading"

        classes: dict[int, Any] = {}
        properties: dict[int, Any] = {}

        def load_class(i: int, info: dict):
            return "c", i, class_utils.load_class(info["uri"], dictionary, True, True, _client())

        def load_prop(i: int, info: dict):
            return "p", i, prop_utils.load_property(info["uri"], client=_client())

        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(load_class, i, info) for i, info in enumerate(class_infos)]
            futures += [pool.submit(load_prop, i, info) for i, info in enumerate(prop_infos)]
            for fut in as_completed(futures):
                if job.cancelled:
                    for f in futures:
                        f.cancel()
                    break
                try:
                    kind, i, result = fut.result()
                except Exception as exc:  # noqa: BLE001 - skip broken entries, keep going
                    logger.warning("Download of an item failed: %s", exc)
                    continue
                if kind == "c":
                    job.classes_done += 1
                    if result is not None:
                        classes[i] = result
                else:
                    job.properties_done += 1
                    if result is not None:
                        properties[i] = result
        if job.cancelled:
            job.status = "cancelled"
            job.message = "Cancelled"
            return
        dictionary.Classes = [classes[i] for i in sorted(classes)]
        dictionary.Properties = [properties[i] for i in sorted(properties)]
        dictionary.model_post_init(None)
        job.message = "Saving"
        job.project_id = on_done(dictionary)
        job.status = "done"
        job.message = "Done"
    except Exception as exc:  # noqa: BLE001 - reported to the user
        logger.exception("Download failed")
        job.status = "error"
        job.error = str(exc)
        job.message = "Failed"


class JobManager:
    def __init__(self) -> None:
        self.jobs: dict[str, Job] = {}
        self.lock = threading.Lock()

    def start(self, uri: str, on_done: Callable[[BsddDictionary], str]) -> Job:
        job = Job(uri=uri)
        with self.lock:
            # forget old finished jobs
            cutoff = time.time() - 3600
            self.jobs = {k: v for k, v in self.jobs.items() if v.status == "running" or v.created > cutoff}
            self.jobs[job.id] = job
        threading.Thread(target=run_download, args=(job, on_done), daemon=True).start()
        return job

    def get(self, job_id: str) -> Job | None:
        return self.jobs.get(job_id)


jobs = JobManager()
