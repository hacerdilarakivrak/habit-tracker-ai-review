from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_create_and_list_habit():
    r = client.post("/habits", json={"name": "Read 20 minutes"})
    assert r.status_code == 200
    hid = r.json()["id"]
    r2 = client.get("/habits")
    assert r2.status_code == 200
    assert any(h["id"] == hid for h in r2.json())


def test_create_habit_rejects_empty_name():
    r = client.post("/habits", json={"name": ""})
    assert r.status_code == 400
    assert r.json()["detail"] == "habit name must not be empty"


def test_create_habit_rejects_whitespace_only_name():
    r = client.post("/habits", json={"name": " \t\n "})
    assert r.status_code == 400
    assert r.json()["detail"] == "habit name must not be empty"


def test_checkin_flow():
    hid = client.post("/habits", json={"name": "Stretch"}).json()["id"]
    r = client.post(f"/habits/{hid}/checkin", json={"day": "2026-09-22"})
    assert r.status_code == 200
    r2 = client.get(f"/habits/{hid}/checkins")
    assert r2.json() == ["2026-09-22"]


def test_checkin_rejects_malformed_date():
    hid = client.post("/habits", json={"name": "Walk"}).json()["id"]
    r = client.post(f"/habits/{hid}/checkin", json={"day": "09/22/2026"})
    assert r.status_code == 400
    assert r.json()["detail"] == "day must be a valid date in YYYY-MM-DD format"


def test_checkin_rejects_invalid_calendar_date():
    hid = client.post("/habits", json={"name": "Walk"}).json()["id"]
    r = client.post(f"/habits/{hid}/checkin", json={"day": "2026-02-30"})
    assert r.status_code == 400
    assert r.json()["detail"] == "day must be a valid date in YYYY-MM-DD format"


def test_checkin_unknown_habit_404():
    r = client.post("/habits/99999/checkin", json={"day": "2026-09-22"})
    assert r.status_code == 404
