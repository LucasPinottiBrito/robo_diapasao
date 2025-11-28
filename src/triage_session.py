# triage_session.py
import os
import json
import uuid
from config import CONFIG
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


class TriageSession:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.path = os.path.join(CONFIG.DATA_DIR, self.id)
        os.makedirs(self.path, exist_ok=True)

        self.meta = {
            "id": self.id,
            "audio_path": None,
            "ai_response": None
        }

    def save_json(self, data, filename="triage.json"):
        with open(os.path.join(self.path, filename), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        self.meta["ai_response"] = data

    def set_audio_path(self, audio_path):
        self.meta["audio_path"] = audio_path

    def save_pdf(self, text: str, filename="triage.pdf"):
        pdf_path = os.path.join(self.path, filename)
        # create a simple PDF with ReportLab
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4
        margin = 40
        y = height - margin
        line_height = 14

        # Title
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margin, y, "Prontuário de Triagem")
        y -= 2 * line_height

        c.setFont("Helvetica", 10)
        # split text into lines that fit the page
        max_chars = 100  # rough wrap
        paragraphs = text.split("\n")
        for para in paragraphs:
            if not para:
                y -= line_height
                continue
            while len(para) > 0:
                chunk = para[:max_chars]
                # try break on last space
                if len(para) > max_chars:
                    idx = chunk.rfind(" ")
                    if idx > 10:
                        chunk = para[:idx]
                c.drawString(margin, y, chunk)
                para = para[len(chunk):].lstrip()
                y -= line_height
                if y < margin:
                    c.showPage()
                    y = height - margin
                    c.setFont("Helvetica", 10)

        c.save()
        # update triage meta path
        self.meta.setdefault("triage", {})["path_pdf"] = pdf_path
        return pdf_path
