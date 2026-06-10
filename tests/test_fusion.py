import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fusion.logic import FusionLogic


def test_poczatkowy_stan_nieaktywny():
    # Świeży obiekt nie powinien zgłaszać żadnych aktywnych sygnałów
    f = FusionLogic(time_window=3.0, confirm_frames=3)
    assert not f.is_siren_active()
    assert not f.is_vision_active()
    assert not f.is_emergency_active()
    assert not f.is_both_active()
    print("✅ test_poczatkowy_stan_nieaktywny")


def test_audio_pojedyncze_wykrycie():
    # Jedno wykrycie syreny powinno aktywować is_siren_active w oknie czasowym
    f = FusionLogic(time_window=3.0, confirm_frames=3)
    f.update_audio(True)
    assert f.is_siren_active()
    print("✅ test_audio_pojedyncze_wykrycie")


def test_audio_brak_wykrycia():
    # Sam False nie powinien aktywować syreny
    f = FusionLogic(time_window=3.0, confirm_frames=3)
    f.update_audio(False)
    f.update_audio(False)
    assert not f.is_siren_active()
    print("✅ test_audio_brak_wykrycia")


def test_audio_wygasniecie_okna():
    # Syrena powinna wygasnąć po przekroczeniu time_window
    f = FusionLogic(time_window=0.2, confirm_frames=1)
    f.update_audio(True)
    assert f.is_siren_active()
    time.sleep(0.3)
    assert not f.is_siren_active()
    print("✅ test_audio_wygasniecie_okna")


def test_vision_aktywna_po_wykryciu():
    # Wykrycie pojazdu powinno aktywować is_vision_active
    f = FusionLogic(time_window=3.0, confirm_frames=1)
    f.update_vision(True, is_emergency=False)
    assert f.is_vision_active()
    print("✅ test_vision_aktywna_po_wykryciu")


def test_vision_brak_bez_wykrycia():
    # Aam False nie aktywuje wizji
    f = FusionLogic(time_window=3.0, confirm_frames=3)
    f.update_vision(False, is_emergency=False)
    assert not f.is_vision_active()
    print("✅ test_vision_brak_bez_wykrycia")


def test_emergency_wymaga_confirm_frames():
    # is_emergency_active wymaga confirm_frames kolejnych wykryć
    f = FusionLogic(time_window=3.0, confirm_frames=3)

    # Dwa wykrycia – za mało
    f.update_vision(True, is_emergency=True)
    f.update_vision(True, is_emergency=True)
    assert not f.is_emergency_active()

    # Trzecie wykrycie – dopiero teraz potwierdzone
    f.update_vision(True, is_emergency=True)
    assert f.is_emergency_active()
    print("✅ test_emergency_wymaga_confirm_frames")


def test_emergency_reset_po_przerwie():
    # Jedna klatka False pomiędzy wykryciami resetuje confirm_frames
    f = FusionLogic(time_window=3.0, confirm_frames=3)
    f.update_vision(True, is_emergency=True)
    f.update_vision(True, is_emergency=True)
    f.update_vision(False, is_emergency=False)   # przerwa
    f.update_vision(True, is_emergency=True)
    # historia: [True, False, True] – nie wszystkie True
    assert not f.is_emergency_active()
    print("✅ test_emergency_reset_po_przerwie")


def test_both_active_wymaga_obu_sygnalow():
    # is_both_active zwraca True tylko gdy aktywne i syrena, i emergency
    f = FusionLogic(time_window=3.0, confirm_frames=1)

    # Tylko syrena
    f.update_audio(True)
    assert not f.is_both_active()

    # Tylko emergency
    f2 = FusionLogic(time_window=3.0, confirm_frames=1)
    f2.update_vision(True, is_emergency=True)
    assert not f2.is_both_active()

    # Oba
    f3 = FusionLogic(time_window=3.0, confirm_frames=1)
    f3.update_audio(True)
    f3.update_vision(True, is_emergency=True)
    assert f3.is_both_active()
    print("✅ test_both_active_wymaga_obu_sygnalow")


def test_vision_wygasniecie_okna():
    # Wizja powinna wygasnąć po przekroczeniu time_window
    f = FusionLogic(time_window=0.2, confirm_frames=1)
    f.update_vision(True, is_emergency=False)
    assert f.is_vision_active()
    time.sleep(0.3)
    assert not f.is_vision_active()
    print("✅ test_vision_wygasniecie_okna")


if __name__ == "__main__":
    test_poczatkowy_stan_nieaktywny()
    test_audio_pojedyncze_wykrycie()
    test_audio_brak_wykrycia()
    test_audio_wygasniecie_okna()
    test_vision_aktywna_po_wykryciu()
    test_vision_brak_bez_wykrycia()
    test_emergency_wymaga_confirm_frames()
    test_emergency_reset_po_przerwie()
    test_both_active_wymaga_obu_sygnalow()
    test_vision_wygasniecie_okna()
    print("\nWszystkie testy zakończone sukcesem.")