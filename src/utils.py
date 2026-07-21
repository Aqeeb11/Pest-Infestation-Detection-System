from pathlib import Path
from typing import Dict, List


def list_image_files(root: Path) -> List[Path]:
    if not root.exists():
        raise FileNotFoundError(f"Directory not found: {root}")
    return sorted([path for path in root.rglob('*') if path.is_file() and path.suffix.lower() in {'.jpg', '.jpeg', '.png'}])


def class_names(dataset_root: Path) -> List[str]:
    return sorted([path.name for path in dataset_root.iterdir() if path.is_dir()])


def build_label_map(class_names_list: List[str]) -> Dict[str, int]:
    return {name: index for index, name in enumerate(class_names_list)}
