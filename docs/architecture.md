# C-Drishti Architecture

C-Drishti currently runs as a browser-based demonstration prototype. The application maintains synthetic enforcement events in memory and demonstrates four flows: traffic enforcement, weighbridge fusion, public-safety hotspot escalation, and industrial-emission escalation.

```text
Sensors / Demo Events
        |
        v
Sense -> Fuse -> Analyse -> Route
        |
        +--> Role-based officer queues
        +--> Cross-department alerts
        +--> Audit log
        +--> Legal retrieval assistant

Procurement workbook -> Python anomaly screen -> Audit-priority signals
```

## Current implementation

- Frontend: single-file HTML/CSS/JavaScript application.
- State: browser memory; refresh resets the demo.
- Legal assistant: conservative keyword retrieval with optional local Ollama generation.
- Analytics: Python 3-sigma screening over a workbook.
- Public data: synthetic demonstration workbook only.

## Planned production evolution

The next version will separate the frontend and backend, add FastAPI and PostgreSQL, replace keyword retrieval with embeddings-based RAG, and add stronger anomaly methods plus persistent audit logging.
