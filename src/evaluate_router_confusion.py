from pathlib import Path

import torch
from ultralytics import YOLO


def main():
    root = Path(__file__).resolve().parents[1]

    model_path = (
        root
        / "runs"
        / "classify"
        / "router_yolov8n"
        / "weights"
        / "best.pt"
    )

    dataset_path = root / "dataset" / "router"

    if not model_path.exists():
        raise FileNotFoundError(
            f"Router model not found:\n{model_path}"
        )

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Router dataset not found:\n{dataset_path}"
        )

    device = 0 if torch.cuda.is_available() else "cpu"

    print("=" * 60)
    print("        ROUTER CONFUSION MATRIX")
    print("=" * 60)

    model = YOLO(str(model_path))

    print(f"Model: {model_path}")

    if device == 0:
        print("Using GPU: NVIDIA RTX 3050")
    else:
        print("Using CPU")

    # Run validation on test dataset
    metrics = model.val(
        data=str(dataset_path),
        split="test",
        device=device,
        plots=True,
    )

    print("\n" + "=" * 60)
    print("RESULT")
    print("=" * 60)

    print(
        f"Top-1 accuracy: "
        f"{float(metrics.top1) * 100:.2f}%"
    )

    print(
        f"Top-5 accuracy: "
        f"{float(metrics.top5) * 100:.2f}%"
    )

    print("\nClasses:")

    for index, name in model.names.items():
        print(f"{index}: {name}")

    print("\nConfusion matrix files are saved in:")
    print(
        root
        / "runs"
        / "classify"
        / "val-2"
    )

    print("\nLook for:")
    print("  confusion_matrix.png")
    print("  confusion_matrix_normalized.png")

    print("\nEvaluation complete.")


if __name__ == "__main__":
    main()