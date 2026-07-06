# AgriShield Security & Telemetry Agent Framework

AgriShield is an advanced, secure agricultural extension agent combining real-time crop telemetry, plant pathology diagnostics, and a human-in-the-loop (HITL) incident resolution gateway. It features robust parameter validation, automated retry policies, command injection hooks, and a containerized production deployment model.

---

## Project Structure

```
agrishield/
├── app/                        # Core Application Code
│   ├── agent.py                # ReAct agent, tools, retry policy, and validation models
│   ├── production_app.py       # Production FastAPI API with HITL verification queue
│   └── app_utils/              # Application utilities
├── submission_frontend/         # Manager Dashboard Service
│   ├── main.py                 # Standalone FastAPI manager UI and polling gateway
│   └── Dockerfile              # Docker container for the frontend dashboard
├── tests/                      # Testing Suite (Unit, integration, and retry logic)
├── .agents/                    # Secure Development Hooks & Policies
│   ├── CONTEXT.md              # Secure coding paved roads
│   ├── hooks.json              # Tool call pre-execution intercepts
│   └── scripts/                # Validation scripts to block destructive commands
├── .semgrep/                   # Custom Semgrep Static Analysis Rules
│   └── rules.yaml              # Pattern scanning to prevent key exposure
├── threat_model.md             # STRIDE Threat Model analysis report
├── Dockerfile                  # Docker container for the production FastAPI backend
├── pyproject.toml              # Dependencies definition
└── README.md                   # Project documentation
```

---

## Requirements

Ensure you have the following installed locally:
- **uv**: Fast Python package installer and manager - [Install](https://docs.astral.sh/uv/getting-started/installation/)
- **google-agents-cli**: Command-line tool for agent development - Install with `uv tool install google-agents-cli`

---

## Setup & Running Locally

### 1. Install Dependencies
Run the installation command to sync python packages and lock environment variables:
```bash
agents-cli install
```

### 2. Run the Services
To fully test the incident loop, run both the backend API and the frontend dashboard:

*   **Start the Backend Production API** (runs on port `8080`):
    ```bash
    uv run uvicorn app.production_app:app --host 127.0.0.1 --port 8080
    ```

*   **Start the Standalone Dashboard UI** (runs on port `8000`):
    Configure the backend target using browser redirection or direct environment config, then run:
    ```bash
    cd submission_frontend
    uv run uvicorn main:app --host 127.0.0.1 --port 8000
    ```

Navigate to `http://127.0.0.1:8000` in your web browser to monitor incoming high-risk incidents.

---

## Core Application Features

### 1. Automated Weather Telemetry & State Updates
The weather telemetry tool (`get_weather_telemetry`) automatically updates a global state object storing simulated temperature and relative humidity. The pathology engine (`analyze_plant_pathology`) reads this context. In high-humidity conditions (>75%), the system automatically flags critical crop diseases like Late Blight.

### 2. Human-in-the-Loop Verification Queue
High-risk incidents (such as Potato crops experiencing >75% humidity) are intercepted at `POST /v1/execute`, cached with a status of `"Pending"`, and returned via `GET /v1/pending`. Verification actions (`POST /v1/execute/{id}/action` with `"approve"` or `"reject"`) allow managers to manually execute the Gemini pathology analysis or dismiss the warning.

### 3. Production Fault Tolerance & Fallbacks
*   **Tenacity Retry Loop**: The asynchronous Gemini model execution is wrapped with a tenacity retry policy that automatically intercepts transient API errors (status codes 429 and 503) and retries up to 3 times with exponential backoff.
*   **Structured Local Fallbacks**: If the Gemini API call encounters a persistent server error or timeout, the agent catches the exception and falls back to a local rule-based diagnostic engine. It prepends the output with a server load notice to guarantee service uptime.

### 4. Out-of-Scope Protection
The pathology tool implements strict system instructions blocking non-agricultural prompts (such as recipe requests or PC hardware optimizations). It immediately returns the standard out-of-scope block phrase:
`"I can only assist with agricultural issues such as crop telemetry, plant pathology, or farming support. This request is out of scope."`

---

## Security & Verification Controls

-   **Command Intercept Validation**: Registered a `PreToolUse` hook in `.agents/hooks.json` mapping to a Python script that sanitizes execution arguments. It blocks destructive commands (like `rm -rf` or `mkfs`) returning Exit Code 2.
-   **Static Analysis Key Guard**: Custom Semgrep rules (`.semgrep/rules.yaml`) actively check files during development to catch hardcoded Google credentials or developer API keys.
-   **Threat Analysis**: A full STRIDE evaluation (`threat_model.md`) has been generated to assess data flows, coordinate validation bounds, and implement prompt injection defenses.

---

## Testing & Quality Assurance

### Run Unit and Integration Tests
To execute all unit, integration, and retry logic test suites:
```bash
uv run pytest tests/unit/
```

### Run Code Linter and Style Checkers
```bash
agents-cli lint
```
This runs `ruff check`, `ruff format`, `codespell`, and `ty check` sequentially to guarantee absolute codebase compliance.
