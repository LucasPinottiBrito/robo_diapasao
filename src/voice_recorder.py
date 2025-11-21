import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write


class VoiceRecorder:
    def __init__(self, filename="recording.wav", samplerate=44100, blocksize=1024):
        self.filename = filename
        self.samplerate = samplerate
        self.blocksize = blocksize
        self.frames = []
        self.stream = None
        self.is_recording = False

    def _callback(self, indata, frames, time, status):
        if self.is_recording:
            self.frames.append(indata.copy())

    def start(self):
        if self.is_recording:
            return

        self.frames = []
        self.is_recording = True

        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=1,
            blocksize=self.blocksize,
            callback=self._callback
        )
        self.stream.start()

    def stop(self):
        if not self.is_recording:
            return None

        self.is_recording = False
        self.stream.stop()
        self.stream.close()

        audio = np.concatenate(self.frames, axis=0)

        write(self.filename, self.samplerate, audio)
        return self.filename
