from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import yaml
from ultralytics import YOLO


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _find_test_image_count(test_dir: Path) -> int:
    if not test_dir.exists():
        raise FileNotFoundError(f"Test directory not found: {test_dir}")
    return sum(1 for path in test_dir.rglob("*") if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"})


def _coerce_metric(metrics: Any, *candidate_names: str) -> Any:
    for name in candidate_names:
        if hasattr(metrics, name):
            return getattr(metrics, name)

    results_dict = getattr(metrics, "results_dict", None)
    if isinstance(results_dict, dict):
        for name in candidate_names:
            if name in results_dict:
                return results_dict[name]
            alt = name.replace("top1", "top1_acc").replace("top5", "top5_acc")
            if alt in results_dict:
                return results_dict[alt]

    return None


def _save_confusion_matrix(metrics: Any, output_dir: Path, class_names: list[str]) -> None:
    confusion_matrix = None
    cm_obj = getattr(metrics, "confusion_matrix", None)
    if cm_obj is not None:
        for attr in ("matrix", "confusion_matrix", "cm"):
            if hasattr(cm_obj, attr):
                value = getattr(cm_obj, attr)
                if value is not None:
                    confusion_matrix = value
                    break
        if confusion_matrix is None and hasattr(cm_obj, "to_array"):
            confusion_matrix = cm_obj.to_array()

    if confusion_matrix is None:
        print("Confusion matrix is not available in this Ultralytics version.")
        return

    matrix = np.asarray(confusion_matrix)
    if matrix.ndim != 2:
        print("Confusion matrix could not be interpreted as a 2D array.")
        return

    cm_path = output_dir / "confusion_matrix.csv"
    np.savetxt(cm_path, matrix, fmt="%d", delimiter=",")

    labels_path = output_dir / "class_names.json"
    with labels_path.open("w", encoding="utf-8") as handle:
        json.dump(class_names, handle, indent=2)

    print(f"Confusion matrix saved to: {cm_path}")
    print(f"Class labels saved to: {labels_path}")


def main() -> None:
    root = _repo_root()

    model_path = root / "runs/classify/disease_yolov8n/weights/best.pt"
    dataset_dir = root / "dataset/raw/disease/Grapevine Leaf Variety & Disease Dataset (GLVD)/Grapevine Leaf Variety & Disease Dataset (GLVD)/Diseases"
    data_config = root / "dataset/config/disease.yaml"
    test_dir = dataset_dir / "test"
    output_dir = root / "runs/classify/disease_yolov8n/test_results"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not model_path.exists():
        raise FileNotFoundError(f"Trained model not found: {model_path}")
    if not dataset_dir.exists():
        raise FileNotFoundError(f"Dataset directory not found: {dataset_dir}")
    if not data_config.exists():
        raise FileNotFoundError(f"Dataset config not found: {data_config}")
    if not test_dir.exists():
        raise FileNotFoundError(f"Test directory not found: {test_dir}")

    print(f"Loading model: {model_path}")
    model = YOLO(str(model_path))

    print(f"Evaluating only the test split from: {test_dir}")
    print(f"Using GPU device 0")

    metrics = model.val(
        data=str(dataset_dir),
        split="test",
        device=0,
        project=str(output_dir.parent),
        name=output_dir.name,
        exist_ok=True,
        imgsz=224,
        batch=16,
    )

    top1 = _coerce_metric(metrics, "top1", "top1_acc")
    top5 = _coerce_metric(metrics, "top5", "top5_acc")

    if top1 is None:
        top1 = getattr(metrics, "top1", None)
    if top5 is None:
        top5 = getattr(metrics, "top5", None)

    if top1 is not None:
        top1_value = float(top1) * 100.0
        print(f"Test Top-1 accuracy: {top1_value:.2f}%")
    else:
        print("Test Top-1 accuracy: unavailable")

    if top5 is not None:
        top5_value = float(top5) * 100.0
        print(f"Test Top-5 accuracy: {top5_value:.2f}%")
    else:
        print("Test Top-5 accuracy: unavailable")

    test_image_count = _find_test_image_count(test_dir)
    print(f"Number of test images: {test_image_count}")

    with data_config.open("r", encoding="utf-8") as handle:
        dataset_config = yaml.safe_load(handle)
    class_names = dataset_config.get("names", [])

    _save_confusion_matrix(metrics, output_dir, class_names)

    summary_path = output_dir / "evaluation_summary.json"
    summary = {
        "top1_accuracy": float(top1) if top1 is not None else None,
        "top5_accuracy": float(top5) if top5 is not None else None,
        "num_test_images": test_image_count,
        "model_path": str(model_path),
        "test_dir": str(test_dir),
    }
    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    print(f"Evaluation results saved in: {output_dir}")
    print(f"Summary saved to: {summary_path}")


if __name__ == "__main__":
    main()
