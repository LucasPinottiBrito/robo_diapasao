# triage_manager.py
from typing import Dict, Optional
from triage_session import TriageSession


class TriageManager:
    def __init__(self):
        # session_id -> TriageSession
        self.active_sessions: Dict[str, TriageSession] = {}

    def create_session(self) -> TriageSession:
        session = TriageSession()
        self.active_sessions[session.id] = session
        return session

    def list_sessions(self):
        return [(sid, s.meta) for sid, s in self.active_sessions.items()]

    def get_session(self, session_id: str) -> Optional[TriageSession]:
        return self.active_sessions.get(session_id)

    def finish_session(self, session_id: str):
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
