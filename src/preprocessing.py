from pathlib import Path
from typing import Tuple

from PIL import Image
from torchvision import transforms


DATASET_ROOT = Path(__file__).resolve().parents[1] / "dataset" / "classification"


def get_data_dir(split: str) -> Path:
    split_path = DATASET_ROOT / split
    if not split_path.exists():
        raise FileNotFoundError(f"Dataset split not found: {split_path}")
    return split_path


def build_transform(image_size: int = 224) -> transforms.Compose:
    return transforms.Compose(
        [
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )


def load_image(path: Path) -> Image.Image:
    with Image.open(path) as image:
        return image.convert("RGB")


def preprocess_image(path: Path, image_size: int = 224) -> Tuple[torch.Tensor, Path]:
    from torch import tensor

    image = load_image(path)
    transform = build_transform(image_size)
    tensor_image = transform(image)
    return tensor_image, path
