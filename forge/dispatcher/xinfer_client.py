import requests
import json

class xInferDispatcher:
    def __init__(self, sentinel_api_url):
        self.api_url = sentinel_api_url

    def trigger_hot_reload(self, onnx_model_path):
        url = f"{self.api_url}/api/v1/control/reload-model"
        payload = {"model_path": onnx_model_path}

        print(f"[Dispatcher] Triggering zero-downtime hot-reload at {url} ...")
        try:
            resp = requests.post(url, json=payload, timeout=3)
            if resp.status_code == 200:
                print(f"[Dispatcher] Sentinel successfully hot-reloaded model: {onnx_model_path}!")
                return True
            else:
                print(f"[Dispatcher Warning] Sentinel returned HTTP {resp.status_code}. (Daemon may be paused).")
                return False
        except Exception as e:
            print(f"[Dispatcher Info] Could not reach Sentinel API ({e}). Model is saved to disk for next boot.")
            return False