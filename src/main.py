# main.py
from face_detector import FaceDetector
from voice_recorder import VoiceRecorder
from network_client import NetworkClient
from triage_manager import TriageManager
from ui import UI
from db.config import engine
from db.models import Base

# Ensure DB tables exist
Base.metadata.create_all(engine)

# Init components
face_detector = FaceDetector()
voice_recorder = VoiceRecorder(filename="patient.wav")
network_client = NetworkClient()
triage_manager = TriageManager()

# Start UI (UI will create sessions on demand)
app_ui = UI(
    face_detector=face_detector,
    voice_recorder=voice_recorder,
    network_client=network_client,
    triage_manager=triage_manager
)

# Run app
if __name__ == "__main__":
    app_ui.run()
