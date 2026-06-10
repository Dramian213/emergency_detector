import os
import soundfile as sf

# --- KONFIGURACJA ---
AKTUALNY_FOLDER = os.path.dirname(os.path.abspath(__file__))
PLIK_SYREN = os.path.join(AKTUALNY_FOLDER, "dataset", "Uprzywilejowane.wav")
PLIK_TLA = os.path.join(AKTUALNY_FOLDER, "dataset", "Ulica_raw.wav")
DLUGOSC_SEK = 3
SAMPLE_RATE = 16000


def tnij_audio(sciezka_in, folder_out):
    if not os.path.exists(sciezka_in):
        print(f"❌ Brak pliku: {sciezka_in}")
        return
    os.makedirs(folder_out, exist_ok=True)

    data, sr = sf.read(sciezka_in)
    if len(data.shape) > 1:
        data = data[:, 0]  # Konwersja stereo do mono

    probki_na_kawalek = DLUGOSC_SEK * SAMPLE_RATE
    ilosc = len(data) // probki_na_kawalek

    print(f"Tnę {sciezka_in} na {ilosc} części po {DLUGOSC_SEK}s...")
    for i in range(ilosc):
        start = i * probki_na_kawalek
        kawalek = data[start:start + probki_na_kawalek]
        sf.write(os.path.join(folder_out, f"chunk_{i:03d}.wav"), kawalek, SAMPLE_RATE)
    print(f"Zapisano w: {folder_out}")

if __name__ == "__main__":
    tnij_audio(PLIK_SYREN, os.path.join(AKTUALNY_FOLDER, "dataset", "syrena"))
    tnij_audio(PLIK_TLA, os.path.join(AKTUALNY_FOLDER, "dataset", "tlo"))