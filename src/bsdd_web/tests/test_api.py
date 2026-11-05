from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from bsdd_web import jsonpatch
from bsdd_web.app import create_app
from bsdd_web.config import Settings

from .conftest import sample_data


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    s = Settings()
    s.data_dir = tmp_path
    s.save_delay = 0.05
    s.offline = True
    s.static_dir = tmp_path / "nostatic"
    return s


@pytest.fixture
def client(settings):
    with TestClient(create_app(settings)) as c:
        yield c


def create(client, data=None, **kw):
    r = client.post("/api/projects", json={"dictionary": data if data is not None else sample_data(), **kw})
    assert r.status_code == 201, r.text
    return r.json()["id"]


def connect(client, pid, cid, name="User"):
    ws = client.websocket_connect(f"/api/projects/{pid}/ws?client={cid}&name={name}")
    session = ws.__enter__()
    hello = session.receive_json()
    assert hello["type"] == "hello"
    return ws, session, hello


def recv_until(session, kind):
    while True:
        msg = session.receive_json()
        if msg["type"] == kind:
            return msg


def test_health(client):
    assert client.get("/api/health").json()["status"] == "ok"


def test_create_invalid_and_sloppy(client):
    data = sample_data()
    data["Classes"].append({"Code": "Broken"})  # Name missing
    r = client.post("/api/projects", json={"dictionary": data})
    assert r.status_code == 422 and r.json()["can_sloppy"]
    pid = create(client, data, sloppy=True)
    doc = client.get(f"/api/projects/{pid}/dictionary.json").json()
    assert "Broken" not in [c["Code"] for c in doc["Classes"]]


def test_new_project_and_unknown(client):
    r = client.post("/api/projects", json={"header": {"DictionaryName": "Hello"}})
    assert r.status_code == 201
    assert client.get("/api/projects/does-not-exist-123456").status_code == 404


def test_collaboration_undo_redo_persistence(client, settings):
    pid = create(client)
    ws_a, a, hello_a = connect(client, pid, "client-a", "Alice")
    ws_b, b, hello_b = connect(client, pid, "client-b", "Bob")
    doc_b = hello_b["doc"]
    version_b = hello_b["version"]

    a.send_json({"type": "op", "rid": 1, "op": "class.update", "args": {"code": "Wall", "data": {"Name": "Mauer"}}})
    recv_until(a, "patch")
    ack = recv_until(a, "ack")
    assert ack["ok"] and ack["history"]["undo"] == "class.update"

    # Bob receives the same patch and ends up with the same document
    msg = recv_until(b, "patch")
    assert msg["version"] == version_b + 1 and msg["author"] == "client-a"
    doc_b = jsonpatch.apply(doc_b, msg["patch"])
    names = {c["Code"]: c["Name"] for c in doc_b["dictionary"]["Classes"]}
    assert names["Wall"] == "Mauer"

    # Bob cannot undo Alice's change
    b.send_json({"type": "undo", "rid": 2})
    assert recv_until(b, "ack")["ok"] is False

    # invalid op is rejected without changing anything
    a.send_json({"type": "op", "rid": 3, "op": "class.create", "args": {"data": {"Code": "Wall", "Name": "x"}}})
    ack = recv_until(a, "ack")
    assert not ack["ok"] and "exists" in ack["error"]

    # Alice undoes
    a.send_json({"type": "undo", "rid": 4})
    msg = recv_until(b, "patch")
    doc_b = jsonpatch.apply(doc_b, msg["patch"])
    assert {c["Code"]: c["Name"] for c in doc_b["dictionary"]["Classes"]}["Wall"] == "Wall"
    ack = recv_until(a, "ack")
    assert ack["ok"] and ack["history"]["redo"] == "class.update"

    # redo
    a.send_json({"type": "redo", "rid": 5})
    recv_until(a, "ack")
    msg = recv_until(b, "patch")
    doc_b = jsonpatch.apply(doc_b, msg["patch"])

    # conflicting undo: Bob changes the same class after Alice
    b.send_json({"type": "op", "rid": 6, "op": "class.update", "args": {"code": "Wall", "data": {"Name": "Bobs Wall"}}})
    assert recv_until(b, "ack")["ok"]
    a.send_json({"type": "undo", "rid": 7})
    ack = recv_until(a, "ack")
    assert not ack["ok"] and "someone else" in ack["error"]

    # presence
    a.send_json({"type": "presence", "selection": {"class": "Wall"}})
    users = recv_until(b, "users")["users"]
    assert any(u["selection"].get("class") == "Wall" for u in users)

    ws_a.__exit__(None, None, None)
    ws_b.__exit__(None, None, None)

    import time

    time.sleep(0.3)
    saved = json.loads((settings.projects_dir / pid / "dictionary.json").read_text(encoding="utf-8"))
    assert {c["Code"]: c["Name"] for c in saved["Classes"]}["Wall"] == "Bobs Wall"


