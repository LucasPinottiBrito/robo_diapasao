# network_client.py
import requests
from config import CONFIG
import base64
from typing import Any, Dict

class NetworkClient:
    def send_audio(self, filepath: str, session_id: str) -> Dict[str, Any]:
        with open(filepath, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode("utf-8")

        payload = {
            "audio": audio_b64,
            "session_id": session_id
        }

        resp = requests.post(CONFIG.N8N_ENDPOINT, json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json()
