from pathlib import Path
import tkinter as tk
from tkinter import filedialog

import torch
from ultralytics import YOLO


def main():
    # Project root
    root = Path(__file__).resolve().parents[1]

    # Trained disease model
    model_path = (
        root
        / "runs"
        / "classify"
        / "disease_yolov8n"
        / "weights"
        / "best.pt"
    )

    if not model_path.exists():
        raise FileNotFoundError(
            f"Trained model not found:\n{model_path}"
        )

    # Use GPU if available
    device = 0 if torch.cuda.is_available() else "cpu"

    print("Loading disease model...")
    model = YOLO(str(model_path))

    # Open Windows file picker
    window = tk.Tk()
    window.withdraw()

    image_path = filedialog.askopenfilename(
        title="Select a grape leaf image",
        filetypes=[
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.webp"),
            ("All files", "*.*"),
        ],
    )

    window.destroy()

    # User cancelled
    if not image_path:
        print("No image selected.")
        return

    print(f"\nSelected image: {image_path}")
    print("Running prediction...\n")

    # Predict
    results = model.predict(
        source=image_path,
        device=device,
        verbose=False,
    )

    result = results[0]

    if result.probs is None:
        print("Could not get classification probabilities.")
        return

    # Get class probabilities
    probabilities = result.probs.data.cpu().numpy()

    # Sort from highest to lowest confidence
    ranked = sorted(
        enumerate(probabilities),
        key=lambda x: float(x[1]),
        reverse=True,
    )

    # Best prediction
    best_index, best_score = ranked[0]
    best_name = model.names[int(best_index)]

    # Display result
    print("=" * 55)
    print("             GRAPE DISEASE PREDICTION")
    print("=" * 55)

    print(f"Image: {Path(image_path).name}")
    print()
    print(f"Prediction : {best_name}")
    print(f"Confidence : {float(best_score) * 100:.2f}%")

    print("\nTop 5 predictions:")

    for rank, (class_index, score) in enumerate(
        ranked[:5], start=1
    ):
        class_name = model.names[int(class_index)]
        confidence = float(score) * 100

        print(
            f"{rank}. {class_name:<25} "
            f"{confidence:.2f}%"
        )

    print("=" * 55)


if __name__ == "__main__":
    main()