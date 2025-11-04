import sounddevice as sd
from scipy.io.wavfile import write


class VoiceRecorder:
    def __init__(self, filename="patient.wav", samplerate=44100):
        self.filename = filename
        self.samplerate = samplerate
        self.recording = None


    def start(self):
        self.recording = sd.rec(int(10 * self.samplerate), samplerate=self.samplerate, channels=1)


    def stop(self):
        sd.wait()
        write(self.filename, self.samplerate, self.recording)
        return self.filename