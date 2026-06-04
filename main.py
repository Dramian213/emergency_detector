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

    try:
        while True:
            if fusion.should_trigger():
                print("🚨 POJAZD UPRZYWILEJOWANY WYKRYTY!")
            time.sleep(1)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()