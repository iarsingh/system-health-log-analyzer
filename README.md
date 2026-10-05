# System Health & Log Analyzer

<!-- project-guide:start -->
## Project guide

[Project architecture](PROJECT_ARCHITECTURE.md) · [Interview questions and answers](INTERVIEW_QA.md)

Use the architecture document for the component diagram, implementation boundaries, and verification entry points. The interview guide includes source-backed answers and project walkthroughs.

### Implementation map

| Component | Responsibility |
| --- | --- |
| [`src/analyzer/main.py`](src/analyzer/main.py) | HTTP handlers: `GET /healthz`, `POST /ingest`, `GET /alerts` |
| [`src/analyzer/detect.py`](src/analyzer/detect.py) | Functions: `ingest`, `alerts` |
| [`requirements.txt`](requirements.txt) | Implementation or supporting configuration |
| [`src/analyzer/__init__.py`](src/analyzer/__init__.py) | Implementation or supporting configuration |
| [`tests/test_analyzer.py`](tests/test_analyzer.py) | Executable checks and regression examples |
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | GitHub Actions job definitions |
| [`README.md`](README.md) | Project explanations or operating notes |

### Local setup and verification

From the repository root (the commands follow the checked-in manifests):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

To serve the FastAPI application locally, install the server separately if it is not already available:

```bash
python -m pip install uvicorn
PYTHONPATH=src python -m uvicorn analyzer.main:app --reload
```

<!-- project-guide:end -->

Phase 1

Skills: Python, Linux snapshots, FastAPI, regex

CPU, memory, disk plus application logs → anomaly flags → REST. Nothing is paged.

```bash
pip install -r requirements.txt
pytest -q
```

Laptop proof. No hosted model. Cluster apply stays false until a human approves.

## Ops plane

Workspaces, tenant isolation, job approval, and audit live under `/v1`. Production apply is refused. See `docs/ARCHITECTURE.md`.
