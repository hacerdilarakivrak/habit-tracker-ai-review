import sqlite3
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "habits.db")
    with TestClient(main.app) as test_client:
        yield test_client


def test_create_and_list_habit(client):
    r = client.post("/habits", json={"name": "Read 20 minutes"})
    assert r.status_code == 200
    hid = r.json()["id"]
    r2 = client.get("/habits")
    assert r2.status_code == 200
    assert any(h["id"] == hid for h in r2.json())


def test_checkin_flow(client):
    hid = client.post("/habits", json={"name": "Stretch"}).json()["id"]
    r = client.post(f"/habits/{hid}/checkin", json={"day": "2026-09-22"})
    assert r.status_code == 200
    r2 = client.get(f"/habits/{hid}/checkins")
    assert r2.json() == ["2026-09-22"]


def test_checkin_unknown_habit_404(client):
    r = client.post("/habits/99999/checkin", json={"day": "2026-09-22"})
    assert r.status_code == 404


def test_summary_with_zero_checkins(client):
    hid = client.post("/habits", json={"name": "Meditate"}).json()["id"]
    r = client.get(f"/habits/{hid}/summary")
    assert r.status_code == 200
    assert r.json() == {"habit_id": hid, "count": 0}


def test_summary_counts_distinct_days_in_last_seven_days(client):
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


def test_summary_unknown_habit_404(client):
    r = client.get("/habits/99999/summary")
    assert r.status_code == 404


def test_summary_normalizes_and_rejects_noncanonical_stored_days(client, monkeypatch):
    class FixedDate(date):
        @classmethod
        def today(cls):
            return cls(2026, 3, 2)

    monkeypatch.setattr(main, "date", FixedDate)
    hid = client.post("/habits", json={"name": "Read"}).json()["id"]
    with sqlite3.connect(main.DB_PATH) as conn:
        conn.executemany(
            "INSERT INTO checkins (habit_id, day) VALUES (?, ?)",
            [
                (hid, "2026-02-28"),
                (hid, "2026-02-28T12:00:00"),
                (hid, "2026-02-30"),
                (hid, "2026-03-01malformed"),
                (hid, "2026-02-23"),
            ],
        )

    r = client.get(f"/habits/{hid}/summary")
    assert r.status_code == 200
    assert r.json() == {"habit_id": hid, "count": 1}


def test_client_uses_an_isolated_temporary_database(client, tmp_path):
    assert main.DB_PATH == tmp_path / "habits.db"
    assert client.get("/habits").json() == []
