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

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="AgriShield Manager Dashboard", version="1.0.0")

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8080")

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AgriShield Manager Dashboard</title>
    <!-- Inter Google Font (SF Pro substitute) -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #0066cc;
            --primary-focus: #0071e3;
            --high-risk: #ff453a;
            --ink: #1d1d1f;
            --body: #1d1d1f;
            --body-muted: #7a7a7a;
            --canvas: #ffffff;
            --canvas-parchment: #f5f5f7;
            --hairline: #e0e0e0;
            --divider-soft: #f0f0f0;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Inter', -apple-system, system-ui, sans-serif;
            background-color: var(--canvas-parchment);
            color: var(--body);
            min-height: 100vh;
            overflow-x: hidden;
            -webkit-font-smoothing: antialiased;
        }

        /* Apple Top Navigation Bars */
        .global-nav {
            background-color: #000000;
            height: 44px;
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            position: fixed;
            top: 0;
            left: 0;
            z-index: 1001;
            padding: 0 24px;
        }

        .global-nav-content {
            width: 100%;
            max-width: 1024px;
            display: flex;
            align-items: center;
            color: #ffffff;
            font-size: 12px;
            letter-spacing: -0.12px;
        }

        .global-nav-logo {
            font-weight: 700;
            letter-spacing: 0.5px;
            color: #ffffff;
            text-decoration: none;
        }

        .sub-nav-frosted {
            background-color: rgba(255, 255, 255, 0.8);
            backdrop-filter: saturate(180%) blur(20px);
            -webkit-backdrop-filter: saturate(180%) blur(20px);
            height: 52px;
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            position: fixed;
            top: 44px;
            left: 0;
            z-index: 1000;
            border-bottom: 1px solid var(--hairline);
            padding: 0 24px;
        }

        .sub-nav-content {
            width: 100%;
            max-width: 1024px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .sub-nav-title {
            font-size: 21px;
            font-weight: 600;
            letter-spacing: 0.231px;
            color: var(--ink);
        }

        .status-indicator {
            font-size: 12px;
            color: var(--body-muted);
            font-weight: 400;
        }

        /* Container Layout */
        .container {
            max-width: 1024px;
            margin: 96px auto 0 auto; /* offset for nav bars */
            padding: 48px 24px;
        }

        header.dashboard-header {
            margin-bottom: 40px;
            text-align: left;
        }

        header.dashboard-header h2 {
            font-size: 40px;
            font-weight: 600;
            line-height: 1.1;
            letter-spacing: -0.02em;
            color: var(--ink);
        }

        header.dashboard-header p {
            color: var(--body-muted);
            font-size: 17px;
            margin-top: 8px;
            line-height: 1.47;
            letter-spacing: -0.374px;
        }

        /* Empty State */
        .empty-state {
            display: none;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 80px 40px;
            background-color: var(--canvas);
            border-radius: 18px;
            border: 1px solid var(--hairline);
            text-align: center;
        }

        .empty-state-icon {
            font-size: 40px;
            margin-bottom: 16px;
            color: #30d158;
        }

        .empty-state h3 {
            font-size: 21px;
            font-weight: 600;
            margin-bottom: 8px;
            letter-spacing: -0.01em;
        }

        .empty-state p {
            color: var(--body-muted);
            font-size: 14px;
            max-width: 320px;
            line-height: 1.43;
        }

        /* Grid & Cards */
        .queue-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(310px, 1fr));
            gap: 24px;
        }

        .incident-card {
            background-color: var(--canvas);
            border-radius: 18px;
            border: 1px solid var(--hairline);
            padding: 24px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.3s cubic-bezier(0.25, 1, 0.5, 1);
            position: relative;
        }

        .incident-card:hover {
            transform: translateY(-2px);
            border-color: #b0b0b0;
        }

        .incident-card.high-risk {
            border: 2px solid var(--high-risk);
        }

        .incident-card.high-risk:hover {
            border-color: var(--high-risk);
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .crop-badge {
            font-size: 12px;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 9999px;
            background-color: var(--canvas-parchment);
            border: 1px solid var(--hairline);
            color: var(--ink);
            text-transform: uppercase;
        }

        .crop-badge.high-risk {
            background-color: rgba(255, 69, 58, 0.08);
            border-color: rgba(255, 69, 58, 0.2);
            color: var(--high-risk);
        }

        .humidity-badge {
            font-size: 13px;
            color: var(--body-muted);
        }

        /* Card Body */
        .card-body {
            margin-bottom: 24px;
        }

        .symptoms-title {
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--body-muted);
            margin-bottom: 6px;
        }

        .symptoms-text {
            font-size: 15px;
            line-height: 1.47;
            margin-bottom: 16px;
            color: var(--ink);
            font-weight: 400;
        }

        .meta-row {
            display: flex;
            gap: 20px;
            background-color: var(--canvas-parchment);
            padding: 8px 12px;
            border-radius: 8px;
            border: 1px solid var(--hairline);
        }

        .meta-item {
            display: flex;
            flex-direction: column;
        }

        .meta-label {
            font-size: 11px;
            color: var(--body-muted);
        }

        .meta-val {
            font-size: 13px;
            font-weight: 600;
            color: var(--ink);
            margin-top: 1px;
        }

        /* Button Layout (Capsule Pill Styles) */
        .card-actions {
            display: flex;
            gap: 12px;
        }

        button {
            cursor: pointer;
            font-family: inherit;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.2s ease;
            border-radius: 9999px; /* Pill Radius */
            outline: none;
        }

        .btn-approve {
            flex: 1;
            background-color: var(--primary);
            color: #ffffff;
            border: none;
            padding: 10px 20px;
        }

        .btn-approve:hover {
            background-color: var(--primary-focus);
        }

        .btn-approve:active {
            transform: scale(0.95);
        }

        .btn-reject {
            flex: 1;
            background-color: transparent;
            color: var(--ink);
            border: 1px solid #d2d2d7;
            padding: 10px 20px;
        }

        .btn-reject:hover {
            background-color: var(--canvas-parchment);
            color: var(--high-risk);
            border-color: var(--high-risk);
        }

        .btn-reject:active {
            transform: scale(0.95);
        }

        .incident-card.processing {
            opacity: 0.4;
            pointer-events: none;
        }

        /* Slide-out Drawer Panel */
        .drawer {
            position: fixed;
            top: 0;
            right: 0;
            bottom: 0;
            width: 480px;
            background-color: rgba(255, 255, 255, 0.95);
            backdrop-filter: saturate(180%) blur(30px);
            -webkit-backdrop-filter: saturate(180%) blur(30px);
            border-left: 1px solid var(--hairline);
            box-shadow: -10px 0 40px rgba(0, 0, 0, 0.05);
            z-index: 1000;
            transform: translateX(100%);
            transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            display: flex;
            flex-direction: column;
            margin-top: 44px; /* Align with global nav */
        }

        .drawer.open {
            transform: translateX(0);
        }

        .drawer-header {
            padding: 24px;
            border-bottom: 1px solid var(--divider-soft);
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }

        .btn-close {
            background-color: var(--canvas-parchment);
            border: 1px solid var(--hairline);
            color: var(--ink);
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
        }

        .btn-close:hover {
            background-color: #e8e8ed;
        }

        .drawer-body {
            padding: 24px;
            flex: 1;
            overflow-y: auto;
        }

        .drawer-header-content h3 {
            font-size: 22px;
            font-weight: 600;
            letter-spacing: -0.01em;
            color: var(--ink);
        }

        .drawer-meta {
            font-size: 13px;
            color: var(--body-muted);
            margin-top: 4px;
        }

        .drawer-loading {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 80px 0;
            gap: 16px;
            color: var(--body-muted);
            font-size: 14px;
        }

        .spinner {
            width: 28px;
            height: 28px;
            border: 3px solid rgba(0, 0, 0, 0.05);
            border-top: 3px solid var(--primary);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .drawer-result {
            margin-top: 12px;
        }

        .result-card {
            background-color: var(--canvas);
            border: 1px solid var(--hairline);
            border-radius: 14px;
            padding: 24px;
        }

        .result-icon-badge {
            width: 32px;
            height: 32px;
            background-color: rgba(48, 209, 88, 0.1);
            border: 1px solid rgba(48, 209, 88, 0.2);
            color: #30d158;
            font-size: 14px;
            font-weight: 700;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 20px;
        }

        .result-text {
            font-size: 15px;
            line-height: 1.5;
            color: var(--body);
        }

        .result-text strong {
            color: var(--ink);
        }

        .fadeIn {
            animation: fadeIn 0.4s ease forwards;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @media (max-width: 640px) {
            .drawer {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <!-- Apple Pinned Global Nav Bar -->
    <div class="global-nav">
        <div class="global-nav-content">
            <a href="#" class="global-nav-logo">AgriShield</a>
        </div>
    </div>

    <!-- Apple Sub-Nav Frosted Glass Bar -->
    <div class="sub-nav-frosted">
        <div class="sub-nav-content">
            <span class="sub-nav-title">Queue</span>
            <span class="status-indicator">Live connection active</span>
        </div>
    </div>

    <div class="container">
        <header class="dashboard-header">
            <h2>Incident Resolution Gateway</h2>
            <p>Review and action pending agricultural safety incidents flagged by crop telemetry validation.</p>
        </header>

        <!-- Empty State Message -->
        <div id="empty-state" class="empty-state">
            <div class="empty-state-icon">✓</div>
            <h3>All caught up</h3>
            <p>No pending agricultural incidents require manual manager verification at this time.</p>
        </div>

        <!-- Dynamic Grid of Incident Cards -->
        <div id="queue-grid" class="queue-grid"></div>
    </div>

    <!-- Slide-out Resolution Drawer Panel -->
    <div id="drawer" class="drawer">
        <div class="drawer-header">
            <div id="drawer-header-info"></div>
            <button class="btn-close" onclick="closeDrawer()">✕</button>
        </div>
        <div id="drawer-body" class="drawer-body"></div>
    </div>

    <script>
        const BACKEND_URL = "http://127.0.0.1:8080";
        let pendingIncidents = {};

        async function pollQueue() {
            try {
                const response = await fetch(`${BACKEND_URL}/v1/pending`);
                if (!response.ok) throw new Error("Failed to fetch pending queue");
                const data = await response.json();
                pendingIncidents = data;
                renderQueue();
            } catch (err) {
                console.error("Error polling pending queue:", err);
            }
        }

        function renderQueue() {
            const grid = document.getElementById("queue-grid");
            const emptyState = document.getElementById("empty-state");
            const keys = Object.keys(pendingIncidents);

            if (keys.length === 0) {
                grid.style.display = "none";
                emptyState.style.display = "flex";
                return;
            }

            grid.style.display = "grid";
            emptyState.style.display = "none";

            grid.innerHTML = "";
            keys.forEach(id => {
                const incident = pendingIncidents[id];
                const isHighRisk = incident.crop.toLowerCase() === "potato";

                const card = document.createElement("div");
                card.className = `incident-card ${isHighRisk ? 'high-risk' : ''}`;
                card.id = `card-${id}`;

                card.innerHTML = `
                    <div class="card-header">
                        <span class="crop-badge ${isHighRisk ? 'high-risk' : ''}">${incident.crop.toUpperCase()}</span>
                        <span class="humidity-badge">${incident.humidity} Humidity</span>
                    </div>
                    <div class="card-body">
                        <p class="symptoms-title">Reported Symptoms</p>
                        <p class="symptoms-text">"${incident.symptoms}"</p>
                        <div class="meta-row">
                            <div class="meta-item">
                                <span class="meta-label">Latitude</span>
                                <span class="meta-val">${incident.latitude.toFixed(4)}</span>
                            </div>
                            <div class="meta-item">
                                <span class="meta-label">Longitude</span>
                                <span class="meta-val">${incident.longitude.toFixed(4)}</span>
                            </div>
                        </div>
                    </div>
                    <div class="card-actions">
                        <button class="btn-approve" onclick="handleAction('${id}', 'approve')">Approve</button>
                        <button class="btn-reject" onclick="handleAction('${id}', 'reject')">Reject</button>
                    </div>
                `;
                grid.appendChild(card);
            });
        }

        async function handleAction(incidentId, action) {
            const card = document.getElementById(`card-${incidentId}`);
            if (card) {
                card.classList.add("processing");
            }

            openDrawer(incidentId, action);

            try {
                const response = await fetch(`${BACKEND_URL}/v1/execute/${incidentId}/action`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ action: action })
                });

                if (!response.ok) throw new Error("Failed to process action");
                const data = await response.json();

                if (action === "approve") {
                    displayResult(data.pathology, "Approved");
                } else {
                    displayResult(data.message, "Rejected");
                    if (card) card.remove();
                }
            } catch (err) {
                console.error("Action error:", err);
                displayError(action === "approve"
                    ? "Error retrieving pathology diagnosis. Please try again."
                    : "Error processing rejection request. Please try again."
                );
                if (card) {
                    card.classList.remove("processing");
                }
            }
        }

        function openDrawer(incidentId, action) {
            const drawer = document.getElementById("drawer");
            const drawerHeaderInfo = document.getElementById("drawer-header-info");
            const drawerBody = document.getElementById("drawer-body");
            const incident = pendingIncidents[incidentId];

            const statusLabel = action === "approve" ? "Verifying Crop" : "Dismissing Incident";

            drawerHeaderInfo.innerHTML = `
                <div class="drawer-header-content">
                    <h3>${statusLabel}: ${incident.crop.toUpperCase()}</h3>
                    <p class="drawer-meta">Lat: ${incident.latitude.toFixed(4)} · Lon: ${incident.longitude.toFixed(4)} · Humidity: ${incident.humidity}</p>
                </div>
            `;

            const loadingText = action === "approve"
                ? "Requesting pathology model analysis..."
                : "Dismissing incident alert and marking queue...";

            drawerBody.innerHTML = `
                <div class="drawer-loading">
                    <div class="spinner"></div>
                    <p>${loadingText}</p>
                </div>
            `;
            drawer.classList.add("open");
        }

        function displayResult(contentResult, actionStatus) {
            const drawerBody = document.getElementById("drawer-body");
            drawerBody.innerHTML = "";

            const formattedResult = contentResult
                .replace(/Diagnosis:/g, '<strong>Diagnosis:</strong>')
                .replace(/Risk:/g, '<br><br><strong>Risk:</strong>')
                .replace(/Recommendation:/g, '<br><br><strong>Recommendation:</strong>')
                .replace(/Action:/g, '<br><br><strong>Action Required:</strong>');

            const isRejected = actionStatus === "Rejected";

            const resultDiv = document.createElement("div");
            resultDiv.className = "drawer-result fadeIn";
            resultDiv.innerHTML = `
                <div class="result-card">
                    <div class="result-icon-badge" style="background-color: ${isRejected ? 'rgba(255, 69, 58, 0.1)' : 'rgba(48, 209, 88, 0.1)'}; border-color: ${isRejected ? 'rgba(255, 69, 58, 0.2)' : 'rgba(48, 209, 88, 0.2)'}; color: ${isRejected ? '#ff453a' : '#30d158'};">
                        ${isRejected ? '✕' : '✓'}
                    </div>
                    <p class="result-text">${formattedResult}</p>
                </div>
            `;
            drawerBody.appendChild(resultDiv);
            pollQueue();
        }

        function displayError(message) {
            const drawerBody = document.getElementById("drawer-body");
            drawerBody.innerHTML = "";
            const errorDiv = document.createElement("div");
            errorDiv.className = "drawer-error fadeIn";
            errorDiv.innerHTML = `<p style="color: var(--high-risk);">${message}</p>`;
            drawerBody.appendChild(errorDiv);
        }

        function closeDrawer() {
            document.getElementById("drawer").classList.remove("open");
        }

        window.addEventListener("DOMContentLoaded", () => {
            pollQueue();
            setInterval(pollQueue, 3000);
        });
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def get_dashboard():
    # Dynamically inject the BACKEND_URL environment variable value into the JavaScript context
    html_content = DASHBOARD_HTML.replace(
        'const BACKEND_URL = "http://127.0.0.1:8080";',
        f'const BACKEND_URL = "{BACKEND_URL}";',
    )
    return html_content
