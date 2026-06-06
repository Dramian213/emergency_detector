import cv2
from ultralytics import YOLO

VEHICLE_CLASSES = {
    0: "emergency",
    1: "car",
    2: "truck",
    3: "bus",
}

class VehicleDetector:
    def __init__(self, fusion, camera_index=0, conf_threshold=0.5, emergency_conf_threshold=0.8, min_box_area_ratio=0.01, confirm_frames=3):
        self.fusion = fusion
        self.conf_threshold = conf_threshold
        self.emergency_conf_threshold = emergency_conf_threshold
        self.min_box_area_ratio = min_box_area_ratio
        self.confirm_frames = confirm_frames

        self.model = YOLO("vision/models/emergency_final.pt")
        self.cap = cv2.VideoCapture(camera_index)

        self._recent_emergency = []

        if not self.cap.isOpened():
            raise RuntimeError(f"Nie można otworzyć kamery o indeksie {camera_index}")

    def _box_area_ratio(self, xyxy, frame_shape):
        x1, y1, x2, y2 = xyxy
        h, w = frame_shape[:2]
        box_area = max(0, x2 - x1) * max(0, y2 - y1)
        frame_area = float(h * w)
        return box_area / frame_area if frame_area > 0 else 0.0

    def _update_emergency_history(self, value: bool):
        self._recent_emergency.append(bool(value))
        if len(self._recent_emergency) > self.confirm_frames:
            self._recent_emergency.pop(0)

    def _confirmed_emergency(self):
        return len(self._recent_emergency) == self.confirm_frames and all(self._recent_emergency)

    def run(self):
        print("Vision: analizuję obraz")
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                print("Nie udało się pobrać klatki z kamery.")
                break

            results = self.model(frame, verbose=False)[0]
            detected = False
            emergency = False

            for box in results.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])

                if cls_id not in VEHICLE_CLASSES:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                area_ratio = self._box_area_ratio((x1, y1, x2, y2), frame.shape)

                if cls_id == 0:
                    if conf >= self.emergency_conf_threshold and area_ratio >= self.min_box_area_ratio:
                        emergency = True
                        detected = True

                        label = f"{VEHICLE_CLASSES[cls_id]} {conf:.2f}"
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(
                            frame,
                            label,
                            (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0, 255, 0),
                            2,
                        )
                else:
                    if conf >= self.conf_threshold and area_ratio >= self.min_box_area_ratio:
                        detected = True

                        label = f"{VEHICLE_CLASSES[cls_id]} {conf:.2f}"
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        cv2.putText(
                            frame,
                            label,
                            (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0, 255, 0),
                            2,
                        )

            self._update_emergency_history(emergency)
            confirmed_emergency = self._confirmed_emergency()

            self.fusion.update_vision(detected, is_emergency=confirmed_emergency)

            status_text = "POJAZD WYKRYTY" if detected else "BRAK POJAZDU"
            color = (0, 255, 0) if detected else (0, 0, 255)
            cv2.putText(
                frame,
                status_text,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                color,
                2
            )

            right_text = "UPRZYWILEJOWANY"
            right_color = (0, 255, 0) if emergency else (0, 0, 255)
            cv2.putText(
                frame,
                right_text,
                (frame.shape[1] - 300, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                right_color,
                2
            )

            cv2.imshow("Detekcja", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("Zakończono detekcję.")
                break
            if cv2.getWindowProperty("Detekcja", cv2.WND_PROP_VISIBLE) < 1:
                print("Zamknięto okno detekcji.")
                break

        self.cap.release()
        cv2.destroyAllWindows()