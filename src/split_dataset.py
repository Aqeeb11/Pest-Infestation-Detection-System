from argparse import ArgumentParser
from pathlib import Path
import random
import shutil
from typing import List, Sequence

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif'}


def is_image_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS


def collect_images(source_dir: Path) -> List[Path]:
    return sorted([path for path in source_dir.iterdir() if is_image_file(path)])


def clear_output_root(output_root: Path) -> None:
    if output_root.exists():
        print(f"Removing old output directory: {output_root}")
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)


def copy_images(images: Sequence[Path], destination_dir: Path) -> None:
    destination_dir.mkdir(parents=True, exist_ok=True)
    for image_path in images:
        shutil.copy2(image_path, destination_dir / image_path.name)


def split_train_folder(train_src: Path, output_root: Path, train_ratio: float, seed: int) -> None:
    print(f"Reading training data from: {train_src}")
    random.seed(seed)

    for class_dir in sorted(train_src.iterdir()):
        if not class_dir.is_dir():
            continue

        images = collect_images(class_dir)
        if not images:
            print(f"  Skipping empty class directory: {class_dir.name}")
            continue

        random.shuffle(images)
        split_index = int(len(images) * train_ratio)
        train_images = images[:split_index]
        valid_images = images[split_index:]

        print(
            f"  {class_dir.name}: {len(images)} images -> "
            f"{len(train_images)} train, {len(valid_images)} valid"
        )

        copy_images(train_images, output_root / 'train' / class_dir.name)
        copy_images(valid_images, output_root / 'valid' / class_dir.name)


def copy_test_folder(test_src: Path, output_root: Path) -> None:
    if not test_src.exists():
        print(f"Test folder does not exist: {test_src}")
        return

    print(f"Copying test data from: {test_src}")
    for class_dir in sorted(test_src.iterdir()):
        if not class_dir.is_dir():
            continue

        images = collect_images(class_dir)
        if not images:
            print(f"  Skipping empty test class directory: {class_dir.name}")
            continue

        print(f"  {class_dir.name}: copying {len(images)} test images")
        copy_images(images, output_root / 'test' / class_dir.name)


def parse_args() -> ArgumentParser:
    parser = ArgumentParser(description='Split augmented dataset into classification train/valid/test folders.')
    root = Path(__file__).resolve().parents[1]
    parser.add_argument(
        '--source', '-s',
        type=Path,
        default=root / 'dataset' / 'raw' / 'augmented-dataset',
        help='Source dataset root containing train, valid, and test folders.',
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=root / 'dataset' / 'classification',
        help='Output dataset root for train, valid, and test folders.',
    )
    parser.add_argument(
        '--train-ratio',
        type=float,
        default=0.8,
        help='Fraction of training images to keep in the train split.',
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed when shuffling training images.',
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_root = args.source
    output_root = args.output
    train_root = source_root / 'train'
    test_root = source_root / 'test'
    valid_root = source_root / 'valid'

    if not train_root.exists():
        raise FileNotFoundError(f"Train folder not found: {train_root}")

    clear_output_root(output_root)

    if valid_root.exists() and not any(valid_root.iterdir()):
        print(f"Ignoring existing empty valid folder: {valid_root}")

    split_train_folder(train_root, output_root, args.train_ratio, args.seed)
    copy_test_folder(test_root, output_root)

    print("Dataset split complete.")


if __name__ == '__main__':
    main()
