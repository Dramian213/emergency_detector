import sounddevice as sd
import numpy as np
import librosa
import pickle

class SirenDetector:
    def __init__(self, fusion, sample_rate=22050, duration=1.0):
        self.fusion = fusion
        self.sr = sample_rate
        self.duration = duration
        self.model = pickle.load(open("audio/models/siren_model.pkl", "rb"))

    def extract_features(self, audio):
        mfcc = librosa.feature.mfcc(y=audio, sr=self.sr, n_mfcc=13)
        return np.mean(mfcc, axis=1)

    def run(self):
        print("Audio: nasłuchuję...")
        while True:
            audio = sd.rec(
                int(self.duration * self.sr),
                samplerate=self.sr, channels=1, dtype='float32'
            )
            sd.wait()
            features = self.extract_features(audio.flatten())
            prediction = self.model.predict([features])[0]
            self.fusion.update_audio(bool(prediction))