import requests
import numpy as np

class SentinelTelemetryAPI:
    """Pulls live ambient telemetry vectors directly from Sentinel REST API."""
    def __init__(self, base_url="http://localhost:8443"):
        self.base_url = base_url.rstrip("/")

    def fetch_live_telemetry_batch(self, limit=500):
        url = f"{self.base_url}/api/v1/system-health"
        try:
            resp = requests.get(url, timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                # Parse recent low-score baseline events
                threats = data.get("threats", [])
                low_anomalies = [t for t in threats if t.get("score", 1.0) < 0.30]
                print(f"[APICollector] Queried Sentinel API. Retrieved {len(low_anomalies)} low-anomaly records.")
                return low_anomalies
        except Exception as e:
            print(f"[APICollector Info] Sentinel REST API not accessible ({e}).")
        return []