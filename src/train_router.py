"""
Router training script - v2

WHAT CHANGED FROM train_router.py AND WHY
-------------------------------------------------------------------------
The original router hit ~99% on its own test split but only ~85% on
manually chosen unseen images. That gap means the model was learning
something that correlates with the label ONLY inside this dataset
(background style, lighting, camera/source signature) instead of the
actual visual difference between disease symptoms, pest damage, and
non-grape leaves.

This version does NOT change your classes, your dataset, or your
architecture (still YOLOv8n-cls). It changes the training recipe so the
model is forced to rely on leaf/lesion/insect texture rather than
background shortcuts:

  - Stronger color augmentation (hsv_h/s/v): breaks the link between
    "this exact lighting/color profile" and the label.
  - Geometric augmentation (degrees, translate, scale, shear, flips):
    leaves/pests appear at arbitrary angles and positions in real
    photos, not just however they happened to be framed in your dataset.
  - erasing=0.3: randomly blanks out a patch of the image during
    training. This is one of the most direct fixes for "background
    shortcut learning" - the model can no longer count on the same
    corner of the image always being visible.
  - auto_augment="randaugment": adds additional randomized
    photometric/geometric perturbation on top of the above.
  - label_smoothing=0.1: stops the model from driving any single
    class's probability to a near-certain extreme during training.
    This directly targets "confidently wrong" predictions - a model
    trained with label smoothing tends to leave more probability mass
    on the runner-up class, which surfaces genuine ambiguity as a
    lower margin at inference time instead of hiding it.
  - dropout=0.2: extra regularization on the classifier head, since
    each class is drawn from a comparatively narrow/homogeneous source.
  - epochs raised from 17 (bounded by early stop) to a 40-epoch BUDGET.
    This is not "blindly increasing epochs to fix accuracy" - it is
    giving the model enough room to converge under the added
    augmentation (which makes each epoch a harder learning problem).
    patience=10 (early stopping) still controls actual training length,
    exactly as before.
  - seed=0 for reproducible comparisons between v1 and v2.

Saved to runs/classify/router_yolov8n_v2/ so your current router_yolov8n
run is untouched and still usable as a baseline for comparison.
"""

from pathlib import Path

import torch
from ultralytics import YOLO


def main():
    root = Path(__file__).resolve().parents[1]
    dataset_root = root / "dataset" / "router"

    if not dataset_root.exists():
        raise FileNotFoundError(f"Router dataset not found:\n{dataset_root}")

    device = 0 if torch.cuda.is_available() else "cpu"

    print("=" * 60)
    print("          TRAINING ROUTER MODEL (v2)")
    print("=" * 60)
    print(f"Dataset: {dataset_root}")
    print("Using GPU device 0" if device == 0 else "Using CPU")

    model = YOLO("yolov8n-cls.pt")

    results = model.train(
        data=str(dataset_root),
        epochs=40,
        imgsz=224,
        batch=32,
        device=device,
        workers=2,
        patience=10,
        pretrained=True,
        seed=0,
        project=str(root / "runs" / "classify"),
        name="router_yolov8n_v2",

        # ---- Regularization: discourage shortcut-driven overconfidence ----
        label_smoothing=0.1,
        dropout=0.2,

        # ---- Augmentation: remove background/lighting/source shortcuts ----
        hsv_h=0.02,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=15,
        translate=0.1,
        scale=0.3,
        shear=5,
        fliplr=0.5,
        flipud=0.2,
        erasing=0.3,
        auto_augment="randaugment",
    )

    print("\n" + "=" * 60)
    print("          ROUTER v2 TRAINING COMPLETE")
    print("=" * 60)

    run_dir = root / "runs" / "classify" / "router_yolov8n_v2"
    best_model = run_dir / "weights" / "best.pt"
    last_model = run_dir / "weights" / "last.pt"

    print(f"Run directory: {run_dir}")
    if best_model.exists():
        print(f"Best model: {best_model}")
    if last_model.exists():
        print(f"Last model: {last_model}")

    print(
        "\nNOTE: A higher/lower Top-1 number on this same dataset's test\n"
        "split does NOT tell you whether v2 actually fixed anything.\n"
        "Run evaluate_router.py against your manually collected unseen\n"
        "images (not this dataset's test split) to find out."
    )


if __name__ == "__main__":
    main()
