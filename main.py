import threading
import time
import sys
import os

AKTUALNY_FOLDER = os.path.dirname(os.path.abspath(__file__))
if AKTUALNY_FOLDER not in sys.path:
    sys.path.insert(0, AKTUALNY_FOLDER)

from vision.detector import VehicleDetector
from audio.live_cpu import uruchom_nasluch_live_cpu
from fusion.logic import FusionLogic


def main():
    print("========================================================")
    print("SYSTEM (WIDEO + AUDIO) URUCHOMIONY")
    print("Nasłuch mikrofonu (Wav2Vec2) i kamera działają w tle.")
    print("Naciśnij Ctrl+C w oknie konsoli, aby zakończyć.")
    print("========================================================")

    # 1. Inicjalizacja głównej logiki fuzji danych
    # time_window=3.0 oznacza, że pamiętamy zdarzenie przez 3 sekundy
    fusion = FusionLogic(time_window=3.0, confirm_frames=3)

    # 2. Inicjalizacja detektora wideo (przekazujemy obiekt fuzji)
    vehicle_detector = VehicleDetector(fusion=fusion)

    # 3. Konfiguracja wątków pobocznych (daemon=True zapewnia zamknięcie wraz z main)
    threads = [
        threading.Thread(
            target=uruchom_nasluch_live_cpu,
            args=(fusion,),
            daemon=True,
            name="Watek-Audio-Wav2Vec2"
        ),
        threading.Thread(
            target=vehicle_detector.run,
            daemon=True,
            name="Watek-Wizja-YOLO"
        ),
    ]

    # 4. Uruchomienie wątków audio i wideo
    for t in threads:
        t.start()

    last_state = None

    try:
        while True:
            # Pobieranie aktualnego stanu z fuzji danych
            siren = fusion.is_siren_active()
            vehicle = fusion.is_vision_active()
            emergency = fusion.is_emergency_active()
            both = fusion.is_both_active()

            # Maszyna stanów dla głównego komunikatu systemowego
            if both:
                state = "🔴 [ALERT] ZMIANA ŚWIATEŁ! (Syrena akustyczna + Pojazd w kadrze)"
            elif emergency:
                state = "🚨 [WIZJA ALERT] POJAZD UPRZYWILEJOWANY W POLU WIDZENIA"
            elif siren:
                state = "🔊 [AUDIO ALERT] SŁYSZĘ SYRENĘ ALARMOWĄ (Brak kontaktu wzrokowego)"
            elif vehicle:
                state = "🚗 [INFO] W kadrze znajdują się wyłącznie pojazdy cywilne"
            else:
                state = "ℹ️ [STATUS] Otoczenie czyste. Brak zagrożeń i syren"

            # Wypisujemy stan tylko wtedy, gdy uległ zmianie
            if state != last_state:
                # \r i czyszczenie linii, żeby nadpisać dynamiczny print z live_cpu.py
                sys.stdout.write("\r" + " " * 90 + "\r")
                print(state, flush=True)
                last_state = state

            # Krótki sen, żeby nie obciążać procesora
            time.sleep(0.1)

    except KeyboardInterrupt:
        sys.stdout.write("\r" + " " * 90 + "\r")
        print("\nRęczne zatrzymanie systemu.")
    finally:
        print("Wszystkie podsystemy zostały bezpiecznie zamknięte.")


if __name__ == "__main__":
    main()