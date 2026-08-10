from pathlib import Path

from ultralytics import YOLO


def main():
    # Path to the disease dataset root containing train, val, and test folders.
    dataset_root = Path("dataset/raw/disease/Grapevine Leaf Variety & Disease Dataset (GLVD)/Grapevine Leaf Variety & Disease Dataset (GLVD)/Diseases")

    # Load the pretrained YOLOv8 classification model.
    model = YOLO("yolov8n-cls.pt")

    print(f"Training disease classification model on dataset: {dataset_root}")
    print("Using GPU device 0 and Ultralytics YOLOv8 classification API")

    results = model.train(
        data=str(dataset_root),
        epochs=30,
        imgsz=224,
        batch=16,
        device=0,
        workers=2,
        patience=8,
        project="runs/classify",
        name="disease_yolov8n",
        pretrained=True,
    )

    # Print the final run directory and the best model path if available.
    run_dir = Path("runs/classify/disease_yolov8n")
    best_model_path = getattr(results, "best", None)
    if best_model_path is None:
        best_model_path = getattr(results, "model", None)

    print("\nTraining complete.")
    print(f"Run directory: {run_dir}")
    if best_model_path is not None:
        print(f"Best model saved at: {best_model_path}")
    else:
        print("Best model path not available from the training result object.")


if __name__ == "__main__":
    main()
