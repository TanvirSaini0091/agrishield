# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from fastapi.testclient import TestClient

from app.agent import AGENT_STATE
from app.production_app import app, incident_queue

client = TestClient(app)


def test_production_app_normal_flow():
    # Clear state and queue
    incident_queue.clear()
    AGENT_STATE["last_humidity"] = None
    AGENT_STATE["last_temperature"] = None

    # Normal tomato request (not queued)
    payload = {
        "latitude": 45.0,
        "longitude": 45.0,
        "crop": "tomato",
        "symptoms": "yellow spots",
    }
    response = client.post("/v1/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "telemetry" in data
    assert "Early Blight" in data["pathology"]
    assert data["state"]["last_humidity"] == "60%"


def test_production_app_human_in_the_loop_flow():
    incident_queue.clear()

    # High-risk potato request at equatorial zone (90% humidity)
    payload = {
        "latitude": 5.0,
        "longitude": 45.0,
        "crop": "potato",
        "symptoms": "dark water-soaked spots",
    }
    response = client.post("/v1/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"
    assert "incident_id" in data
    incident_id = data["incident_id"]

    # Check pending queue
    pending_response = client.get("/v1/pending")
    assert pending_response.status_code == 200
    pending_data = pending_response.json()
    assert incident_id in pending_data
    assert pending_data[incident_id]["status"] == "Pending"
    assert pending_data[incident_id]["crop"] == "potato"

    # Action: Approve
    action_payload = {"action": "approve"}
    action_response = client.post(
        f"/v1/execute/{incident_id}/action", json=action_payload
    )
    assert action_response.status_code == 200
    action_data = action_response.json()
    assert action_data["status"] == "Approved"
    assert "Late Blight" in action_data["pathology"]

    # Try to approve again (should fail)
    action_response_dup = client.post(
        f"/v1/execute/{incident_id}/action", json=action_payload
    )
    assert action_response_dup.status_code == 400


def test_production_app_reject_flow():
    incident_queue.clear()

    payload = {
        "latitude": 5.0,
        "longitude": 45.0,
        "crop": "potato",
        "symptoms": "dark water-soaked spots",
    }
    response = client.post("/v1/execute", json=payload)
    incident_id = response.json()["incident_id"]

    # Action: Reject
    action_payload = {"action": "reject"}
    action_response = client.post(
        f"/v1/execute/{incident_id}/action", json=action_payload
    )
    assert action_response.status_code == 200
    assert action_response.json()["status"] == "Rejected"

    # Verify no longer in pending list
    pending_response = client.get("/v1/pending")
    assert incident_id not in pending_response.json()
