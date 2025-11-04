import os
import json
import uuid
from config import CONFIG


class TriageSession:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.path = os.path.join(CONFIG.DATA_DIR, self.id)
        os.makedirs(self.path, exist_ok=True)

    
    def save(self, data):
        with open(os.path.join(self.path, "triage.json"), "w") as f:
            json.dump(data, f, indent=4)