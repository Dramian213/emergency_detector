import time
from collections import deque


class FusionLogic:
    def __init__(self, time_window=3.0, confirm_frames=3):
        self.time_window = time_window
        self.confirm_frames = confirm_frames

        # Vision
        self._vision_history = deque(maxlen=confirm_frames)
        self._emergency_history = deque(maxlen=confirm_frames)
        self._vision_detected = False
        self._emergency_detected = False
        self._last_vision_time = 0.0
        self._last_emergency_time = 0.0

        # Audio (syrena)
        self._audio_history = deque(maxlen=confirm_frames)
        self._last_audio_time = 0.0

    # --- AUDIO ---
    def update_audio(self, detected: bool):
        now = time.time()
        self._audio_history.append(bool(detected))

        if detected:
            self._last_audio_time = now

    def is_siren_active(self) -> bool:
        now = time.time()
        # Sprawdzamy czy w oknie czasowym (np. 3 sekundy) wykryto syrenę
        recent = (now - self._last_audio_time) < self.time_window

        # POPRAWKA: Wystarczy, że w ostatniej historii była chociaż JEDNA potwierdzona syrena
        # i mieści się to w czasie time_window. To eliminuje problem gubienia klatek na CPU.
        ma_sygnal_w_historii = any(self._audio_history)

        return ma_sygnal_w_historii and recent

    # --- VISION ---
    def update_vision(self, detected: bool, is_emergency: bool = False):
        now = time.time()

        self._vision_history.append(bool(detected))
        self._emergency_history.append(bool(is_emergency))

        self._vision_detected = any(self._vision_history)

        self._emergency_detected = (
                len(self._emergency_history) == self.confirm_frames
                and sum(self._emergency_history) >= self.confirm_frames
        )

        if detected:
            self._last_vision_time = now
        if is_emergency:
            self._last_emergency_time = now

    def is_vision_active(self) -> bool:
        now = time.time()
        recent = (now - self._last_vision_time) < self.time_window
        return self._vision_detected and recent

    def is_emergency_active(self) -> bool:
        now = time.time()
        recent = (now - self._last_emergency_time) < self.time_window
        return self._emergency_detected and recent

    # --- FUZJA ---
    def is_both_active(self) -> bool:
        return self.is_siren_active() and self.is_emergency_active()