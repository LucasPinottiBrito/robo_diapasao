from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import cv2
from PIL import Image, ImageTk
import threading
import time
from config import CONFIG
from db.doctor_repo import DoctorRepository
from db.patient_repo import PatientRepository
from db.triage_repo import TriageRepository
from triage_session import TriageSession
from ui_doctors import DoctorUI


class UI:
    def __init__(self, face_detector=None, voice_recorder=None, network_client=None, triage_manager=None):
        self.face_detector = face_detector
        self.voice_recorder = voice_recorder
        self.network_client = network_client
        self.triage_manager = triage_manager

        self.root = tk.Tk()
        self.root.title("Triage Robot")

        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        menu_bar.add_command(label="Médicos", command=self.open_doctors)
        
        # Status
        self.status_var = tk.StringVar(value="Inicializando sistema...")
        tk.Label(self.root, textvariable=self.status_var, font=("Arial", 12), fg="darkred").pack(pady=5)

        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="x", padx=8)

        # Session controls
        session_frame = tk.Frame(top_frame)
        session_frame.pack(side="left", padx=8)

        tk.Button(session_frame, text="➕ Nova Triagem", command=self.create_session).pack(side="left", padx=4)
        tk.Label(top_frame, text="Sessão:").pack(side="left", padx=(10, 2))
        self.selected_session_var = tk.StringVar(value="")
        self.sessions_menu = ttk.Combobox(top_frame, textvariable=self.selected_session_var, width=30, state="readonly")
        self.sessions_menu.pack(side="left")

        tk.Label(top_frame, text="Médico:").pack(side="left", padx=(10, 2))
        self.doctor_select_var = tk.StringVar(value="")
        self.doctor_menu = ttk.Combobox(top_frame, textvariable=self.doctor_select_var, width=30, state="readonly")
        self.doctor_menu.pack(side="left")

        self.refresh_sessions_menu()
        self.refresh_doctor_menu()

        # bind event when doctor list changes
        self.root.bind("<<DOCTOR_UPDATED>>", lambda e: self.refresh_doctor_menu())

        # Camera panel
        self.camera_label = tk.Label(self.root)
        self.camera_label.pack(pady=6)

        # Control buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=6)

        self.start_btn = tk.Button(btn_frame, text="🎙️ Iniciar Gravação", font=("Arial", 12, "bold"),
                                   command=self.start_recording)
        self.start_btn.pack(side="left", padx=10)

        self.stop_btn = tk.Button(btn_frame, text="🛑 Parar Gravação", font=("Arial", 12, "bold"),
                                  command=self.stop_recording)
        self.stop_btn.pack(side="left", padx=10)
        self.stop_btn.config(state="disabled")

        # AI response box
        self.response_box = ScrolledText(self.root, width=80, height=14, font=("Arial", 10))
        self.response_box.pack(padx=10, pady=8)

        # OpenCV Camera
        self.cap = cv2.VideoCapture(CONFIG.CAMERA_INDEX)
        self.running = True
        self.recording = False
        self.face_present = False
        self.face_timeout = False
        self.last_face_seen = None

        # Thread camera update
        threading.Thread(target=self.update_camera_loop, daemon=True).start()

        self.root.protocol("WM_DELETE_WINDOW", self.close)

        # refresh sessions dropdown initially
        self.refresh_sessions_menu()

    def open_doctors(self):
            DoctorUI(self.root)

    def refresh_sessions_menu(self):
        values = [s[0] for s in self.triage_manager.list_sessions()]
        self.sessions_menu["values"] = values
        if values:
            self.selected_session_var.set(values[-1])

    def refresh_doctor_menu(self):
        docs = DoctorRepository().list()
        labels = [f"{d['id']} – {d['name']}" for d in docs]
        self.doctor_menu["values"] = labels
        if labels:
            self.doctor_select_var.set(labels[0])
     
    # --- Session management ---
    def create_session(self):
        session = self.triage_manager.create_session()
        self.refresh_sessions_menu()
        self.selected_session_var.set(session.id)
        self.set_status(f"🆕 Nova triagem criada: {session.id}")
        self.response_box.insert(tk.END, f"\n[SESSION CREATED] {session.id}\n")
    
    def get_selected_doctor_id(self):
        val = self.doctor_select_var.get()
        if not val:
            return None
        return int(val.split("–")[0].strip())
    
    def refresh_sessions_menu(self):
        values = [s[0] for s in self.triage_manager.list_sessions()]
        self.sessions_menu["values"] = values
        if values:
            self.selected_session_var.set(values[-1])

    def get_current_session(self):
        sid = self.selected_session_var.get()
        if not sid:
            return None
        return self.triage_manager.get_session(sid)

    # --- CAMERA ---
    def update_camera_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.05)
                continue

            # Face detection
            if self.face_detector:
                faces = self.face_detector.detect(frame)

                if len(faces) > 0:
                    self.face_present = True
                    self.last_face_seen = time.time()
                else:
                    if self.last_face_seen:
                        if (time.time() - self.last_face_seen) > CONFIG.FACE_DETECTION_TIMEOUT:
                            self.face_timeout = True

                # Draw face on frame
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Update UI status
                if self.face_timeout:
                    self.status_var.set("⚠️ Rosto ausente. Encerrando triagem...")
                elif not self.recording:
                    self.status_var.set("👤 Rosto detectado! Selecione/Crie uma triagem.")
                elif self.recording:
                    self.status_var.set("🎙️ Gravando sintomas...")

            # Convert frame for tkinter
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img_tk = ImageTk.PhotoImage(img)

            # update UI safely
            try:
                self.camera_label.config(image=img_tk)
                self.camera_label.image = img_tk
            except tk.TclError:
                # window closed
                break

            time.sleep(0.03)

            if self.face_timeout and not self.recording:
                time.sleep(1)
                self.close()

    # --- UI ACTIONS ---
    def start_recording(self):
        if not self.voice_recorder:
            self.set_status("❌ Gravador não inicializado.")
            return

        session = self.get_current_session()
        if session is None:
            self.set_status("❗ Selecione ou crie uma triagem primeiro.")
            return

        self.response_box.insert(tk.END, f"\n🎙️ Iniciando gravação para sessão {session.id} …\n")
        self.recording = True
        self.voice_recorder.start()

        session.set_audio_path(self.voice_recorder.filename)

        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.set_status("🎙️ Gravando...")

    def stop_recording(self):
        if not self.voice_recorder:
            return

        session = self.get_current_session()
        if session is None:
            self.set_status("❗ Selecione uma triagem antes de parar.")
            return

        self.recording = False
        self.stop_btn.config(state="disabled")
        self.start_btn.config(state="normal")

        filepath = self.voice_recorder.stop()
        session.set_audio_path(filepath)
        self.response_box.insert(tk.END, f"🛑 Gravação finalizada e salva em {filepath}\n")
        self.set_status("⏳ Enviando áudio para IA…")

        # envia requisição e aguarda resposta em thread separada
        threading.Thread(target=self._dispatch_audio_and_handle_response, args=(session,), daemon=True).start()

    def _dispatch_audio_and_handle_response(self, session: TriageSession):
        try:
            response_json = self.network_client.send_audio(session.meta["audio_path"], session.id)
        except Exception as e:
            self.response_box.insert(tk.END, f"\n❌ Erro no envio ao agente: {e}\n")
            self.set_status("❌ Falha no envio")
            return

        
        ai_resp = response_json

        # save raw ai response to session filesystem
        session.save_json(ai_resp)

        status = ai_resp.get("status")
        record = ai_resp.get("record")
        msg = ai_resp.get("message")
        patient_summary = record.get("summary") if record else None
        patient = record.get("patient") if record else None
        doctor_id = self.get_selected_doctor_id()
        self.response_box.insert(tk.END, f"\n🤖 IA diz: {msg}\n")
        self.set_status("✅ Resposta recebida")

        if status == "finished":
            pdf_path = session.save_pdf(patient_summary)
            ai_resp.setdefault("record", {}).setdefault("triage", {})["path_pdf"] = pdf_path
            session.save_json(ai_resp) 

            try:
                patient_repo = PatientRepository()
                patient_id = patient_repo.create(
                    name=patient.get("name", "Desconhecido"),
                    cpf=patient.get("cpf", "000.000.000-00"),
                    date_of_birth=patient.get("date_of_birth")
                )
                self.response_box.insert(tk.END, f"\n💾 Paciente salvo no banco. ID={patient_id}\n")
                
                triage = TriageRepository()
                triage_id = triage.create(
                    session.id, 
                    datetime.now().isoformat(), 
                    path=session.path, 
                    patient_id=patient_id,
                    doctor_id=doctor_id
                )

                self.response_box.insert(tk.END, f"\n💾 Triagem finalizada e salva no banco. ID={triage_id}\n")
            
            except Exception as e:
                self.response_box.insert(tk.END, f"\n❌ Erro ao salvar no banco: {e}\n")

            self.triage_manager.finish_session(session.id)
            self.refresh_sessions_menu()
            self.set_status("🏁 Triagem finalizada.")
        else:
            self.set_status("🔁 Triagem pendente - IA solicitou follow-up.")

    def show_ai_response(self, response_text):
        self.response_box.insert(tk.END, f"\n🤖 Resposta da IA:\n{response_text}\n")

    def set_status(self, text):
        try:
            self.status_var.set(text)
        except tk.TclError:
            pass

    def close(self):
        self.running = False
        try:
            self.cap.release()
        except Exception:
            pass
        try:
            self.root.destroy()
        except Exception:
            pass

    def run(self):
        self.root.mainloop()
