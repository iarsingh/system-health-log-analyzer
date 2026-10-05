# system-health-log-analyzer — interview questions and answers

[README](README.md) · [Project architecture](PROJECT_ARCHITECTURE.md)

Answers below use this repository’s files and implementation. They distinguish existing behavior from suggested extensions; source links let you verify each walkthrough.

## 1. What problem does system-health-log-analyzer address, and what can you demonstrate?

CPU, memory, disk plus application logs → anomaly flags → REST. Nothing is paged.

I would demonstrate the linked implementation or examples and distinguish that evidence from any planned production features. Start with [`README.md`](README.md).

## 2. How is this repository organized?

- [`src/analyzer/main.py`](src/analyzer/main.py): Implementation or supporting configuration.
- [`src/analyzer/detect.py`](src/analyzer/detect.py): Implementation or supporting configuration.
- [`requirements.txt`](requirements.txt): Implementation or supporting configuration.
- [`src/analyzer/__init__.py`](src/analyzer/__init__.py): Implementation or supporting configuration.
- [`tests/test_analyzer.py`](tests/test_analyzer.py): Executable checks and regression examples.
- [`.github/workflows/ci.yml`](.github/workflows/ci.yml): GitHub Actions job definitions.
- [`README.md`](README.md): Project explanations or operating notes.

[PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md) contains the component diagram and the implementation walkthrough.

## 3. Can you walk through `ingest` and explain the decision it makes?

The main walkthrough here is `ingest(snapshot, logs)` in [`src/analyzer/detect.py`](src/analyzer/detect.py#L9).

```python
def ingest(snapshot, logs):
    if not isinstance(snapshot, dict):
        raise InputError("snapshot required")
    alerts = []
    for key in ("cpu_percent", "memory_percent", "disk_percent"):
        value = snapshot.get(key)
        if value is None:
            continue
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 100:
            raise InputError(f"{key} must be 0-100")
        if value >= 90:
            alerts.append({"kind": key, "level": "critical", "value": value})
        elif value >= 80:
            alerts.append({"kind": key, "level": "warn", "value": value})
    hits = []
    for i, line in enumerate(logs or []):
        if isinstance(line, str) and ERROR_RE.search(line):
            hits.append({"line": i, "text": line[:240]})
    if len(hits) >= 3:
        alerts.append({"kind": "log_burst", "level": "warn", "value": len(hits)})
```

This is an excerpt; follow the source link for the rest of the branches.

The implementation calls `ERROR_RE.search`, `HISTORY.append`, `InputError`, `alerts.append`, `enumerate`, `hits.append`, `isinstance`, `len`, `snapshot.get`. In an interview, trace those calls in execution order using a fixture input.

## 4. What responsibility does `alerts` have?

`alerts()` is defined in [`src/analyzer/detect.py`](src/analyzer/detect.py#L33).

Its return expressions include:

- `{'alerts': [a for rec in HISTORY for a in rec['alerts']], 'samples': len(HISTORY), 'paged': False}`

It uses `len`. This is the code path I would compare against the caller to explain responsibility boundaries.

## 5. What input validation and failure behavior are implemented?

Explicit failure paths include:

- `InputError('snapshot required')` in [`src/analyzer/detect.py`](src/analyzer/detect.py#L11).
- `InputError(f'{key} must be 0-100')` in [`src/analyzer/detect.py`](src/analyzer/detect.py#L18).
- `HTTPException(status_code=422, detail=str(exc))` in [`src/analyzer/main.py`](src/analyzer/main.py#L14).

I would test both the condition that reaches each exception and the caller that translates it. An explicit raise does not mean every malformed input or dependency failure is handled.

## 6. Which test would you use to demonstrate correctness?

[`tests/test_analyzer.py`](tests/test_analyzer.py#L9) contains `test_cpu_and_log_burst`:

```python
def test_cpu_and_log_burst():
    payload = client.post("/ingest", json={"snapshot": {"cpu_percent": 95, "memory_percent": 10, "disk_percent": 10}, "logs": ["ERROR timeout", "exception", "panic"]}).json()
    assert {a["kind"] for a in payload["alerts"]} >= {"cpu_percent", "log_burst"}
    assert payload["paged"] is False
```

This is a concrete regression example from the repository. Its assertions establish that case; they do not establish behavior for every input or under production load.

## 7. What HTTP interface does the code expose?

- `GET /healthz` → `healthz` in [`src/analyzer/main.py`](src/analyzer/main.py#L6).
- `POST /ingest` → `post_ingest` in [`src/analyzer/main.py`](src/analyzer/main.py#L10).
- `GET /alerts` → `get_alerts` in [`src/analyzer/main.py`](src/analyzer/main.py#L17).

These are literal decorators. Application/router prefixes, authentication, and middleware must be checked in the corresponding setup code.

## 8. How would you investigate data ownership and persistence?

Trace the data/configuration files and the code that reads or writes them in the component table. Identify which files are examples, which records are mutable, and which external store is actually configured. I would document those facts before discussing retention, backup, or tenant isolation.

## 9. How would another engineer reproduce your walkthrough?

Start from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

These commands follow repository manifests; environment setup and command results still need to be checked on the target machine.

## 10. What does automation verify, and what does it not prove?

Inspect [`.github/workflows/ci.yml`](.github/workflows/ci.yml) for triggers, permissions, and job commands. I would name the checks that those definitions run and show the latest run separately. A workflow definition alone does not establish a successful deployment, security review, or production SLO.

## 11. How would you present this project in a Forward Deployed Engineer interview?

Start with the user and operational problem described in [`README.md`](README.md). Explain one constraint that changes the implementation, show the linked code or example, and walk through a success case and a failure case. Agree on a measurable acceptance criterion before expanding the solution, and leave a handoff with data boundaries and rollback ownership. Any proposed production or business metric should be identified as a target until measured.

## 12. What is the input-to-output contract of `ingest`?

In [`src/analyzer/detect.py`](src/analyzer/detect.py#L9), `ingest(snapshot, logs)` receives the inputs. The function computes these intermediate values:

- `alerts = []`
- `hits = []`
- `rec = {'alerts': alerts, 'log_hits': hits, 'paged': False}`

Its result is defined by:

- `rec`

## 13. Which decision rules or boundary conditions should an interviewer challenge?

The implementation in [`src/analyzer/detect.py`](src/analyzer/detect.py#L9) branches on:

- `not isinstance(snapshot, dict)`
- `len(hits) >= 3`
- `value is None`
- `not isinstance(value, (int, float)) or isinstance(value, bool) or (not 0 <= value <= 100)`
- `value >= 90`
- `isinstance(line, str) and ERROR_RE.search(line)`
- `value >= 80`

A useful extension is a table-driven test that covers each condition just below, at, and above its boundary where applicable. These expressions are the current rules; changing them changes behavior and should be justified by the project’s acceptance criteria.
