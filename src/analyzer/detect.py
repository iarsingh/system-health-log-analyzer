import re
from collections import deque
HISTORY = deque(maxlen=200)
ERROR_RE = re.compile(r"\b(error|exception|panic|oom|timeout|5\d\d)\b", re.I)

class InputError(ValueError):
    pass

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
    rec = {"alerts": alerts, "log_hits": hits, "paged": False}
    HISTORY.append(rec)
    return rec

def alerts():
    return {"alerts": [a for rec in HISTORY for a in rec["alerts"]], "samples": len(HISTORY), "paged": False}
