from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from ultralytics import YOLO

# Project root
project_root = Path(__file__).resolve().parent.parent

# Load trained model
model = YOLO(
    project_root /
    "runs" /
    "classify" /
    "results" /
    "grape_classification-5" /
    "weights" /
    "best.pt"
)

root = tk.Tk()
root.withdraw()

image_file = filedialog.askopenfilename(
    title="Select a grape leaf image",
    filetypes=[("Image Files", "*.jpg *.jpeg *.png")]
)

if not image_file:
    print("No image selected.")
    exit()

results = model.predict(
    source=image_file,
    imgsz=224,
    save=True
)

r = results[0]

print("\n========== Prediction ==========")
print("Disease   :", r.names[r.probs.top1])
print(f"Confidence: {float(r.probs.top1conf) * 100:.2f}%")
print("================================")