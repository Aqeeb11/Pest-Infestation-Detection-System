"""
Router prediction script - v2

WHAT CHANGED FROM predict_router.py AND WHY
-------------------------------------------------------------------------
This still uses ONE model with the SAME 3 classes
(grape_disease, grape_pest, non_grape) - nothing about the router's
class structure changed, per the project constraints.

What changed is how the raw 3-class probabilities are turned into a
decision. The old code compared the top-1 class's confidence and the
margin between the top-1 and top-2 raw classes. That conflates two
different questions into one number:

  Q1: Is this a grape leaf at all?          (grape vs non_grape)
  Q2: If it is, disease or pest?            (disease vs pest)

A flat top-1/top-2 margin check can pass even when Q1 is genuinely
ambiguous, simply because Q2 "wins" the tie-break by chance. This
version evaluates Q1 and Q2 as two separate, explicit checks computed
from the same softmax output:

  grape_score     = P(disease) + P(pest)
  non_grape_score = P(non_grape)

  Stage 1 (domain check): is grape_score clearly ahead of
  non_grape_score? If not -> UNCERTAIN. This is what should have
  caught the Apple example in your report - and does (pest 54.10% +
  disease 0.02% = 55.02% "grape" vs 45.87% "non_grape" -> the 25%
  margin requirement rejects this correctly).

  Stage 2 (fine-grained check): only evaluated if Stage 1 passed.
  Is disease clearly ahead of pest, or vice versa, WITHIN the grape
  probability mass? If not -> UNCERTAIN.

Additionally, a normalized entropy check is added as a second,
independent uncertainty signal. Entropy catches near-uniform
distributions (e.g. ~33/33/33) that a pure margin check can sometimes
miss depending on how mass is distributed, and gives you a single
interpretable "how confused was the model" number for logging.

IMPORTANT - what this file does NOT do:
This decision logic reduces false "forced" classifications and makes
genuine 3-way ambiguity easier to catch. It does NOT, by itself, fix a
model that has learned a background/lighting shortcut and is
confidently wrong as a result - that is a training-data problem, fixed
in train_router_v2.py. Use both together.
"""

import math
from pathlib import Path

import torch
from ultralytics import YOLO

DEVICE = 0 if torch.cuda.is_available() else "cpu"

# Stage 1: grape vs non_grape must be separated by at least this margin
GRAPE_VS_NONGRAPE_MARGIN = 0.20

# Stage 2: disease vs pest (within the grape probability mass) must be
# separated by at least this margin
DISEASE_VS_PEST_MARGIN = 0.20

# Reject if normalized entropy over all 3 raw classes exceeds this
# (0 = fully confident, 1 = perfectly uniform/uncertain)
ENTROPY_THRESHOLD = 0.65

CLASS_NAMES = ("grape_disease", "grape_pest", "non_grape")


def normalized_entropy(probs):
    """Shannon entropy over the 3-class distribution, normalized to [0, 1]."""
    eps = 1e-12
    h = -sum(p * math.log(p + eps) for p in probs)
    h_max = math.log(len(probs))
    return h / h_max


def decide(probs_by_name: dict):
    """
    probs_by_name: dict mapping class name -> probability (float), for
    exactly the 3 router classes.

    Returns (decision, info) where decision is one of:
      "grape_disease", "grape_pest", "non_grape", "UNCERTAIN"
    and info is a dict of diagnostic values for logging/evaluation.
    """
    p_disease = probs_by_name["grape_disease"]
    p_pest = probs_by_name["grape_pest"]
    p_non_grape = probs_by_name["non_grape"]

    entropy = normalized_entropy([p_disease, p_pest, p_non_grape])

    grape_score = p_disease + p_pest
    non_grape_score = p_non_grape
    domain_margin = abs(grape_score - non_grape_score)

    info = {
        "p_disease": p_disease,
        "p_pest": p_pest,
        "p_non_grape": p_non_grape,
        "grape_score": grape_score,
        "non_grape_score": non_grape_score,
        "domain_margin": domain_margin,
        "entropy": entropy,
    }

    if entropy > ENTROPY_THRESHOLD:
        info["reason"] = "high_entropy"
        return "UNCERTAIN", info

    if domain_margin < GRAPE_VS_NONGRAPE_MARGIN:
        info["reason"] = "ambiguous_grape_vs_nongrape"
        return "UNCERTAIN", info

    if non_grape_score > grape_score:
        info["reason"] = None
        return "non_grape", info

    # It's a grape leaf. Now decide disease vs pest using only the
    # probability mass that belongs to those two classes.
    ratio_disease = p_disease / grape_score
    ratio_pest = p_pest / grape_score
    fine_margin = abs(ratio_disease - ratio_pest)
    info["ratio_disease"] = ratio_disease
    info["ratio_pest"] = ratio_pest
    info["fine_margin"] = fine_margin

    if fine_margin < DISEASE_VS_PEST_MARGIN:
        info["reason"] = "ambiguous_disease_vs_pest"
        return "UNCERTAIN", info

    info["reason"] = None
    if ratio_disease > ratio_pest:
        return "grape_disease", info
    return "grape_pest", info


