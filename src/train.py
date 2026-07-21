from ultralytics import YOLO

# Load YOLOv8 classification model
model = YOLO("yolov8n-cls.pt")

# Train the model
model.train(
    data="dataset/classification",
    epochs=30,
    imgsz=224,
    batch=16,
    project="results",
    name="grape_classification"
)