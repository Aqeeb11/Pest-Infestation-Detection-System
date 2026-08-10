import os
import tarfile
from pathlib import Path, PurePosixPath

ARCHIVE_PATH = r"C:\Users\Lenovo\Downloads\ip102_v1.1.tar"
TARGET_SPLITS = {
    "train": "ip102_v1.1/train.txt",
    "val": "ip102_v1.1/val.txt",
    "test": "ip102_v1.1/test.txt",
}
VITIS_CLASS_IDS = list(range(59, 76))
CLASS_NAME_MAP = {
    59: "Viteus_vitifoliae",
    60: "Colomerus_vitis",
    61: "Brevipalpus_lewisi",
    62: "Oides_decempunctata",
    63: "Polyphagotarsonemus_latus",
    64: "Pseudococcus_comstocki",
    65: "Parathrene_regalis",
    66: "Ampelophaga",
    67: "Lycorma_delicatula",
    68: "Xylotrechus",
    69: "Cicadella_viridis",
    70: "Miridae",
    71: "Trialeurodes_vaporariorum",
    72: "Erythroneura_apicalis",
    73: "Papilio_xuthus",
    74: "Panonchus_citri",
    75: "Phyllocoptes_oleiverus",
}
EXPECTED_COUNTS = {
    "train": 10060,
    "val": 1675,
    "test": 5041,
}
EXPECTED_TOTAL = sum(EXPECTED_COUNTS.values())


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def normalize_tar_path(path: str) -> str:
    normalized = path.replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.rstrip("/")


def build_tar_index(tar: tarfile.TarFile):
    full_map = {}
    basename_map = {}

    for member in tar.getmembers():
        normalized = normalize_tar_path(member.name)
        full_map[normalized] = member
        basename = Path(normalized).name
        basename_map.setdefault(basename, []).append(member)

    return full_map, basename_map


def find_tar_member(tar, image_name: str, full_map, basename_map):
    normalized_target = normalize_tar_path(image_name)
    candidate_paths = [
        normalized_target,
        f"ip102_v1.1/{normalized_target}",
        f"./{normalized_target}",
        f"./ip102_v1.1/{normalized_target}",
    ]

    for candidate in candidate_paths:
        member = full_map.get(candidate)
        if member is not None:
            return member

    base_name = Path(normalized_target).name
    possible = basename_map.get(base_name, [])
    if not possible:
        return None

    filtered = [m for m in possible if m.isfile()]
    if len(filtered) == 1:
        return filtered[0]

    raise ValueError(
        f"Multiple TAR members match image basename '{base_name}': "
        f"{[m.name for m in filtered]}"
    )


def parse_split_file(tar, path, full_map, basename_map):
    member = None
    normalized_path = normalize_tar_path(path)
    if normalized_path in full_map:
        member = full_map[normalized_path]
    elif f"./{normalized_path}" in full_map:
        member = full_map[f"./{normalized_path}"]

    if member is None:
        raise FileNotFoundError(f"Split file '{path}' not found in TAR archive.")

    with tar.extractfile(member) as fileobj:
        if fileobj is None:
            raise RuntimeError(f"Could not open split file '{member.name}' in TAR archive.")
        content = fileobj.read().decode("utf-8", errors="replace")

    selected = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        parts = stripped.split()
        if len(parts) != 2:
            raise ValueError(
                f"Unexpected format in split file '{path}' at line {line_number}: {line!r}"
            )

        image_name, class_id_str = parts
        try:
            class_id = int(class_id_str)
        except ValueError as exc:
            raise ValueError(
                f"Invalid class id in split file '{path}' at line {line_number}: {class_id_str!r}"
            ) from exc

        if class_id not in VITIS_CLASS_IDS:
            continue

        tar_member = find_tar_member(tar, image_name, full_map, basename_map)
        if tar_member is None:
            raise FileNotFoundError(
                f"Image '{image_name}' referenced in '{path}' not found in TAR archive."
            )

        selected.append((image_name, class_id, tar_member))

    return selected


def ensure_empty_target(target_dir: Path):
    if not target_dir.exists():
        target_dir.mkdir(parents=True, exist_ok=True)
        return

    items = list(target_dir.iterdir())
    if items:
        raise RuntimeError(
            f"Target directory '{target_dir}' is not empty. "
            "Please remove or relocate existing contents before extracting."
        )


def extract_selected_images(tar, selected_images, target_dir: Path):
    counts = {}
    total = 0

    for split_name, images in selected_images.items():
        print(f"\nExtracting {split_name}: {len(images)} images")
        split_dir = target_dir / split_name
        split_dir.mkdir(parents=True, exist_ok=True)

        per_class = {}
        for index, (image_name, class_id, member) in enumerate(images, start=1):
            class_name = CLASS_NAME_MAP[class_id]
            dest_dir = split_dir / class_name
            dest_dir.mkdir(parents=True, exist_ok=True)

            dest_path = dest_dir / Path(image_name).name
            if dest_path.exists():
                raise RuntimeError(
                    f"Destination file already exists: {dest_path}. "
                    "The script will not overwrite existing files."
                )

            with tar.extractfile(member) as source_file:
                if source_file is None:
                    raise RuntimeError(
                        f"Failed to open TAR member '{member.name}' for extraction."
                    )
                with open(dest_path, "wb") as out_file:
                    out_file.write(source_file.read())

            per_class[class_name] = per_class.get(class_name, 0) + 1
            total += 1

            if index % 250 == 0 or index == len(images):
                print(f"  {index}/{len(images)} extracted")

        print(f"Finished {split_name} split")
        for class_name in sorted(per_class):
            print(f"  {class_name}: {per_class[class_name]}")

        counts[split_name] = len(images)

    return counts, total


def main():
    repo_root = get_repo_root()
    target_root = repo_root / "dataset" / "raw" / "pest"

    print(f"Archive: {ARCHIVE_PATH}")
    print(f"Target directory: {target_root}")

    ensure_empty_target(target_root)
    print(f"Verified target directory is empty: {target_root}")

    with tarfile.open(ARCHIVE_PATH, "r") as tar:
        full_map, basename_map = build_tar_index(tar)
        selected_images = {}

        for split_name, split_path in TARGET_SPLITS.items():
            images = parse_split_file(tar, split_path, full_map, basename_map)
            selected_images[split_name] = images
            print(
                f"Selected {len(images)} Vitis images from split '{split_name}'"
            )

        for split_name, expected_count in EXPECTED_COUNTS.items():
            actual_count = len(selected_images[split_name])
            if actual_count != expected_count:
                raise AssertionError(
                    f"Split '{split_name}' count mismatch: expected {expected_count}, "
                    f"found {actual_count}."
                )

        all_selected = [item for split_images in selected_images.values() for item in split_images]
        if len(all_selected) != EXPECTED_TOTAL:
            raise AssertionError(
                f"Total selected image count mismatch: expected {EXPECTED_TOTAL}, "
                f"found {len(all_selected)}."
            )

        print(f"Starting extraction of {len(all_selected)} images...")
        counts, total_extracted = extract_selected_images(tar, selected_images, target_root)

    print("\nExtraction complete")
    for split_name in TARGET_SPLITS:
        print(f"  {split_name}: {counts[split_name]}")
    print(f"  total: {total_extracted}")

    if total_extracted != EXPECTED_TOTAL:
        raise AssertionError(
            f"Final extraction total mismatch: expected {EXPECTED_TOTAL}, found {total_extracted}."
        )


if __name__ == "__main__":
    main()
