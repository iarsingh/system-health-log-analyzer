from fastapi.testclient import TestClient
from analyzer import detect
from analyzer.main import app
client = TestClient(app)

def setup_function():
    detect.HISTORY.clear()

def test_cpu_and_log_burst():
    payload = client.post("/ingest", json={"snapshot": {"cpu_percent": 95, "memory_percent": 10, "disk_percent": 10}, "logs": ["ERROR timeout", "exception", "panic"]}).json()
    assert {a["kind"] for a in payload["alerts"]} >= {"cpu_percent", "log_burst"}
    assert payload["paged"] is False

def test_bad_percent():
    assert client.post("/ingest", json={"snapshot": {"cpu_percent": 140}}).status_code == 422