def load_router(model_path: Path) -> YOLO:
    if not model_path.exists():
        raise FileNotFoundError(f"Router model not found:\n{model_path}")
    return YOLO(str(model_path))


def predict_image(model: YOLO, image_path: str):
    results = model.predict(source=image_path, device=DEVICE, verbose=False)
    if not results or results[0].probs is None:
        raise RuntimeError("Router did not return classification probabilities.")

    result = results[0]
    raw = result.probs.data.cpu().numpy()

    probs_by_name = {}
    for idx, score in enumerate(raw):
        name = model.names[int(idx)]
        if name in CLASS_NAMES:
            probs_by_name[name] = float(score)

    decision, info = decide(probs_by_name)
    return decision, info


def main():
    import tkinter as tk
    from tkinter import filedialog

    root = Path(__file__).resolve().parents[1]
    model_path = root / "runs" / "classify" / "router_yolov8n_v2" / "weights" / "best.pt"

    print(f"Loading router model: {model_path}")
    print("Using GPU: NVIDIA RTX 3050" if DEVICE == 0 else "Using CPU")
    model = load_router(model_path)

    window = tk.Tk()
    window.withdraw()
    image_path = filedialog.askopenfilename(
        title="Select an image",
        filetypes=[
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.webp"),
            ("All files", "*.*"),
        ],
    )
    window.destroy()

    if not image_path:
        print("No image selected.")
        return

    print(f"\nImage: {Path(image_path).name}")
    print("Running router prediction...\n")

    decision, info = predict_image(model, image_path)

    print("=" * 55)
    print("              ROUTER RESULT (v2)")
    print("=" * 55)
    print(f"grape_disease prob : {info['p_disease'] * 100:.2f}%")
    print(f"grape_pest prob    : {info['p_pest'] * 100:.2f}%")
    print(f"non_grape prob     : {info['p_non_grape'] * 100:.2f}%")
    print(f"grape score        : {info['grape_score'] * 100:.2f}%")
    print(f"non_grape score    : {info['non_grape_score'] * 100:.2f}%")
    print(f"domain margin      : {info['domain_margin'] * 100:.2f}%  (need >= {GRAPE_VS_NONGRAPE_MARGIN*100:.0f}%)")
    if "fine_margin" in info:
        print(f"disease/pest margin: {info['fine_margin'] * 100:.2f}%  (need >= {DISEASE_VS_PEST_MARGIN*100:.0f}%)")
    print(f"entropy            : {info['entropy']:.3f}  (reject if > {ENTROPY_THRESHOLD})")
    print("-" * 55)

    if decision == "UNCERTAIN":
        print(f"RESULT: UNCERTAIN  (reason: {info['reason']})")
        print("Please upload a clearer grape leaf image.")
        print("The image will NOT be sent to the disease or pest model.")
    elif decision == "non_grape":
        print("RESULT: NON-GRAPE IMAGE")
        print("Please upload a grape leaf image.")
    elif decision == "grape_disease":
        print("RESULT: GRAPE DISEASE IMAGE")
        print("This image can be sent to the disease model.")
    elif decision == "grape_pest":
        print("RESULT: GRAPE PEST IMAGE")
        print("This image can be sent to the pest model.")

    print("=" * 55)


if __name__ == "__main__":
    main()
