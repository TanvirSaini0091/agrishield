Local Project Context & Secure Coding Standards
Core Paved Roads
We systematically address common vulnerability classes by guiding the agent to use our pre-configured, secure-by-default helper patterns instead of writing raw implementation logic from scratch.

Tool Input Validation: Every agricultural agent tool (weather, plant pathology, market data) must strictly validate incoming parameters (like latitude, longitude, and file formats) against strict Pydantic schemas rather than parsing raw dictionaries or strings.

No Shell Execution: Never use run_command or raw shell execution tools unless explicitly approved by hooks.json.

Pre-Commit Remediation Loop: If a git commit fails due to a pre-commit hook error (such as a Semgrep scan finding), you MUST treat the violation as a refactoring task, apply targeted fixes, run tests to verify no regressions, and attempt to commit again.

TDD Planning Gate
During the Plan phase, you must decompose the workspace task into logical, modular stages. Every implementation plan MUST include a dedicated Security Boundaries & Assertions section outlining specific edge cases (such as malformed parameter strings, out-of-bounds latitude/longitude values, and unauthenticated session requests) that could exploit the feature.
