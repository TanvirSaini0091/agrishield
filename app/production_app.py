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
import os
import uuid
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from app.agent import AGENT_STATE, analyze_plant_pathology, get_weather_telemetry

app = FastAPI(title="AgriShield Production API", version="1.0.0")

# Add CORS Middleware to allow requests from the dashboard frontend dynamically
frontend_url = os.getenv("FRONTEND_URL", "http://127.0.0.1:8000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-Memory State Store to track human-in-the-loop verification incidents
incident_queue = {}


class ExecuteRequest(BaseModel):
    latitude: float = Field(..., description="Latitude coordinate (-90.0 to 90.0).")
    longitude: float = Field(..., description="Longitude coordinate (-180.0 to 180.0).")
    crop: str = Field(..., description="Name of the crop (e.g. potato, tomato).")
    symptoms: str = Field(..., description="Description of crop leaf symptoms.")

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: float) -> float:
        if not (-90.0 <= v <= 90.0):
            raise ValueError("Latitude must be between -90.0 and 90.0")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        if not (-180.0 <= v <= 180.0):
            raise ValueError("Longitude must be between -180.0 and 180.0")
        return v


class ActionRequest(BaseModel):
    action: Literal["approve", "reject"]


@app.post("/v1/execute")
def execute_analysis(request: ExecuteRequest):
    # Reset global state to ensure complete request isolation
    AGENT_STATE["last_humidity"] = None
    AGENT_STATE["last_temperature"] = None

    # 1. Run Weather Telemetry Loop
    telemetry_result = get_weather_telemetry(request.latitude, request.longitude)
    if "Error" in telemetry_result:
        raise HTTPException(status_code=400, detail=telemetry_result)

    # Check if it triggers high-risk agronomic threshold (Potato with Relative Humidity > 75%)
    humidity_str = AGENT_STATE.get("last_humidity")
    high_humidity = False
    if humidity_str:
        try:
            humidity_val = int(humidity_str.replace("%", ""))
            if humidity_val > 75:
                high_humidity = True
        except Exception:
            pass

    if request.crop.lower() == "potato" and high_humidity:
        incident_id = str(uuid.uuid4())
        incident_queue[incident_id] = {
            "status": "Pending",
            "latitude": request.latitude,
            "longitude": request.longitude,
            "crop": request.crop,
            "symptoms": request.symptoms,
            "humidity": humidity_str,
            "temperature": AGENT_STATE.get("last_temperature"),
        }
        return {
            "status": "queued",
            "incident_id": incident_id,
            "message": "Incident queued for human-in-the-loop verification due to high-risk agronomic threshold.",
        }

    # 2. Run Plant Pathology Loop (sequentially, utilizing AGENT_STATE updated by telemetry)
    pathology_result = analyze_plant_pathology(request.crop, request.symptoms)
    if "Error" in pathology_result:
        raise HTTPException(status_code=400, detail=pathology_result)

    return {
        "telemetry": telemetry_result,
        "pathology": pathology_result,
        "state": {
            "last_humidity": AGENT_STATE.get("last_humidity"),
            "last_temperature": AGENT_STATE.get("last_temperature"),
        },
    }


@app.get("/v1/pending")
def get_pending_incidents():
    return {k: v for k, v in incident_queue.items() if v["status"] == "Pending"}


@app.post("/v1/execute/{incident_id}/action")
def execute_action(incident_id: str, request: ActionRequest):
    if incident_id not in incident_queue:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident = incident_queue[incident_id]
    if incident["status"] != "Pending":
        raise HTTPException(status_code=400, detail="Incident already processed")

    if request.action == "approve":
        # Propagate stored context state to AGENT_STATE before running pathology
        AGENT_STATE["last_humidity"] = incident["humidity"]
        AGENT_STATE["last_temperature"] = incident["temperature"]

        pathology_result = analyze_plant_pathology(
            incident["crop"], incident["symptoms"]
        )
        if "Error" in pathology_result:
            raise HTTPException(status_code=400, detail=pathology_result)

        incident["status"] = "Approved"
        incident["result"] = pathology_result

        return {"status": "Approved", "pathology": pathology_result}
    else:
        incident["status"] = "Rejected"
        return {
            "status": "Rejected",
            "message": "Incident verification rejected and marked as dismissed.",
        }
