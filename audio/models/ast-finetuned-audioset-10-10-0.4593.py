import collections
import queue
import sys
from transformers import pipeline
import numpy as np
import sounddevice as sd

# --- POPRAWIONA KONFIGURACJA ---
MODEL_NAME = "MIT/ast-finetuned-audioset-10-10-0.4593"
KLASY_ALARMOWE = ["siren", "ambulance", "police car", "fire engine", "emergency vehicle"]
PROG_PEWNOSCI = 0.02  # 2% - niski próg, złapiemy nawet cichą syrenę w tle

SAMPLE_RATE = 16000
DLUGOSC_OKNA_SEK = 4  # Model MUSI słyszeć 4 sekundy, żeby rozpoznać modulację syreny
KROK_ANALIZY_SEK = 2  # Analiza co pół sekundy – idealny kompromis dla CPU

CHUNK_SIZE = int(SAMPLE_RATE * KROK_ANALIZY_SEK)
BUFFER_SIZE = int(SAMPLE_RATE * DLUGOSC_OKNA_SEK)

audio_queue = queue.Queue()


def audio_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    audio_queue.put(indata[:, 0].copy())


def uruchom_nasluch_cpu():
    print("💻 [CPU] Inicjalizacja modelu...")

    # KLUCZOWE: Dodajemy top_k=20, żeby pipeline zwracał więcej klas, nie tylko top 5
    klasyfikator = pipeline(
        "audio-classification",
        model=MODEL_NAME,
        device="cpu",
        top_k=20
    )

    bufor_audio = collections.deque(maxlen=BUFFER_SIZE)
    bufor_audio.extend(np.zeros(BUFFER_SIZE, dtype=np.float32))

    print("\n🎤 URUCHAMIANIE MIKROFONU...")
    print("📢 Testuj, puszczając dźwięk syreny przez min. 4-5 sekund.")
    print("-" * 60)

    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        callback=audio_callback,
        blocksize=CHUNK_SIZE,
    )

    with stream:
        while True:
            try:
                nowe_dane = audio_queue.get()
                bufor_audio.extend(nowe_dane)

                audio_do_analizy = np.array(bufor_audio, dtype=np.float32)

                wyniki = klasyfikator(
                    {"raw": audio_do_analizy, "sampling_rate": SAMPLE_RATE}
                )

                wykryto_syrene = False
                najwyzszy_wynik = 0.0
                dokladna_klasa = ""

                # Przeszukujemy rozszerzoną listę top 20
                for pozycja in wyniki:
                    etykieta = pozycja["label"]
                    pewnosc = pozycja["score"]

                    if any(alarm in etykieta.lower() for alarm in KLASY_ALARMOWE):
                        wykryto_syrene = True
                        if pewnosc > najwyzszy_wynik:
                            najwyzszy_wynik = pewnosc
                            dokladna_klasa = etykieta

                if wykryto_syrene and najwyzszy_wynik >= PROG_PEWNOSCI:
                    print(f"🚨 [ALERT] -> {dokladna_klasa:<15} | Pewność: {najwyzszy_wynik:.2%}")
                else:
                    # Pokazujemy 3 pierwsze domyślne klasy, żeby widzieć pełniejszy kontekst
                    tlo_info = ", ".join([f"{r['label']} ({r['score']:.1%})" for r in wyniki[:2]])
                    print(f"🟢 [Nasłuch...] {tlo_info}")

            except KeyboardInterrupt:
                print("\n🛑 Zatrzymano.")
                break
            except Exception as e:
                print(f"❌ Błąd: {e}")
                break


if __name__ == "__main__":
    uruchom_nasluch_cpu()