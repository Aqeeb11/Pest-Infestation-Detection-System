from pathlib import Path

import torch
import numpy as np
import matplotlib.pyplot as plt
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

    # Pest dataset
    dataset_root = root / "dataset" / "raw" / "pest"
    test_path = dataset_root / "test"

    # Check required paths
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

    # Load trained model
    model = YOLO(str(model_path))

    # ---------------------------------------------------------
    # 1. Standard YOLO validation
    # ---------------------------------------------------------
    metrics = model.val(
        data=str(dataset_root),
        split="test",
        device=device,
    )

    top1 = float(metrics.top1)
    top5 = float(metrics.top5)

    # ---------------------------------------------------------
    # 2. Get class names
    # ---------------------------------------------------------
    names = model.names

    if isinstance(names, dict):
        class_names = [names[i] for i in range(len(names))]
    else:
        class_names = list(names)

    num_classes = len(class_names)

    print("\nClasses:")
    for i, name in enumerate(class_names):
        print(f"{i}: {name}")

    # ---------------------------------------------------------
    # 3. Predict every test image
    # ---------------------------------------------------------
    y_true = []
    y_pred = []

    image_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".webp",
    }

    test_images = [
        file
        for file in test_path.rglob("*")
        if file.is_file()
        and file.suffix.lower() in image_extensions
    ]

    print(f"\nNumber of test images: {len(test_images)}")
    print("Generating predictions...")

    for image_path in test_images:

        # Expected structure:
        # test/
        #   class_1/
        #       image.jpg
        #   class_2/
        #       image.jpg

        relative_path = image_path.relative_to(test_path)

        # First directory after test/ is the true class
        if len(relative_path.parts) < 2:
            print(f"Skipping image with unknown class: {image_path}")
            continue

        true_class_name = relative_path.parts[0]

        # Convert true class name to class index
        if true_class_name not in class_names:
            print(
                f"Warning: class '{true_class_name}' "
                f"not found in model classes. Skipping."
            )
            continue

        true_index = class_names.index(true_class_name)

        # Predict
        results = model.predict(
            source=str(image_path),
            device=device,
            verbose=False,
        )

        if not results:
            continue

        result = results[0]

        if result.probs is None:
            continue

        # Top-1 predicted class
        predicted_index = int(result.probs.top1)

        y_true.append(true_index)
        y_pred.append(predicted_index)

    # ---------------------------------------------------------
    # 4. Create confusion matrix manually
    # ---------------------------------------------------------
    confusion = np.zeros(
        (num_classes, num_classes),
        dtype=int,
    )

    for true_index, predicted_index in zip(y_true, y_pred):
        confusion[true_index][predicted_index] += 1

    # ---------------------------------------------------------
    # 5. Create results directory
    # ---------------------------------------------------------
    results_dir = (
        root
        / "runs"
        / "classify"
        / "pest_yolov8n"
        / "test_results"
    )

    results_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ---------------------------------------------------------
    # 6. Save raw confusion matrix as CSV
    # ---------------------------------------------------------
    csv_file = results_dir / "confusion_matrix.csv"

    with open(csv_file, "w", encoding="utf-8") as file:
        file.write("," + ",".join(class_names) + "\n")

        for i, class_name in enumerate(class_names):
            row = ",".join(str(value) for value in confusion[i])
            file.write(f"{class_name},{row}\n")

    # ---------------------------------------------------------
    # 7. Generate normalized confusion matrix
    # ---------------------------------------------------------
    row_sums = confusion.sum(axis=1, keepdims=True)

    normalized = np.divide(
        confusion,
        row_sums,
        out=np.zeros_like(
            confusion,
            dtype=float,
        ),
        where=row_sums != 0,
    )

    # ---------------------------------------------------------
    # 8. Plot raw confusion matrix
    # ---------------------------------------------------------
    plt.figure(figsize=(12, 10))

    plt.imshow(
        confusion,
        interpolation="nearest",
        cmap="Blues",
    )

    plt.title("Pest Model Confusion Matrix")
    plt.colorbar()

    tick_marks = np.arange(num_classes)

    plt.xticks(
        tick_marks,
        class_names,
        rotation=90,
    )

    plt.yticks(
        tick_marks,
        class_names,
    )

    threshold = confusion.max() / 2.0

    for i in range(num_classes):
        for j in range(num_classes):

            plt.text(
                j,
                i,
                str(confusion[i, j]),
                horizontalalignment="center",
                color="white"
                if confusion[i, j] > threshold
                else "black",
            )

    plt.ylabel("True")
    plt.xlabel("Predicted")
    plt.tight_layout()

    confusion_png = results_dir / "confusion_matrix.png"

    plt.savefig(
        confusion_png,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    # ---------------------------------------------------------
    # 9. Plot normalized confusion matrix
    # ---------------------------------------------------------
    plt.figure(figsize=(12, 10))

    plt.imshow(
        normalized,
        interpolation="nearest",
        cmap="Blues",
        vmin=0,
        vmax=1,
    )

    plt.title("Pest Model Confusion Matrix Normalized")
    plt.colorbar()

    plt.xticks(
        tick_marks,
        class_names,
        rotation=90,
    )

    plt.yticks(
        tick_marks,
        class_names,
    )

    for i in range(num_classes):
        for j in range(num_classes):

            plt.text(
                j,
                i,
                f"{normalized[i, j]:.2f}",
                horizontalalignment="center",
                color="white"
                if normalized[i, j] > 0.5
                else "black",
            )

    plt.ylabel("True")
    plt.xlabel("Predicted")
    plt.tight_layout()

    normalized_png = (
        results_dir
        / "confusion_matrix_normalized.png"
    )

    plt.savefig(
        normalized_png,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    # ---------------------------------------------------------
    # 10. Save evaluation summary
    # ---------------------------------------------------------
    summary_file = results_dir / "evaluation_summary.txt"

    with open(
        summary_file,
        "w",
        encoding="utf-8",
    ) as file:

        file.write("PEST MODEL EVALUATION\n")
        file.write("=====================\n")
        file.write(
            f"Test Top-1 accuracy: {top1 * 100:.2f}%\n"
        )
        file.write(
            f"Test Top-5 accuracy: {top5 * 100:.2f}%\n"
        )
        file.write(
            f"Number of test images: {len(test_images)}\n"
        )
        file.write(
            f"Images used in confusion matrix: {len(y_true)}\n"
        )

    # ---------------------------------------------------------
    # 11. Print final results
    # ---------------------------------------------------------
    print("\n" + "=" * 60)
    print("             PEST MODEL EVALUATION")
    print("=" * 60)

    print(f"Test Top-1 accuracy: {top1 * 100:.2f}%")
    print(f"Test Top-5 accuracy: {top5 * 100:.2f}%")
    print(f"Number of test images: {len(test_images)}")
    print(
        f"Images used in confusion matrix: {len(y_true)}"
    )

    print("\nConfusion matrix saved to:")
    print(confusion_png)

    print("\nNormalized confusion matrix saved to:")
    print(normalized_png)

    print("\nCSV saved to:")
    print(csv_file)

    print("\nEvaluation summary saved to:")
    print(summary_file)

    print("=" * 60)


if __name__ == "__main__":
    main()