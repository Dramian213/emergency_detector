import os
import glob
import time
import joblib
import numpy as np
import soundfile as sf
import torch
from transformers import AutoFeatureExtractor, Wav2Vec2Model
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

MODEL_NAME = "facebook/wav2vec2-base"

AKTUALNY_FOLDER = os.path.dirname(os.path.abspath(__file__))
FOLDER_SYREN = os.path.join(AKTUALNY_FOLDER, "dataset", "syrena")
FOLDER_TLA = os.path.join(AKTUALNY_FOLDER, "dataset", "tlo")
DOCELOWY_PLIK_MODELU = os.path.join(AKTUALNY_FOLDER, "models", "wytrenowany_wykrywacz.joblib")

print("📦 [Trening] Ładowanie modelu Wav2Vec2...")
feature_extractor = AutoFeatureExtractor.from_pretrained(MODEL_NAME)
model = Wav2Vec2Model.from_pretrained(MODEL_NAME)
model.eval()

def extract_features(audio):
    inputs = feature_extractor(
        audio,
        sampling_rate=16000,
        return_tensors="pt"
    )
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()


def trenuj_system_cpu():
    print("💻 Inicjalizacja ekstraktora cech Wav2Vec2 na CPU...")

    # Słownik kategorii korzysta teraz bezpośrednio ze zmiennych globalnych
    kategorie = {FOLDER_SYREN: 1, FOLDER_TLA: 0}

    X = []
    y = []

    print("🧠 Wyciąganie cech matematycznych z plików...")
    start_time = time.time()

    for folder, etykieta in kategorie.items():
        pliki = glob.glob(os.path.join(folder, "*.wav"))
        print(f" -> Przetwarzanie {len(pliki)} plików z folderu: {folder}...")

        for sciezka in pliki:
            try:
                data, sr = sf.read(sciezka)
                cechy_wektor = extract_features(data)

                X.append(cechy_wektor)
                y.append(etykieta)
            except Exception as e:
                print(f"⚠️ Pomijam uszkodzony plik {sciezka}: {e}")

    if len(X) == 0:
        print("❌ Błąd: Nie znaleziono żadnych plików .wav!")
        print(f"Upewnij się, że pliki .wav znajdują się w:\n 1. {FOLDER_SYREN}\n 2. {FOLDER_TLA}")
        return

    X = np.array(X)
    y = np.array(y)

    print(f"⚡ CPU zakończyło pracę w {time.time() - start_time:.2f}s! Mamy {X.shape[0]} próbek w bazie.")

    # Podział na zbiór treningowy i testowy
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print("🌲 Trening klasyfikatora Random Forest...")
    klasyfikator = RandomForestClassifier(n_estimators=100, random_state=42)
    klasyfikator.fit(X_train, y_train)

    skutecznosc = klasyfikator.score(X_test, y_test)
    print(f"\n🎯 SKUTECZNOŚĆ MODELU NA ZBIORZE TESTOWYM: {skutecznosc:.2%}")

    # Zapis klasyfikatora w tym samym folderze co skrypt
    joblib.dump(klasyfikator, DOCELOWY_PLIK_MODELU)
    print(f"💾 Model pomyślnie zapisany w lokalizacji:\n   -> {DOCELOWY_PLIK_MODELU}")


if __name__ == "__main__":
    trenuj_system_cpu()