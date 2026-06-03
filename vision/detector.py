import cv2
from ultralytics import YOLO

# Klasy COCO powiązane z pojazdami uprzywilejowanymi
VEHICLE_CLASSES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}

class VehicleDetector:
    def __init__(self, fusion, camera_index=0, conf_threshold=0.5):
        self.fusion = fusion
        self.conf_threshold = conf_threshold
        self.model = YOLO("vision/models/yolov8n.pt")
        self.cap = cv2.VideoCapture(camera_index)

        if not self.cap.isOpened():
            raise RuntimeError(f"Nie można otworzyć kamery o indeksie {camera_index}")

    def run(self):
        print("Vision: analizuję obraz")
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                print("Nie udało się pobrać klatki z kamery.")
                break

            results = self.model(frame, verbose=False)[0]
            detected = False

            for box in results.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])

                if cls_id in VEHICLE_CLASSES and conf >= self.conf_threshold:
                    detected = True
                    # Rysuj bbox
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    label = f"{VEHICLE_CLASSES[cls_id]} {conf:.2f}"

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(
                        frame,
                        label,
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 0),
                        2
                    )

            self.fusion.update_vision(detected)

            status_text = "POJAZD WYKRYTY" if detected else "BRAK POJAZDU"
            color = (0, 255, 0) if detected else (0, 0, 255)
            cv2.putText(
                frame,
                status_text,
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                color,
                2
            )

            cv2.imshow("Detekcja", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Zakończono detekcję.")
                break

        self.cap.release()
        cv2.destroyAllWindows()