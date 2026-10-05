from analyzer.progression import collect

def test_collect_flags_hot_cpu():
    out = collect({"cpu_percent": 95, "memory_percent": 10, "disk_percent": 10}, ["ok"])
    assert "cpu_percent" in out["anomalies"]
    assert out["paged"] is False

def test_collect_log_burst():
    logs = ["error a", "error b", "timeout c"]
    out = collect({"cpu_percent": 1, "memory_percent": 1, "disk_percent": 1}, logs)
    assert "log_burst" in out["anomalies"]

