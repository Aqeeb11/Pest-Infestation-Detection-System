import os
from pathlib import Path

PARENT_DIR = Path(__file__).resolve().parents[2]

DATASETS = {
    "pest": {
        "root": PARENT_DIR / "dataset" / "raw" / "pest",
        "classes": [
            "Viteus_vitifoliae",
            "Colomerus_vitis",
            "Brevipalpus_lewisi",
            "Oides_decempunctata",
            "Polyphagotarsonemus_latus",
            "Pseudococcus_comstocki",
            "Parathrene_regalis",
            "Ampelophaga",
            "Lycorma_delicatula",
            "Xylotrechus",
            "Cicadella_viridis",
            "Miridae",
            "Trialeurodes_vaporariorum",
            "Erythroneura_apicalis",
            "Papilio_xuthus",
            "Panonchus_citri",
            "Phyllocoptes_oleiverus",
        ],
        "expected_totals": {"train": 10060, "val": 1675, "test": 5041},
    },
    "disease": {
        "root": PARENT_DIR
        / "dataset"
        / "raw"
        / "disease"
        / "Grapevine Leaf Variety & Disease Dataset (GLVD)"
        / "Grapevine Leaf Variety & Disease Dataset (GLVD)"
        / "Diseases",
        "classes": [
            "Bacterial Rot",
            "Black Measles",
            "Black Rot",
            "Downy Mildew",
            "Healthy Leaves",
            "Leaf Blight",
            "Powdery Mildew",
        ],
        "expected_totals": {"train": 3470, "val": 428, "test": 428},
    },
}

IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "bmp", "gif", "tif", "tiff"}


def is_image_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower().lstrip(".") in IMAGE_EXTENSIONS


def verify_dataset(name: str, dataset: dict):
    root = dataset["root"]
    expected_classes = set(dataset["classes"])
    expected_splits = {"train", "val", "test"}

    print(f"\nVerifying dataset: {name}")
    print(f"Root: {root}")

    missing_splits = []
    actual_splits = []
    for split in expected_splits:
        split_dir = root / split
        if not split_dir.exists() or not split_dir.is_dir():
            missing_splits.append(split)
        else:
            actual_splits.append(split)

    if missing_splits:
        print(f"  Missing split directories: {sorted(missing_splits)}")

    unexpected_splits = [d.name for d in root.iterdir() if d.is_dir() and d.name not in expected_splits]
    if unexpected_splits:
        print(f"  Unexpected split directories: {sorted(unexpected_splits)}")

    totals = {split: 0 for split in expected_splits}
    missing_classes = {split: [] for split in expected_splits}
    unexpected_classes = {split: [] for split in expected_splits}
    non_image_files = []

    for split in actual_splits:
        split_dir = root / split
        found_classes = {d.name for d in split_dir.iterdir() if d.is_dir()}

        for expected_class in expected_classes:
            class_dir = split_dir / expected_class
            if not class_dir.exists() or not class_dir.is_dir():
                missing_classes[split].append(expected_class)
                continue

            class_images = [p for p in class_dir.iterdir() if p.is_file()]
            image_files = [p for p in class_images if is_image_file(p)]
            extras = [p for p in class_images if not is_image_file(p)]

            totals[split] += len(image_files)
            if extras:
                non_image_files.extend(extras)

            print(f"  {split} / {expected_class}: {len(image_files)}")

        for actual_class in sorted(found_classes - expected_classes):
            unexpected_classes[split].append(actual_class)

    print("\nSummary:")
    for split in sorted(totals):
        print(f"  {name} {split}: {totals[split]}")

    print(f"  {name} total: {sum(totals.values())}")

    if missing_splits:
        print(f"  Missing splits: {missing_splits}")
    if any(missing_classes.values()):
        print(f"  Missing class directories:")
        for split, classes in missing_classes.items():
            if classes:
                print(f"    {split}: {sorted(classes)}")
    if any(unexpected_classes.values()):
        print(f"  Unexpected class directories:")
        for split, classes in unexpected_classes.items():
            if classes:
                print(f"    {split}: {sorted(classes)}")
    if non_image_files:
        print("  Non-image files found:")
        for path in non_image_files:
            print(f"    {path}")

    expected_total = sum(dataset["expected_totals"].values())
    if sum(totals.values()) != expected_total:
        print(
            f"  Expected total {expected_total}, found {sum(totals.values())}"
        )


def main():
    for name, dataset in DATASETS.items():
        verify_dataset(name, dataset)


if __name__ == "__main__":
    main()
