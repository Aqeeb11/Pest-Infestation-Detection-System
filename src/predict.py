from pathlib import Path
import sys
import tkinter as tk
from tkinter import filedialog

import torch
from ultralytics import YOLO


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Make project root available to Python so that
# data.treatment_database can be imported.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data.treatment_database import get_recommendation


# ============================================================
# DEVICE
# ============================================================

DEVICE = 0 if torch.cuda.is_available() else "cpu"


# ============================================================
# ROUTER DECISION SETTINGS
# ============================================================

GRAPE_VS_NONGRAPE_MARGIN = 0.20
DISEASE_VS_PEST_MARGIN = 0.20
ENTROPY_THRESHOLD = 0.65

CLASS_NAMES = (
    "grape_disease",
    "grape_pest",
    "non_grape",
)


# ============================================================
# ROUTER HELPER
# ============================================================

def normalized_entropy(probs):
    """Calculate normalized Shannon entropy for 3 classes."""
    import math

    eps = 1e-12

    entropy = -sum(
        p * math.log(p + eps)
        for p in probs
    )

    maximum = math.log(len(probs))

    return entropy / maximum


def decide_router(probs_by_name):
    """
    Decide:

    grape_disease
    grape_pest
    non_grape
    UNCERTAIN
    """

    p_disease = probs_by_name["grape_disease"]
    p_pest = probs_by_name["grape_pest"]
    p_non_grape = probs_by_name["non_grape"]

    entropy = normalized_entropy(
        [p_disease, p_pest, p_non_grape]
    )

    grape_score = p_disease + p_pest
    non_grape_score = p_non_grape

    domain_margin = abs(
        grape_score - non_grape_score
    )

    # --------------------------------------------------------
    # Stage 1: Grape vs Non-grape
    # --------------------------------------------------------

    if entropy > ENTROPY_THRESHOLD:
        return "UNCERTAIN", {
            "reason": "high_entropy",
            "entropy": entropy,
            "grape_score": grape_score,
            "non_grape_score": non_grape_score,
            "domain_margin": domain_margin,
        }

    if domain_margin < GRAPE_VS_NONGRAPE_MARGIN:
        return "UNCERTAIN", {
            "reason": "ambiguous_grape_vs_nongrape",
            "entropy": entropy,
            "grape_score": grape_score,
            "non_grape_score": non_grape_score,
            "domain_margin": domain_margin,
        }

    if non_grape_score > grape_score:
        return "non_grape", {
            "reason": None,
            "entropy": entropy,
            "grape_score": grape_score,
            "non_grape_score": non_grape_score,
            "domain_margin": domain_margin,
        }

    # --------------------------------------------------------
    # Stage 2: Disease vs Pest
    # --------------------------------------------------------

    ratio_disease = p_disease / grape_score
    ratio_pest = p_pest / grape_score

    fine_margin = abs(
        ratio_disease - ratio_pest
    )

    info = {
        "reason": None,
        "entropy": entropy,
        "grape_score": grape_score,
        "non_grape_score": non_grape_score,
        "domain_margin": domain_margin,
        "ratio_disease": ratio_disease,
        "ratio_pest": ratio_pest,
        "fine_margin": fine_margin,
    }

    if fine_margin < DISEASE_VS_PEST_MARGIN:
        info["reason"] = "ambiguous_disease_vs_pest"
        return "UNCERTAIN", info

    if ratio_disease > ratio_pest:
        return "grape_disease", info

    return "grape_pest", info


# ============================================================
# ROUTER PREDICTION
# ============================================================

def predict_router(model, image_path):

    results = model.predict(
        source=image_path,
        device=DEVICE,
        verbose=False,
    )

    if not results or results[0].probs is None:
        raise RuntimeError(
            "Router did not return classification probabilities."
        )

    result = results[0]

    probabilities = (
        result.probs.data
        .cpu()
        .numpy()
    )

    probs_by_name = {}

    for index, score in enumerate(probabilities):

        class_name = model.names[int(index)]

        if class_name in CLASS_NAMES:
            probs_by_name[class_name] = float(score)

    # Make sure all three classes exist
    for class_name in CLASS_NAMES:

        if class_name not in probs_by_name:
            raise RuntimeError(
                f"Router class missing: {class_name}"
            )

    decision, info = decide_router(
        probs_by_name
    )

    return decision, probs_by_name, info


