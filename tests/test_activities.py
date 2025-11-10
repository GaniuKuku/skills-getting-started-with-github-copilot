from urllib.parse import quote

from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


client = TestClient(app)


def test_get_activities()
:
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # basic sanity: known activity exists
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "tester@example.com"

    # Ensure clean start
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # signup (email passed as query param)
    resp = client.post(f"/activities/{quote(activity)}/signup", params={"email": email})
    assert resp.status_code == 200
    assert f"Signed up {email}" in resp.json().get("message", "")

    # GET should now include the email
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email in resp.json()[activity]["participants"]

    # duplicate signup should fail
    resp_dup = client.post(f"/activities/{quote(activity)}/signup", params={"email": email})
    assert resp_dup.status_code == 400

    # unregister
    resp_unreg = client.delete(f"/activities/{quote(activity)}/participants", params={"email": email})
    assert resp_unreg.status_code == 200

    # ensure removed
    resp = client.get("/activities")
    assert email not in resp.json()[activity]["participants"]


def test_unregister_nonexistent_returns_404():
    activity = "Chess Club"
    email = "doesnotexist@example.com"

    # Ensure not present
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    resp = client.delete(f"/activities/{quote(activity)}/participants", params={"email": email})
    assert resp.status_code == 404
