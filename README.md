# Emergency Detector

[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)

Emergency Vehicle Detector to inteligentny system przeznaczony do rozpoznawania pojazdów uprzywilejowanych w czasie rzeczywistym z wykorzystaniem technologii widzenia komputerowego. System łączy dwa sposoby wykrywania za pomocą logiki fuzyjnej, aby zapewnić niezawodną identyfikację pojazdów uprzywilejowanych.

## Opis
- Moduł wizji wykorzystuje modele YOLO do detekcji obiektów na obrazach/strumieniu wideo.
- Moduł audio analizuje nagrania/dźwięk w celu wykrycia sygnałów alarmowych (np. syrena) przy użyciu wytrenowanego klasyfikatora.
- Moduł fusion łączy wyniki obu modułów i podejmuje końcową decyzję o wykryciu zdarzenia.

## Funkcje
- **Wykrywanie pojazdów w czasie rzeczywistym** - wykrywa samochody osobowe, ciężarowe, autobusy i pojazdy uprzywilejowane
- **Klasyfikacja pojazdów uprzywilejowanych** - w szczególności identyfikuje pojazdy uprzywilejowane spośród innych typów pojazdów
- **Analiza transmisji z kamery na żywo** - przetwarza strumień wideo z kamery internetowej lub urządzenia fotograficznego
- **Nakładka wizualna** – wyświetla ramki ograniczające i wyniki pewności wykrytych pojazdów
- **Sensor Fusion Framework** – infrastruktura do łączenia wielu modalności detekcji
- **Monitorowanie stanu** – informacje zwrotne od konsoli w czasie rzeczywistym na temat stanu wykrycia

## Zwracane informacje
- Konsola:
  - Aktualizacje statusu wykrywania
  - Alerty dotyczące pojazdów uprzywilejowanych
  - Komunikaty o wykryciu pojazdu inne niż uprzywilejowane
- Okno:
  - Transmisja z kamery na żywo z ramkami wykrywającymi pojazdy
  - Wyniki pewności wykrywania
  - Wskaźniki stanu
  - Nakładki oznaczone kolorami (zielony dla wykrycia, czerwony dla braku wykrycia)

## Wymagania
- **Python 3.11+**
- **Zależności** requirements.txt
- **GPU kopatybilne z CUDA** (opcjonalne, ale rekomandowane dla wydajności)

## Autorzy
- Tomasz Hanusek
- Damian Spodar

<a href="https://github.com/Dramian213/emergency_detector/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Dramian213/emergency_detector" />
</a>
