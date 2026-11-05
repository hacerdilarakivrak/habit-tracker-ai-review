from datetime import date, timedelta

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


def test_checkin_flow():
    hid = client.post("/habits", json={"name": "Stretch"}).json()["id"]
    r = client.post(f"/habits/{hid}/checkin", json={"day": "2026-09-22"})
    assert r.status_code == 200
    r2 = client.get(f"/habits/{hid}/checkins")
    assert r2.json() == ["2026-09-22"]


def test_checkin_unknown_habit_404():
    r = client.post("/habits/99999/checkin", json={"day": "2026-09-22"})
    assert r.status_code == 404


def test_summary_with_zero_checkins():
    hid = client.post("/habits", json={"name": "Meditate"}).json()["id"]
    r = client.get(f"/habits/{hid}/summary")
    assert r.status_code == 200
    assert r.json() == {"habit_id": hid, "count": 0}


def test_summary_counts_distinct_days_in_last_seven_days():
    hid = client.post("/habits", json={"name": "Journal"}).json()["id"]
    today = date.today()
    included_days = [today, today - timedelta(days=3), today - timedelta(days=3)]
    excluded_day = today - timedelta(days=7)

    for day in included_days + [excluded_day]:
        r = client.post(f"/habits/{hid}/checkin", json={"day": day.isoformat()})
        assert r.status_code == 200

    r = client.get(f"/habits/{hid}/summary")
    assert r.status_code == 200
    assert r.json() == {"habit_id": hid, "count": 2}


def test_summary_unknown_habit_404():
    r = client.get("/habits/99999/summary")
    assert r.status_code == 404
