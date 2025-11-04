import cv2
from face_detector import FaceDetector
from voice_recorder import VoiceRecorder
from network_client import NetworkClient
from ui import UI
from triage_session import TriageSession


face_detector = FaceDetector()
ui = UI()
recorder = VoiceRecorder()
network = NetworkClient()
session = TriageSession()


cap = cv2.VideoCapture(0)
spoken = False


while True:
    ret, frame = cap.read()
    faces = face_detector.detect(frame)


    if len(faces) > 0 and not spoken:
        print("Olá! Eu sou o assistente de triagem.")
        spoken = True


    if spoken and len(faces) > 0:
        print("Pressione 'r' para iniciar gravação e 's' para encerrar.")


    key = cv2.waitKey(1)
    if key == ord('r'):
        recorder.start()
    elif key == ord('s'):
        filepath = recorder.stop()
        response = network.send_audio(filepath)
        session.save({"audio_sent": filepath, "response": response.text})


    if face_detector.face_timed_out():
        print("Face ausente. Encerrando triagem.")
        break


    ui.show_frame(frame)


cap.release()
cv2.destroyAllWindows()