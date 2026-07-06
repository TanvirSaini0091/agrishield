---
name: stride-threat-model
description: Performs a systematic STRIDE threat modeling assessment on the current project's codebase and architecture. Use this when starting a new implementation phase or reviewing existing components.
---

# STRIDE Threat Modeling Skill

## Goal
Guide the agent to analyze the workspace directory structure, configuration files, and code files to produce a structured threat_model.md assessment.

## Instructions
### Analyze System Boundaries
Map the entry points (agricultural tools, workflow inputs, latitude/longitude parameters) and data handling layers.

### STRIDE Evaluation
Evaluate the system against the six STRIDE pillars:

* **Spoofing**: Are user identities verified before processing operational field coordinates or triggers?
* **Tampering**: Can a user manipulate parameter arrays, data feeds, or the underlying tracking state?
* **Repudiation**: Are critical agronomic insights and transaction validations logged securely?
* **Information Disclosure**: Are we risking leakage of sensitive system logs, internal backend tokens, or raw crash dumps to end users?
* **Denial of Service**: Are there rate limits or safety buffers guarding expensive API or LLM tool requests?
* **Elevation of Privilege**: Can an unauthenticated user bypass access control to trigger admin or restricted workflow utilities?

### Output
Generate a highly structured threat_model.md saved directly into the workspace root.
