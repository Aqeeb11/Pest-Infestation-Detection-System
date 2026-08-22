import random
import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Existing disease dataset
DISEASE_ROOT = (
    PROJECT_ROOT
    / "dataset"
    / "raw"
    / "disease"
    / "Grapevine Leaf Variety & Disease Dataset (GLVD)"
    / "Grapevine Leaf Variety & Disease Dataset (GLVD)"
    / "Diseases"
)

# Existing pest dataset
PEST_ROOT = PROJECT_ROOT / "dataset" / "raw" / "pest"

# PlantVillage non-grape source
PLANTVILLAGE_ROOT = (
    PROJECT_ROOT
    / "dataset"
    / "raw"
    / "non_grape_source"
    / "plantvillage dataset"
    / "color"
)

# Router dataset
ROUTER_ROOT = PROJECT_ROOT / "dataset" / "router"

SPLITS = ("train", "val", "test")

SEED = 42

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}

TARGET_COUNTS = {
    "grape_disease": {
        "train": 1500,
        "val": 300,
        "test": 300,
    },
    "grape_pest": {
        "train": 1500,
        "val": 300,
        "test": 300,
    },
    "non_grape": {
        "train": 1500,
        "val": 300,
        "test": 300,
    },
}


def is_image_file(path: Path) -> bool:
    return (
        path.is_file()
        and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def collect_images(source_dir: Path) -> list[Path]:
    if not source_dir.exists():
        raise FileNotFoundError(
            f"Source directory not found:\n{source_dir}"
        )

    images = [
        path
        for path in source_dir.rglob("*")
        if is_image_file(path)
    ]

    if not images:
        raise FileNotFoundError(
            f"No images found in:\n{source_dir}"
        )

    return images


def collect_non_grape_images() -> list[Path]:
    """
    Collect PlantVillage color images while explicitly
    excluding every Grape class.
    """

    if not PLANTVILLAGE_ROOT.exists():
        raise FileNotFoundError(
            f"PlantVillage directory not found:\n"
            f"{PLANTVILLAGE_ROOT}"
        )

    images = []

    for class_dir in PLANTVILLAGE_ROOT.iterdir():

        if not class_dir.is_dir():
            continue

        # IMPORTANT:
        # Never allow any Grape class into non_grape.
        if class_dir.name.lower().startswith("grape"):
            continue

        for image_path in class_dir.rglob("*"):
            if is_image_file(image_path):
                images.append(image_path)

    if not images:
        raise FileNotFoundError(
            "No non-grape images were found in PlantVillage."
        )

    return images


def clear_directory(directory: Path) -> None:
    """Remove previously generated files."""

    if not directory.exists():
        return

    for item in directory.iterdir():

        if item.is_file():
            item.unlink()

        elif item.is_dir():
            shutil.rmtree(item)


def copy_images(
    images: list[Path],
    target_dir: Path,
    count: int,
    rng: random.Random,
) -> int:

    if len(images) < count:
        raise ValueError(
            f"Not enough images.\n"
            f"Requested: {count}\n"
            f"Available: {len(images)}"
        )

    target_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    selected = rng.sample(images, count)

    copied = 0

    for source_path in selected:

        destination = target_dir / source_path.name

        # Prevent filename conflicts
        if destination.exists():

            stem = source_path.stem
            suffix = source_path.suffix

            counter = 1

            while destination.exists():

                destination = (
                    target_dir
                    / f"{stem}_{counter}{suffix}"
                )

                counter += 1

        shutil.copy2(
            source_path,
            destination,
        )

        copied += 1

    return copied


def prepare_existing_class(
    source_root: Path,
    class_name: str,
    split: str,
    count: int,
    rng: random.Random,
) -> int:

    source_split = source_root / split

    images = collect_images(source_split)

    target_dir = (
        ROUTER_ROOT
        / split
        / class_name
    )

    clear_directory(target_dir)

    return copy_images(
        images,
        target_dir,
        count,
        rng,
    )


def prepare_non_grape(
    images: list[Path],
    rng: random.Random,
) -> dict[str, int]:

    total_required = sum(
        TARGET_COUNTS["non_grape"].values()
    )

    if len(images) < total_required:
        raise ValueError(
            f"Not enough non-grape images.\n"
            f"Required: {total_required}\n"
            f"Available: {len(images)}"
        )

    # Shuffle once and split into train/val/test.
    shuffled = images.copy()
    rng.shuffle(shuffled)

    train_count = TARGET_COUNTS["non_grape"]["train"]
    val_count = TARGET_COUNTS["non_grape"]["val"]
    test_count = TARGET_COUNTS["non_grape"]["test"]

    train_images = shuffled[
        :train_count
    ]

    val_images = shuffled[
        train_count:
        train_count + val_count
    ]

    test_images = shuffled[
        train_count + val_count:
        train_count + val_count + test_count
    ]

    split_images = {
        "train": train_images,
        "val": val_images,
        "test": test_images,
    }

    summary = {}

    for split, selected_images in split_images.items():

        target_dir = (
            ROUTER_ROOT
            / split
            / "non_grape"
        )

        clear_directory(target_dir)

        target_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        copied = 0

        for source_path in selected_images:

            # Extra safety check:
            # never copy anything from a Grape class.
            relative_parts = source_path.relative_to(
                PLANTVILLAGE_ROOT
            ).parts

            if relative_parts:
                source_class = relative_parts[0]

                if source_class.lower().startswith("grape"):
                    raise RuntimeError(
                        "SAFETY ERROR: A Grape image was "
                        "selected for non_grape."
                    )

            destination = target_dir / source_path.name

            if destination.exists():

                stem = source_path.stem
                suffix = source_path.suffix

                counter = 1

                while destination.exists():

                    destination = (
                        target_dir
                        / f"{stem}_{counter}{suffix}"
                    )

                    counter += 1

            shutil.copy2(
                source_path,
                destination,
            )

            copied += 1

        summary[split] = copied

    return summary


def main():

    print("=" * 60)
    print("       PREPARING 3-CLASS ROUTER DATASET")
    print("=" * 60)

    rng = random.Random(SEED)

    # Collect PlantVillage non-grape images.
    non_grape_images = collect_non_grape_images()

    print(
        f"\nNon-grape images available: "
        f"{len(non_grape_images)}"
    )

    # Prepare existing grape disease and pest classes.
    summary = {}

    for split in SPLITS:

        print(f"\nProcessing {split}...")

        disease_count = TARGET_COUNTS[
            "grape_disease"
        ][split]

        pest_count = TARGET_COUNTS[
            "grape_pest"
        ][split]

        disease_copied = prepare_existing_class(
            DISEASE_ROOT,
            "grape_disease",
            split,
            disease_count,
            rng,
        )

        pest_copied = prepare_existing_class(
            PEST_ROOT,
            "grape_pest",
            split,
            pest_count,
            rng,
        )

        summary[split] = {
            "grape_disease": disease_copied,
            "grape_pest": pest_copied,
        }

    # Prepare non-grape class.
    non_grape_summary = prepare_non_grape(
        non_grape_images,
        rng,
    )

    for split in SPLITS:
        summary[split]["non_grape"] = (
            non_grape_summary[split]
        )

    print("\n" + "=" * 60)
    print("          ROUTER DATASET READY")
    print("=" * 60)

    for split in SPLITS:

        print(f"\n[{split}]")

        for class_name, count in summary[split].items():

            print(
                f"  {class_name:<15}: "
                f"{count} images"
            )

    print("\nSafety checks:")
    print("  ✓ Grape classes excluded from non_grape")
    print("  ✓ Original disease dataset unchanged")
    print("  ✓ Original pest dataset unchanged")
    print("  ✓ Original PlantVillage dataset unchanged")
    print("  ✓ No model trained")


if __name__ == "__main__":
    main()