def test_undo_survives_unrelated_list_changes(client):
    pid = create(client)
    ws_a, a, _ = connect(client, pid, "a")
    ws_b, b, _ = connect(client, pid, "b")
    a.send_json({"type": "op", "rid": 1, "op": "class.delete", "args": {"codes": ["Door"]}})
    assert recv_until(a, "ack")["ok"]
    b.send_json({"type": "op", "rid": 2, "op": "class.update", "args": {"code": "Building", "data": {"Definition": "x"}}})
    assert recv_until(b, "ack")["ok"]
    a.send_json({"type": "undo", "rid": 3})
    ack = recv_until(a, "ack")
    assert ack["ok"], ack
    doc = client.get(f"/api/projects/{pid}/dictionary.json").json()
    assert "Door" in [c["Code"] for c in doc["Classes"]]
    building = next(c for c in doc["Classes"] if c["Code"] == "Building")
    assert building["Definition"] == "x"
    ws_a.__exit__(None, None, None)
    ws_b.__exit__(None, None, None)


def test_exports_endpoint(client):
    pid = create(client)
    for kind in ("excel", "ids", "iso23386", "revit-psets", "revit-shared"):
        r = client.post(f"/api/projects/{pid}/export/{kind}", json={})
        assert r.status_code == 200, (kind, r.text)
        assert int(r.headers["x-export-count"]) > 0
    r = client.post(f"/api/projects/{pid}/export/iso7817", json={})
    assert r.status_code == 400  # empty LOIN
    r = client.post(f"/api/projects/{pid}/ids/candidates", json={})
    assert r.json()["candidates"][0]["pset"]


def test_shell_package(client):
    r = client.get("/api/shell/bsdd_json.zip")
    assert r.status_code == 200 and r.content[:2] == b"PK"


def test_reload_from_disk(settings):
    with TestClient(create_app(settings)) as c:
        pid = create(c)
    with TestClient(create_app(settings)) as c:
        info = c.get(f"/api/projects/{pid}").json()
        assert info["meta"]["name"] == "Sample"


