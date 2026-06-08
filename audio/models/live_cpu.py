import os
import sys
import time
import joblib
import numpy as np
import sounddevice as sd
import torch
from transformers import AutoFeatureExtractor, Wav2Vec2Model

# --- AUTOMATYCZNA ŚCIEŻKA DO MODELU ---
AKTUALNY_FOLDER = os.path.dirname(os.path.abspath(__file__))
PLIK_MODELU = os.path.join(AKTUALNY_FOLDER, "wytrenowany_wykrywacz.joblib")
MODEL_NAME = "facebook/wav2vec2-base"


def extract_features(audio, feature_extractor, model):
    """Wyciąganie cech Wav2Vec2 dla pojedynczego okna audio"""
    inputs = feature_extractor(
        audio,
        sampling_rate=16000,
        return_tensors="pt"
    )
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()


def uruchom_nasluch_live_cpu(fusion):
    """Główna funkcja wątku audio wywoływana przez main.py"""
    print("📦 [Audio AI] Ładowanie modeli do klasyfikacji online...")

    if not os.path.exists(PLIK_MODELU):
        print(f"\n❌ [Audio AI] Błąd: Brak pliku modelu pod ścieżką:\n   -> {PLIK_MODELU}")
        print("Uruchom najpierw skrypt model_train.py!")
        return

    try:
        # Ładowanie klasyfikatora i ekstraktora cech
        klasyfikator = joblib.load(PLIK_MODELU)
        feature_extractor = AutoFeatureExtractor.from_pretrained(MODEL_NAME)
        model = Wav2Vec2Model.from_pretrained(MODEL_NAME)
        model.eval()
        print("🎤 [Audio AI] NASŁUCH MIKROFONU URUCHOMIONY. Analiza środowiska co 1.0s...")
    except Exception as e:
        print(f"❌ [Audio AI] Błąd podczas inicjalizacji modeli: {e}")
        return

    # Parametry przetwarzania
    SR = 16000  # Częstotliwość próbkowania modelu Wav2Vec2
    OKNO_SEK = 3.0  # Długość okna analizy (zgodna z treningiem)
    KROK_SEK = 1.0  # Jak często odświeżamy wynik (co 1 sekundę)

    rozmiar_okna = int(SR * OKNO_SEK)
    rozmiar_kroku = int(SR * KROK_SEK)

    # Kołowy bufor audio na 3 sekundy dźwięku
    bufor_audio = np.zeros(rozmiar_okna, dtype=np.float32)

    def audio_callback(indata, frames, time_info, status):
        nonlocal bufor_audio
        if status:
            print(f"⚠️ Status karty dźwiękowej: {status}", file=sys.stderr)

        # Przesuwamy dotychczasowe dane w lewo i dopisujemy nowe próbki z mikrofonu na koniec
        bufor_audio = np.roll(bufor_audio, -frames)
        bufor_audio[-frames:] = indata[:, 0]

    try:
        # Otwarcie strumienia mikrofonu (pobieramy paczki o wielkości rozmiar_kroku)
        with sd.InputStream(samplerate=SR, channels=1, blocksize=rozmiar_kroku, callback=audio_callback):
            while True:
                # Czekamy na zapełnienie/odświeżenie kolejnego kroku czasowego
                time.sleep(KROK_SEK)

                # Pobieramy kopię bufora do analizy, żeby callback mógł swobodnie zapisywać nowe dane
                sygnal = bufor_audio.copy()

                # Zabezpieczenie przed ciszą (jeśli mikrofon nic nie zbiera, pomijamy ciężką matematykę)
                if np.max(np.abs(sygnal)) < 0.001:
                    continue

                t_start = time.time()

                # Proces klasyfikacji AI
                cechy = extract_features(sygnal, feature_extractor, model)
                predykcja = klasyfikator.predict([cechy])[0]
                prawdopodobienstwo = klasyfikator.predict_proba([cechy])[0][1]

                t_end = time.time()

                # Przekazanie flagi (True/False) do wspólnego systemu fuzji logicznej
                wykryto_syrene = bool(predykcja == 1)
                fusion.update_audio(wykryto_syrene)

                # Linia diagnostyczna w tle
                stan_txt = "🔊 SYRENA!" if wykryto_syrene else "🤫 Tło"
                sys.stdout.write(
                    f"\r💻 [Audio CPU] Status: {stan_txt} ({prawdopodobienstwo:.1%}) | Czas AI: {t_end - t_start:.2f}s ")
                sys.stdout.flush()

    except Exception as e:
        print(f"\n❌ [Audio AI] Krytyczny błąd strumienia audio: {e}")