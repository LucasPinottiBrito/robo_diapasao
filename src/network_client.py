import requests
from config import CONFIG


class NetworkClient:
    def send_audio(self, filepath):
        with open(filepath, 'rb') as f:
            files = {'file': f}
            response = requests.post(CONFIG.N8N_ENDPOINT, files=files)
        return response