# ============================================================
# DISEASE / PEST MODEL PREDICTION
# ============================================================

def predict_classification_model(
    model,
    image_path,
):

    results = model.predict(
        source=image_path,
        device=DEVICE,
        verbose=False,
    )

    if not results or results[0].probs is None:
        raise RuntimeError(
            "Classification model did not return probabilities."
        )

    result = results[0]

    probabilities = (
        result.probs.data
        .cpu()
        .numpy()
    )

    ranked = sorted(
        enumerate(probabilities),
        key=lambda item: float(item[1]),
        reverse=True,
    )

    best_index, best_score = ranked[0]

    best_name = model.names[
        int(best_index)
    ]

    return (
        best_name,
        float(best_score),
        ranked,
    )


# ============================================================
# TREATMENT / SUGGESTION DISPLAY
# ============================================================

def display_recommendation(class_name):
    """
    Look up the detected disease/pest in
    data/treatment_database.py and display:

    - Description
    - Symptoms/Damage
    - Management
    - Prevention
    - Treatment note
    - Verification status
    """

    recommendation = get_recommendation(
        class_name
    )

    print()
    print("=" * 65)
    print("              TREATMENT & SUGGESTIONS")
    print("=" * 65)

    if recommendation is None:

        print(
            f"No treatment information found for: {class_name}"
        )

        print("=" * 65)

        return

    print(
        f"Class : {recommendation['name']}"
    )

    print(
        f"Type  : {recommendation['type']}"
    )

    print()
    print("Description:")

    print(
        f"  {recommendation['description']}"
    )

    symptoms = recommendation.get(
        "symptoms",
        [],
    )

    if symptoms:

        print()
        print("Symptoms / Damage:")

        for item in symptoms:

            print(
                f"  • {item}"
            )

    print()
    print("Management:")

    for item in recommendation.get(
        "management",
        [],
    ):

        print(
            f"  • {item}"
        )

    print()
    print("Prevention:")

    for item in recommendation.get(
        "prevention",
        [],
    ):

        print(
            f"  • {item}"
        )

    print()
    print("Treatment Note:")

    print(
        f"  {recommendation.get('treatment_note', 'Follow current local agricultural guidance.')}"
    )

    print()
    print("Verification Status:")

    print(
        f"  {recommendation.get('verification_status', 'Not specified')}"
    )

    print("=" * 65)


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # Project root
    # --------------------------------------------------------

    root = PROJECT_ROOT

    # --------------------------------------------------------
    # Model paths
    # --------------------------------------------------------

    router_path = (
        root
        / "runs"
        / "classify"
        / "router_yolov8n_v2"
        / "weights"
        / "best.pt"
    )

    disease_path = (
        root
        / "runs"
        / "classify"
        / "disease_yolov8n"
        / "weights"
        / "best.pt"
    )

    pest_path = (
        root
        / "runs"
        / "classify"
        / "pest_yolov8n"
        / "weights"
        / "best.pt"
    )

    # --------------------------------------------------------
    # Check models
    # --------------------------------------------------------

    for model_path in (
        router_path,
        disease_path,
        pest_path,
    ):

        if not model_path.exists():

            raise FileNotFoundError(
                f"Model not found:\n{model_path}"
            )

    print("=" * 65)
    print("          GRAPE PEST / DISEASE DETECTION")
    print("=" * 65)

    if DEVICE == 0:

        print(
            "Using GPU: NVIDIA RTX 3050"
        )

    else:

        print("Using CPU")

    print()
    print("Loading models...")

    router_model = YOLO(
        str(router_path)
    )

    disease_model = YOLO(
        str(disease_path)
    )

    pest_model = YOLO(
        str(pest_path)
    )

    print(
        "Router model loaded."
    )

    print(
        "Disease model loaded."
    )

    print(
        "Pest model loaded."
    )

    # --------------------------------------------------------
    # Select image ONCE
    # --------------------------------------------------------

    window = tk.Tk()
    window.withdraw()

    image_path = filedialog.askopenfilename(
        title="Select grape image",
        filetypes=[
            (
                "Image files",
                "*.jpg *.jpeg *.png *.bmp *.webp",
            ),
            ("All files", "*.*"),
        ],
    )

    window.destroy()

    if not image_path:

        print(
            "No image selected."
        )

        return

    image_name = Path(
        image_path
    ).name

    print()
    print(
        f"Image: {image_name}"
    )

    print()
    print(
        "Running router..."
    )

    # --------------------------------------------------------
    # ROUTER
    # --------------------------------------------------------

    decision, router_probs, router_info = (
        predict_router(
            router_model,
            image_path,
        )
    )

    print()
    print("-" * 65)
    print("                    ROUTER")
    print("-" * 65)

    print(
        f"grape_disease : "
        f"{router_probs['grape_disease'] * 100:.2f}%"
    )

    print(
        f"grape_pest    : "
        f"{router_probs['grape_pest'] * 100:.2f}%"
    )

    print(
        f"non_grape     : "
        f"{router_probs['non_grape'] * 100:.2f}%"
    )

    print()
    print(
        f"Router decision: {decision}"
    )

    # --------------------------------------------------------
    # NON-GRAPE
    # --------------------------------------------------------

    if decision == "non_grape":

        print()
        print("=" * 65)
        print(
            "RESULT: NON-GRAPE IMAGE"
        )
        print("=" * 65)

        print(
            "Please upload a grape leaf image."
        )

        return

    # --------------------------------------------------------
    # UNCERTAIN
    # --------------------------------------------------------

    if decision == "UNCERTAIN":

        print()
        print("=" * 65)
        print(
            "RESULT: UNCERTAIN"
        )
        print("=" * 65)

        print(
            "The router is not sufficiently confident."
        )

        print(
            f"Reason: {router_info.get('reason')}"
        )

        print(
            "The image will NOT be sent to the "
            "disease or pest model."
        )

        return

    # --------------------------------------------------------
    # GRAPE DISEASE
    # --------------------------------------------------------

    if decision == "grape_disease":

        print()
        print(
            "Router selected: DISEASE MODEL"
        )

        print(
            "Running disease model..."
        )

        (
            disease_name,
            disease_confidence,
            ranked,
        ) = predict_classification_model(
            disease_model,
            image_path,
        )

        print()
        print("=" * 65)
        print(
            "              FINAL RESULT"
        )
        print("=" * 65)

        print(
            "Category   : GRAPE DISEASE"
        )

        print(
            f"Disease    : {disease_name}"
        )

        print(
            f"Confidence : "
            f"{disease_confidence * 100:.2f}%"
        )

        print()
        print(
            "Top 5 disease predictions:"
        )

        for rank, (
            class_index,
            score,
        ) in enumerate(
            ranked[:5],
            start=1,
        ):

            class_name = (
                disease_model.names[
                    int(class_index)
                ]
            )

            print(
                f"{rank}. "
                f"{class_name:<25} "
                f"{float(score) * 100:.2f}%"
            )

        print("=" * 65)

        # ----------------------------------------------------
        # TREATMENT & SUGGESTIONS
        # ----------------------------------------------------

        display_recommendation(
            disease_name
        )

        return

    # --------------------------------------------------------
    # GRAPE PEST
    # --------------------------------------------------------

    if decision == "grape_pest":

        print()
        print(
            "Router selected: PEST MODEL"
        )

        print(
            "Running pest model..."
        )

        (
            pest_name,
            pest_confidence,
            ranked,
        ) = predict_classification_model(
            pest_model,
            image_path,
        )

        print()
        print("=" * 65)
        print(
            "              FINAL RESULT"
        )
        print("=" * 65)

        print(
            "Category   : GRAPE PEST"
        )

        print(
            f"Pest       : {pest_name}"
        )

        print(
            f"Confidence : "
            f"{pest_confidence * 100:.2f}%"
        )

        print()
        print(
            "Top 5 pest predictions:"
        )

        for rank, (
            class_index,
            score,
        ) in enumerate(
            ranked[:5],
            start=1,
        ):

            class_name = (
                pest_model.names[
                    int(class_index)
                ]
            )

            print(
                f"{rank}. "
                f"{class_name:<25} "
                f"{float(score) * 100:.2f}%"
            )

        print("=" * 65)

        # ----------------------------------------------------
        # TREATMENT & SUGGESTIONS
        # ----------------------------------------------------

        display_recommendation(
            pest_name
        )

        return


# ============================================================
# PROGRAM ENTRY
# ============================================================

if __name__ == "__main__":
    main()