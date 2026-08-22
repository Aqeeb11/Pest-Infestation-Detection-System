from pathlib import Path

import torch
from ultralytics import YOLO


def main():
    # Project root
    root = Path(__file__).resolve().parents[1]

    # Trained pest classification model
    model_path = (
        root
        / "runs"
        / "classify"
        / "pest_yolov8n"
        / "weights"
        / "best.pt"
    )

    # Pest dataset root
    dataset_root = root / "dataset" / "raw" / "pest"

    # Pest test dataset
    test_path = dataset_root / "test"

    if not model_path.exists():
        raise FileNotFoundError(
            f"Trained pest model not found:\n{model_path}"
        )

    if not dataset_root.exists():
        raise FileNotFoundError(
            f"Pest dataset not found:\n{dataset_root}"
        )

    if not test_path.exists():
        raise FileNotFoundError(
            f"Pest test dataset not found:\n{test_path}"
        )

    # Use GPU if available
    device = 0 if torch.cuda.is_available() else "cpu"

    print(f"Loading model: {model_path}")
    print(f"Evaluating pest test dataset from: {test_path}")

    if device == 0:
        print("Using GPU device 0")
    else:
        print("Using CPU")

    # Load trained classification model
    model = YOLO(str(model_path))

    # Evaluate only the test split
    metrics = model.val(
        data=str(dataset_root),
        split="test",
        device=device,
    )

    # Get Top-1 and Top-5 accuracy
    top1 = float(metrics.top1)
    top5 = float(metrics.top5)

    # Count test images
    image_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".webp",
    }

    test_images = sum(
        1
        for file in test_path.rglob("*")
        if file.is_file()
        and file.suffix.lower() in image_extensions
    )

    print("\n" + "=" * 55)
    print("             PEST MODEL EVALUATION")
    print("=" * 55)

    print(f"Test Top-1 accuracy: {top1 * 100:.2f}%")
    print(f"Test Top-5 accuracy: {top5 * 100:.2f}%")
    print(f"Number of test images: {test_images}")

    print("=" * 55)

    # Save evaluation results
    results_dir = (
        root
        / "runs"
        / "classify"
        / "pest_yolov8n"
        / "test_results"
    )

    results_dir.mkdir(parents=True, exist_ok=True)

    summary_file = results_dir / "evaluation_summary.txt"

    with open(summary_file, "w", encoding="utf-8") as file:
        file.write("PEST MODEL EVALUATION\n")
        file.write("=====================\n")
        file.write(f"Test Top-1 accuracy: {top1 * 100:.2f}%\n")
        file.write(f"Test Top-5 accuracy: {top5 * 100:.2f}%\n")
        file.write(f"Number of test images: {test_images}\n")

    print("\nEvaluation summary saved to:")
    print(summary_file)


if __name__ == "__main__":
    main()