# Emergency Detector

Projekt "Emergency Detector" łączy analizę obrazu i dźwięku, aby wykrywać sygnały alarmowe (np. syreny) oraz obiekty na obrazach związane z sytuacjami awaryjnymi.

## Zwięzły opis

- Moduł wizji wykorzystuje modele YOLO do detekcji obiektów na obrazach/strumieniu wideo.
- Moduł audio analizuje nagrania/dźwięk w celu wykrycia sygnałów alarmowych (np. syrena) przy użyciu wytrenowanego klasyfikatora.
- Moduł fusion łączy wyniki obu modułów i podejmuje końcową decyzję o wykryciu zdarzenia.

## Aktualna struktura projektu (lokalna)

- audio/
  - dataset/
    - syrena/
    - tlo/
    - Ulica_raw.wav
    - Uprzywilejowane.wav
  - models/
    - wytrenowany_wykrywacz.joblib
  - ast-finetuned-audioset-10-10-0.4593.py
  - cut_audio.py
  - live_cpu.py
  - model_train.py

- fusion/
  - logic.py

- vision/
  - dataset/
    - images/
    - images_all/
    - labels/
    - labels_all/
    - data.yaml
  - models/
    - emergency_final.pt
    - emergency_yolo26n_v1.pt
    - emergency_yolo26n_v2.pt
    - emergency_yolo26s_v1.pt
    - emergency_yolo26s_v2.pt
  - detector.py

- runs/
  - detect/
    - train/
      - weights/
        - best.pt
        - last.pt
    - vision/
      - models/

- tests/
  - test_fusion.py

- main.py
- split_image_dataset.py
- yolo26n.pt
- requirements.txt
- .gitignore

> Uwaga: W repo znajdują się duże pliki wag modeli (.pt) zarówno w `vision/models`, jak i w katalogu głównym. Jeśli chcesz opublikować repo bez tych plików, zalecam dodanie ich do `.gitignore` i usunięcie z historii (np. za pomocą BFG lub git filter-repo).

## Wymagania

Zainstaluj zależności z pliku requirements.txt:

```bash
pip install -r requirements.txt
```

(Upewnij się, że używasz środowiska wirtualnego; zależności mogą obejmować torch/ultralytics, opencv, librosa, scikit-learn/joblib itd.)

## Uruchamianie i testy

- Uruchomienie głównego skryptu:

```bash
python main.py
```

- Testy jednostkowe:

```bash
pytest tests/test_fusion.py
```

- Trening modelu audio (przykład):

```bash
python audio/model_train.py
```

- Uruchomienie detektora wizyjnego (przykład):

```bash
python vision/detector.py
```

- Przygotowanie zbioru obrazów:

```bash
python split_image_dataset.py
```

## Modele i artefakty treningowe

- `vision/models/` zawiera wytrenowane modele w formacie `.pt`.
- `runs/` zawiera artefakty treningowe (obrazy batch, args.yaml, weights/best.pt i last.pt).
- `audio/models/` zawiera zapisany klasyfikator audio (`wytrenowany_wykrywacz.joblib`).

## Scenariusz użycia / architektura

1. Moduł wizji (vision/detector.py) analizuje obraz/strumień i zwraca detekcje obiektów.
2. Moduł audio analizuje próbki dźwięku i klasyfikuje, czy występuje syrena.
3. Moduł fusion (fusion/logic.py) łączy wyniki i decyduje o zgłoszeniu zdarzenia.

## Dalsze kroki i zalecenia

- Usuń duże pliki wag z repo (dodaj do .gitignore i oczyść historię) przed publikacją, aby zmniejszyć rozmiar repozytorium.
- Dodać dokumentację argumentów i interfejsów (opis `main.py`, argumentów w `vision/detector.py` i `audio/model_train.py`).
- Jeśli chcesz, mogę zaktualizować `.gitignore` i przygotować instrukcję usuwania plików z historii Git.

---

Autor: lokalna kopia projektu
