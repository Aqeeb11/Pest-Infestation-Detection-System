from pathlib import Path

from ultralytics import YOLO


def main():
    # Path to the pest classification dataset.
    # It contains train, val, and test folders.
    dataset_root = Path("dataset/raw/pest")

    # Load the pretrained YOLOv8 image classification model.
    model = YOLO("yolov8n-cls.pt")

    print(f"Training pest classification model on: {dataset_root}")
    print("Using NVIDIA RTX 3050 GPU (device 0)")

    # Train the image classification model.
    results = model.train(
        data=str(dataset_root),
        epochs=30,
        imgsz=224,
        batch=16,
        device=0,
        workers=2,
        patience=8,
        project="runs/classify",
        name="pest_yolov8n",
        pretrained=True,
    )

    # Training output directory.
    run_dir = Path("runs/classify/pest_yolov8n")

    print("\nTraining complete.")
    print(f"Run directory: {run_dir}")
    print(f"Best model: {run_dir / 'weights' / 'best.pt'}")
    print(f"Last model: {run_dir / 'weights' / 'last.pt'}")


if __name__ == "__main__":
    main()