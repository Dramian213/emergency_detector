import threading
import time
#from audio.detector import SirenDetector
from vision.detector import VehicleDetector
from fusion.logic import FusionLogic

def main():
    print("System uruchomiony. Naciśnij 'q' w oknie detekcji, aby zakończyć.")
    fusion = FusionLogic(time_window=3.0)

    #siren_detector = SirenDetector(fusion=fusion)
    vehicle_detector = VehicleDetector(fusion=fusion)

    # Uruchomienie wątków równoległych
    threads = [
        #threading.Thread(target=siren_detector.run, daemon=True),
        threading.Thread(target=vehicle_detector.run, daemon=True),
    ]
    for t in threads:
        t.start()

    last_emergency_state = False
    last_any_state = False

    try:
        while True:
            current_emergency = fusion.is_emergency_active()
            current_any = fusion.is_vision_active()

            if current_emergency and not last_emergency_state:
                print("🚨 POJAZD UPRZYWILEJOWANY WYKRYTY")

            elif not current_emergency and last_emergency_state:
                if current_any:
                    print("ℹ️ INNE POJAZDY")
                else:
                    print("ℹ️ BRAK POJAZDÓW")

            elif current_any and not last_any_state:
                print("ℹ️ INNE POJAZDY")

            elif not current_any and last_any_state:
                print("ℹ️ BRAK POJAZDÓW")

            last_emergency_state = current_emergency
            last_any_state = current_any
            time.sleep(0.1)

    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()