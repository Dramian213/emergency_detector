# Emergency Vehicle Detector

[![Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip)

Emergency Vehicle Detector to inteligentny system przeznaczony do rozpoznawania pojazdów uprzywilejowanych w czasie rzeczywistym z wykorzystaniem technologii widzenia komputerowego. System łączy dwa sposoby wykrywania za pomocą logiki fuzyjnej, aby zapewnić niezawodną identyfikację pojazdów uprzywilejowanych.

**Obecny cel:** Wykrywanie oparte na wizji przy użyciu YOLO26 przeszkolonego w zakresie modeli pojazdów uprzywilejowanych

**Planowane funkcje:** Wykrywanie syreny dźwiękowej

## Funkcje
- **Wykrywanie pojazdów w czasie rzeczywistym** - wykrywa samochody osobowe, ciężarowe, autobusy i pojazdy uprzywilejowane
- **Klasyfikacja pojazdów uprzywilejowanych** - w szczególności identyfikuje pojazdy uprzywilejowane spośród innych typów pojazdów
- **Analiza transmisji z kamery na żywo** - przetwarza strumień wideo z kamery internetowej lub urządzenia fotograficznego
- **Nakładka wizualna** – wyświetla ramki ograniczające i wyniki pewności wykrytych pojazdów
- **Sensor Fusion Framework** – podstawowa infrastruktura do łączenia wielu modalności detekcji
- **Monitorowanie stanu** – informacje zwrotne od konsoli w czasie rzeczywistym na temat stanu wykrycia

## Zwracane informacje

Aplikacja wyświetla:

  - Konsola:
    - Aktualizacje statusu wykrywania
    - Alerty dotyczące pojazdów uprzywilejowanych
    - Komunikaty o wykryciu pojazdu inne niż uprzywilejowane
  - Okno:
    - Transmisja z kamery na żywo z ramkami wykrywającymi pojazdy
    - Wyniki pewności wykrywania
    - Wskaźniki stanu
    - Nakładki oznaczone kolorami (zielony dla wykrycia, czerwony dla braku wykrycia)

## Architektura

### Vision Module (`vision/detector.py`)
- **Model**: niestandardowy model oparty na YOLO26, przeszkolony w pojazdach uprzywilejowanych
- **Wejście**: strumień wideo w czasie rzeczywistym z kamery
- **Wyjście**: wykrycia pojazdów z klasyfikacją i wynikami pewności
- **Klasy pojazdów**:
  - Klasa 0: pojazdy uprzywilejowane
  - Klasa 1: samochody
  - Klasa 2: ciężarówki
  - Klasa 3: autobusy

### Fusion Module (`fusion/logic.py`)
- **Cel**: łączy sygnały z dwóch źródeł detekcji
- **Okno czasowe**: konfigurowalne okno wykrywania (domyślnie: 3,0 sekundy)
- **Logika**: operacja AND na wykryciach wizyjnych i dźwiękowych
- **Zarządzanie stanem**: śledzi obecność pojazdów uprzywilejowanych i innych

### Audio Module (`audio/detector.py`) [Planned]
- Wykryje syreny pojazdów ratowniczych
- Integracja w rozwoju

## Wymagania

- **Python 3.11+**
- **GPU kopatybilne z CUDA** (opcjonalne, ale rekomandowane dla wydajności)

### Zależności
- `opencv-python` - wizja komputerowa
- `ultralytics` - framework YOLO26
- `torch` - głębokie uczenie
- `numpy` - obliczenia
- `sounddevice` - obsługa wejścia audio
- `librosa` - przetwarzanie dźwięku

## Autorzy
- Tomasz Hanusek
- Damian Spodar

<a href="https://github.com/Dramian213/emergency_detector/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Dramian213/emergency_detector" />
</a>