def test_password_protection_and_read_only_link(client, settings):
    pid = create(client)
    # unprotected: open access, the caller can manage sharing
    assert client.get(f"/api/projects/{pid}").json()["role"] == "edit"
    r = client.post(f"/api/projects/{pid}/access", json={"edit_password": "geheim1", "view_enabled": True})
    assert r.status_code == 200, r.text
    info = r.json()
    owner = info["token"]
    view_id = info["view_id"]
    assert info["edit_protected"] and info["view_enabled"] and not info["view_protected"]

    # edit link now needs the password
    r = client.get(f"/api/projects/{pid}/dictionary.json")
    assert r.status_code == 401 and r.json()["reason"] == "password_required" and r.json()["role"] == "edit"
    assert client.post(f"/api/projects/{pid}/auth", json={"password": "wrong"}).status_code == 401
    token = client.post(f"/api/projects/{pid}/auth", json={"password": "geheim1"}).json()["token"]
    assert client.get(f"/api/projects/{pid}/dictionary.json", headers={"X-Project-Token": token}).status_code == 200
    assert client.get(f"/api/projects/{pid}/dictionary.json", headers={"X-Project-Token": owner}).status_code == 200

    # websocket without token is refused
    with client.websocket_connect(f"/api/projects/{pid}/ws?client=x") as ws:
        msg = ws.receive_json()
        assert msg["type"] == "error" and msg["error"] == "password_required" and msg["auth"]

    # read-only link: no password needed, never leaks the project id, cannot edit
    meta = client.get(f"/api/projects/{view_id}").json()
    assert meta["role"] == "view" and "id" not in meta["meta"] and "access" not in meta["meta"]
    assert client.get(f"/api/projects/{view_id}/dictionary.json").status_code == 200
    assert client.post(f"/api/projects/{view_id}/duplicate").status_code == 403
    assert client.get(f"/api/projects/{view_id}/access").status_code == 403
    ws, session, hello = connect(client, view_id, "viewer")
    assert hello["role"] == "view" and pid not in json.dumps(hello["meta"])
    session.send_json({"type": "op", "rid": 1, "op": "class.update", "args": {"code": "Wall", "data": {"Name": "Hacked"}}})
    ack = recv_until(session, "ack")
    assert not ack["ok"] and "read-only" in ack["error"]
    ws.__exit__(None, None, None)

    # protect the read-only link: viewers need the view (or edit) password
    r = client.post(f"/api/projects/{pid}/access", json={"view_password": "lesen"}, headers={"X-Project-Token": owner})
    owner = r.json()["token"]
    assert client.get(f"/api/projects/{view_id}").status_code == 401
    vt = client.post(f"/api/projects/{view_id}/auth", json={"password": "lesen"}).json()
    assert vt["role"] == "view"
    assert client.get(f"/api/projects/{view_id}", headers={"X-Project-Token": vt["token"]}).status_code == 200
    # a view token never grants edit access
    assert client.get(f"/api/projects/{pid}", headers={"X-Project-Token": vt["token"]}).status_code == 401
    # the edit password opens the read-only link too (read-only)
    assert client.post(f"/api/projects/{view_id}/auth", json={"password": "geheim1"}).json()["role"] == "view"

    # changing a password invalidates old tokens; the caller gets a new one
    r = client.post(f"/api/projects/{pid}/access", json={"edit_password": "neu12345"}, headers={"X-Project-Token": owner})
    new_owner = r.json()["token"]
    assert client.get(f"/api/projects/{pid}", headers={"X-Project-Token": token}).status_code == 401
    assert client.get(f"/api/projects/{pid}", headers={"X-Project-Token": new_owner}).status_code == 200

    # disabling the read-only link makes it disappear
    client.post(f"/api/projects/{pid}/access", json={"view_enabled": False}, headers={"X-Project-Token": new_owner})
    assert client.get(f"/api/projects/{view_id}").status_code == 404

    # settings survive a restart (hashes on disk, link index rebuilt)
    r = client.post(f"/api/projects/{pid}/access", json={"view_enabled": True}, headers={"X-Project-Token": client.post(f"/api/projects/{pid}/auth", json={"password": "neu12345"}).json()["token"]})
    view2 = r.json()["view_id"]
    meta_file = json.loads((settings.data_dir / "projects" / pid / "meta.json").read_text())
    assert "neu12345" not in json.dumps(meta_file) and meta_file["access"]["edit_password"].startswith("scrypt$")
    with TestClient(create_app(settings)) as c2:
        assert c2.get(f"/api/projects/{view2}").json()["role"] == "view"
        assert c2.get(f"/api/projects/{pid}").status_code == 401


def test_password_rate_limit(client):
    pid = create(client)
    client.post(f"/api/projects/{pid}/access", json={"edit_password": "geheim1"})
    codes = [client.post(f"/api/projects/{pid}/auth", json={"password": "x"}).status_code for _ in range(12)]
    assert codes[:10] == [401] * 10 and codes[-1] == 429


def test_view_link_changes_do_not_sign_out_editors(client):
    pid = create(client)
    owner = client.post(f"/api/projects/{pid}/access", json={"edit_password": "geheim1", "view_enabled": True}).json()["token"]
    editor = client.post(f"/api/projects/{pid}/auth", json={"password": "geheim1"}).json()["token"]
    r = client.post(f"/api/projects/{pid}/access", json={"view_password": "lesen", "regenerate_view": True}, headers={"X-Project-Token": owner})
    assert r.status_code == 200
    # editors stay signed in
    assert client.get(f"/api/projects/{pid}", headers={"X-Project-Token": editor}).status_code == 200
    # an edit password change signs everybody out
    client.post(f"/api/projects/{pid}/access", json={"edit_password": "anders1"}, headers={"X-Project-Token": r.json()["token"]})
    assert client.get(f"/api/projects/{pid}", headers={"X-Project-Token": editor}).status_code == 401


def test_connected_clients_are_disconnected_when_access_changes(client):
    pid = create(client)
    ws, session, _ = connect(client, pid, "someone")
    client.post(f"/api/projects/{pid}/access", json={"edit_password": "geheim1"})
    assert recv_until(session, "access_changed")["type"] == "access_changed"
    ws.__exit__(None, None, None)
