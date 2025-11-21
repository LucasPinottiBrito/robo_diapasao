import cv2
from face_detector import FaceDetector
from voice_recorder import VoiceRecorder
from network_client import NetworkClient
from ui import UI
from triage_session import TriageSession


face_detector = FaceDetector()
ui = UI()
recorder = VoiceRecorder(filename="patient.wav")  # usa nova classe contínua
network = NetworkClient()
session = TriageSession()

cap = cv2.VideoCapture(0)
spoken = False


print("Inicializando sistema de triagem...")

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    faces = face_detector.detect(frame)

    # Primeira fala ao detectar rosto
    if len(faces) > 0 and not spoken:
        print("Olá! Eu sou o assistente de triagem.")
        spoken = True

    # Se já cumprimentou e ainda há rosto
    if spoken and len(faces) > 0:
        print("Pressione 'r' para iniciar gravação e 's' para encerrar.")

    # Leitura de teclas
    key = cv2.waitKey(1)

    # Inicia gravação contínua
    if key == ord('r'):
        if not recorder.is_recording:
            print("🎙️ Iniciando gravação...")
            recorder.start()
        else:
            print("⚠️ Já está gravando!")

    # Encerra gravação e envia
    elif key == ord('s'):
        if recorder.is_recording:
            print("🛑 Parando gravação...")
            filepath = recorder.stop()
            print(f"Áudio salvo em: {filepath}")

            print("📡 Enviando áudio para IA...")
            response = network.send_audio(filepath)

            session.save({
                "audio_sent": filepath,
                "response": response.text
            })

            print("Resposta salva na sessão.")

        else:
            print("⚠️ Nenhuma gravação ativa.")

    # Se a face sumir por tempo
    if face_detector.face_timed_out():
        print("Face ausente. Encerrando triagem.")
        break

    # Mostra o frame na UI
    ui.show_frame(frame)
    
cap.release()
cv2.destroyAllWindows()
