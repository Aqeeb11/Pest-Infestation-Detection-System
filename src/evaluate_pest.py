from pathlib import Path
import tkinter as tk
from tkinter import filedialog

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

    if not model_path.exists():
        raise FileNotFoundError(
            f"Trained pest model not found:\n{model_path}"
        )

    # Use GPU if available
    device = 0 if torch.cuda.is_available() else "cpu"

    print("Loading pest model...")
    print(f"Model: {model_path}")

    if device == 0:
        print("Using GPU: NVIDIA RTX 3050")
    else:
        print("Using CPU")

    # Load trained model
    model = YOLO(str(model_path))

    # Open Windows file picker
    window = tk.Tk()
    window.withdraw()

    image_path = filedialog.askopenfilename(
        title="Select a grape leaf / pest image",
        filetypes=[
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.webp"),
            ("All files", "*.*"),
        ],
    )

    window.destroy()

    # If user cancels
    if not image_path:
        print("No image selected.")
        return

    print(f"\nSelected image: {image_path}")
    print("Running pest prediction...\n")

    # Run prediction
    results = model.predict(
        source=image_path,
        device=device,
        verbose=False,
    )

    if not results:
        print("No prediction result returned.")
        return

    result = results[0]

    if result.probs is None:
        print("The model did not return classification probabilities.")
        return

    # Get probabilities
    probabilities = result.probs.data.cpu().numpy()

    # Sort predictions from highest to lowest confidence
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
    print("              GRAPE PEST PREDICTION")
    print("=" * 55)

    print(f"Image: {Path(image_path).name