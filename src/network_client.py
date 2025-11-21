import requests
from config import CONFIG
import base64

class NetworkClient:
    def send_audio(self, filepath):
        # send file audio as base64 to n8n endpoint
        audio_b64 = ""
        with open(filepath, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode("utf-8")
        payload = {"audio": audio_b64}
        response = requests.post(CONFIG.N8N_ENDPOINT, json=payload)
        return response