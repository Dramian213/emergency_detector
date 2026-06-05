import time

class FusionLogic:
    def __init__(self, time_window=3.0):
        self.time_window = time_window
        #self._audio_detected = False
        self._vision_detected = False
        self._emergency_detected = False
        #self._last_audio_time = 0.0
        self._last_vision_time = 0.0

    #def update_audio(self, detected: bool):
    #    if detected:
    #        self._last_audio_time = time.time()
    #    self._audio_detected = detected

    def update_vision(self, detected: bool, is_emergency: bool):
        self._vision_detected = detected
        self._emergency_detected = is_emergency
        if detected:
            self._last_vision_time = time.time()

    def is_vision_active(self) -> bool:
        return self._vision_detected

    def is_emergency_active(self) -> bool:
        return self._emergency_detected

    def should_trigger(self) -> bool:
        now = time.time()
        #audio_recent = (now - self._last_audio_time) < self.time_window
        vision_recent = (now - self._last_vision_time) < self.time_window
        return vision_recent #and audio_recent  # AND logic