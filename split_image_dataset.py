import os
import random
import shutil
from collections import defaultdict

random.seed(2026)

SRC_IMG_DIR = "vision/dataset/images_all"   # folder z wszystkimi zdjęciami (pliki .jpg/.png)
SRC_LABEL_DIR = "vision/dataset/labels_all" # folder z odpowiadającymi plikami .txt (YOLO)
DST_ROOT = "vision/dataset"                 # wynikowy katalog (dataset/images/{train,val,test}, labels/{...})

# Proporcje splitu
RATIOS = {"train": 0.6, "val": 0.2, "test": 0.2}

# Mapowanie nazw klas
CLASS_NAMES = {0: "emergency", 1: "car", 2: "truck", 3: "bus"}
NUM_CLASSES = len(CLASS_NAMES)

os.makedirs(os.path.join(DST_ROOT, "images", "train"), exist_ok=True)
os.makedirs(os.path.join(DST_ROOT, "images", "val"), exist_ok=True)
os.makedirs(os.path.join(DST_ROOT, "images", "test"), exist_ok=True)
os.makedirs(os.path.join(DST_ROOT, "labels", "train"), exist_ok=True)
os.makedirs(os.path.join(DST_ROOT, "labels", "val"), exist_ok=True)
os.makedirs(os.path.join(DST_ROOT, "labels", "test"), exist_ok=True)

# Lista obrazów
imgs = [f for f in os.listdir(SRC_IMG_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
imgs.sort()
random.shuffle(imgs)

# Dla każdego obrazu wczytaj zestaw obecnych klas
def read_classes_for_image(img_name):
    lbl_name = os.path.splitext(img_name)[0] + ".txt"
    lbl_path = os.path.join(SRC_LABEL_DIR, lbl_name)
    classes = set()
    if os.path.exists(lbl_path):
        with open(lbl_path, "r", encoding="utf-8") as fh:
            for line in fh:
                parts = line.strip().split()
                if not parts:
                    continue
                try:
                    cls = int(float(parts[0]))
                    classes.add(cls)
                except:
                    continue
    return classes

img_classes = {img: read_classes_for_image(img) for img in imgs}

# Policz ile obrazów zawiera każdą klasę
class_counts = defaultdict(int)
for s in img_classes.values():
    for c in s:
        class_counts[c] += 1

print("Liczebności klas (liczba obrazów zawierających klasę):")
for c in range(NUM_CLASSES):
    print(f"  {c} ({CLASS_NAMES.get(c, str(c))}): {class_counts.get(c,0)}")

# Oblicz docelowe liczby obrazów na split dla każdej klasy
desired = {c: {split: int(round(class_counts.get(c,0) * RATIOS[split])) for split in RATIOS} for c in range(NUM_CLASSES)}

print("\nDocelowe liczby obrazów dla splitów (dla każdej klasy):")
for c in range(NUM_CLASSES):
    print(f"  {c} {CLASS_NAMES.get(c)}: {desired[c]}")

# Inicjalizuj aktualne liczby
current = {c: {split: 0 for split in RATIOS} for c in range(NUM_CLASSES)}
assignments = {}  # img do split

# Sortuj obrazy malejąco wg liczby klas (trudniejsze przypadki najpierw)
sorted_imgs = sorted(imgs, key=lambda x: -len(img_classes[x]))

for img in sorted_imgs:
    classes = img_classes[img]
    # Deficyt dla każdego splitu - suma braków klasy (desired - current) dla klas w obrazie
    split_deficits = {}
    for split in RATIOS:
        deficit = 0
        for c in classes:
            need = desired.get(c, {}).get(split, 0)
            cur = current.get(c, {}).get(split, 0)
            deficit += max(0, need - cur)
        split_deficits[split] = deficit

    # Wybierz split z największym deficytem, jeśli wszystkie 0 => przypisz do train
    best_split = max(split_deficits, key=lambda k: (split_deficits[k], 1 if k=="train" else 0))
    assignments[img] = best_split

    # Zaktualizuj liczniki dla klas w obrazie
    for c in classes:
        current[c][best_split] += 1

# Po pierwszym przebiegu możemy mieć niewypełnione pozostałości (np. klasa bez wystarczającej liczby obrazów)
print("\nAktualne rozkłady po przydziale:")
for c in range(NUM_CLASSES):
    print(f"  {c} {CLASS_NAMES.get(c)}: {current[c]}")

# Skopiuj pliki do katalogów docelowych
for img, split in assignments.items():
    src_img = os.path.join(SRC_IMG_DIR, img)
    dst_img = os.path.join(DST_ROOT, "images", split, img)
    shutil.copy2(src_img, dst_img)

    lbl = os.path.splitext(img)[0] + ".txt"
    src_lbl = os.path.join(SRC_LABEL_DIR, lbl)
    dst_lbl = os.path.join(DST_ROOT, "labels", split, lbl)
    if os.path.exists(src_lbl):
        shutil.copy2(src_lbl, dst_lbl)
    else:
        # jeśli brak pliku label, utwórz pusty plik
        open(dst_lbl, "w", encoding="utf-8").close()

print("\nKopiowanie zakończone. Podsumowanie liczebności:")
for split in RATIOS:
    n_imgs = len(os.listdir(os.path.join(DST_ROOT, "images", split)))
    print(f"  {split}: {n_imgs} obrazów")