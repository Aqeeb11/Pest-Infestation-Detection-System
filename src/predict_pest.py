from pathlib import Path
import tkinter as tk
from tkinter import filedialog

import torch
from ultralytics import YOLO


def main():
    # Project root directory
    root = Path(__file__).resolve().parents[1]

    # Trained pest classification model path
    model_path = root / "runs" / "classify" / "pest_yolov8n" / "weights" / "best.pt"

    if not model_path.exists():
        raise FileNotFoundError(f"Trained model not found: {model_path}")

    # Use GPU device 0 if CUDA is available, otherwise use CPU.
    device = 0 if torch.cuda.is_available() else "cpu"

    print("Loading pest model...")
    model = YOLO(str(model_path))

    # Open a Windows file chooser to select an image.
    window = tk.Tk()
    window.withdraw()

    image_path = filedialog.askopenfilename(
        title="Select a grape pest image",
        filetypes=[
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.webp"),
            ("All files", "*.*"),
        ],
    )

    window.destroy()

    if not image_path:
        print("No image selected.")
        return

    print(f"\nSelected image: {image_path}")
    print("Running prediction...\n")

    results = model.predict(source=image_path, device=device, verbose=False)

    if len(results) == 0:
        print("No prediction result returned.")
        return

    result = results[0]
    if result.probs is None:
        print("Could not get classification probabilities.")
        return

    probabilities = result.probs.data.cpu().numpy()
    ranked = sorted(enumerate(probabilities), key=lambda item: float(item[1]), reverse=True)

    best_index, best_score = ranked[0]
    best_name = model.names[int(best_index)]

    border = "=" * 50
    print(border)
    print("             GRAPE PEST PREDICTION")
    print(border)
    print(f"Image: {Path(image_path).name}\n")
    print(f"Prediction: {best_name}")
    print(f"Confidence: {float(best_score) * 100:.2f}%\n")
    print("Top 5 predictions:")

    for rank, (class_index, score) in enumerate(ranked[:5], start=1):
        class_name = model.names[int(class_index)]
        print(f"{rank}. {class_name:<22} {float(score) * 100:.2f}%")

    print(border)


if __name__ == "__main__":
    main()
