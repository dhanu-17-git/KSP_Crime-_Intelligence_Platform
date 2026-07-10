import pytest
from sqlalchemy import select
from app.core.database import get_db_session
from app.models.fir import Notification, Accused, CaseNote

def test_action_notify_station(client):
    # 1. Start thread
    resp = client.post(
        "/api/v1/investigation/query",
        json={"query_text": "Vikram Hegde", "requested_by": "officer-demo", "thread_id": None}
    )
    assert resp.status_code == 200
    data = resp.json()
    thread_id = data["thread_id"]
    assert thread_id

    # 2. Trigger mock notify_station
    followup_resp = client.post(
        "/api/v1/investigation/query",
        json={
            "query_text": "Notify station Nazarbad PS regarding active suspect alert.",
            "requested_by": "officer-demo",
            "thread_id": thread_id
        }
    )
    assert followup_resp.status_code == 200
    followup_data = followup_resp.json()
    assert followup_data["type"] == "action"
    assert "ACTION TAKEN" in followup_data["report_text"]
    assert "Nazarbad PS" in followup_data["report_text"]


def test_action_flag_suspect(client):
    # 1. Start thread
    resp = client.post(
        "/api/v1/investigation/query",
        json={"query_text": "Ramesh Adiga", "requested_by": "officer-demo", "thread_id": None}
    )
    assert resp.status_code == 200
    thread_id = resp.json()["thread_id"]

    # 2. Trigger mock flag_suspect
    followup_resp = client.post(
        "/api/v1/investigation/query",
        json={
            "query_text": "Flag suspect 90008 reason suspect fleeing custody.",
            "requested_by": "officer-demo",
            "thread_id": thread_id
        }
    )
    assert followup_resp.status_code == 200
    followup_data = followup_resp.json()
    assert followup_data["type"] == "action"
    assert "ACTION TAKEN" in followup_data["report_text"]
    assert "90008" in followup_data["report_text"]


def test_action_add_case_note(client):
    # 1. Start thread
    resp = client.post(
        "/api/v1/investigation/query",
        json={"query_text": "Prakash Gowda", "requested_by": "officer-demo", "thread_id": None}
    )
    assert resp.status_code == 200
    thread_id = resp.json()["thread_id"]

    # 2. Trigger mock add_case_note
    followup_resp = client.post(
        "/api/v1/investigation/query",
        json={
            "query_text": "Add case note 90005: Weapon recovered at Cubbon Park scene.",
            "requested_by": "officer-demo",
            "thread_id": thread_id
        }
    )
    assert followup_resp.status_code == 200
    followup_data = followup_resp.json()
    assert followup_data["type"] == "action"
    assert "ACTION TAKEN" in followup_data["report_text"]
    assert "90005" in followup_data["report_text"]


def test_ambiguous_followup_no_action(client):
    # 1. Start thread
    resp = client.post(
        "/api/v1/investigation/query",
        json={"query_text": "Deepak Kulkarni", "requested_by": "officer-demo", "thread_id": None}
    )
    assert resp.status_code == 200
    thread_id = resp.json()["thread_id"]

    # 2. Ambiguous query (no action triggered)
    followup_resp = client.post(
        "/api/v1/investigation/query",
        json={
            "query_text": "What is the status of the cheating case?",
            "requested_by": "officer-demo",
            "thread_id": thread_id
        }
    )
    assert followup_resp.status_code == 200
    followup_data = followup_resp.json()
    assert followup_data["type"] == "report"  # Normal report, not action
    assert "ACTION TAKEN" not in followup_data["report_text"]
