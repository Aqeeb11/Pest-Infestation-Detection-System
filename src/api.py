from pathlib import Path
import sys
import tempfile
import shutil
import traceback
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import torch
from ultralytics import YOLO


# ============================================================
# Project root and sys.path adjustments
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# Router decision constants
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
# FastAPI app + CORS
# ============================================================

app = FastAPI(title="Grape Pest/Disease Detection API")


# ============================================================
# XAI / Grad-CAM static file serving
# ============================================================

XAI_DIR = PROJECT_ROOT / "runs" / "xai"
XAI_DIR.mkdir(parents=True, exist_ok=True)

app.mount(
    "/xai",
    StaticFiles(directory=str(XAI_DIR)),
    name="xai",
)


origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Device
# ============================================================

DEVICE = 0 if torch.cuda.is_available() else "cpu"


# ============================================================
# Helper functions
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
    Decide among:
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

    # Stage 1: Grape vs Non-grape

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

    # Stage 2: Disease vs Pest

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
# Model prediction helpers
# ============================================================

def extract_probs_by_name(result, model):
    """Extract probabilities mapping from a YOLO result object."""

    if result.probs is None:
        raise RuntimeError(
            "Model did not return classification probabilities."
        )

    probs = result.probs.data.cpu().numpy()

    probs_by_name = {}

    for index, score in enumerate(probs):
        class_name = model.names[int(index)]

        if class_name in CLASS_NAMES:
            probs_by_name[class_name] = float(score)

    for class_name in CLASS_NAMES:
        if class_name not in probs_by_name:
            raise RuntimeError(
                f"Router class missing: {class_name}"
            )

    return probs_by_name


def predict_router(model, image_path: str):
    """Run router model."""

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

    probabilities = result.probs.data.cpu().numpy()

    probs_by_name = {}

    for index, score in enumerate(probabilities):

        class_name = model.names[int(index)]

        if class_name in CLASS_NAMES:
            probs_by_name[class_name] = float(score)

    for class_name in CLASS_NAMES:
        if class_name not in probs_by_name:
            raise RuntimeError(
                f"Router class missing: {class_name}"
            )

    decision, info = decide_router(probs_by_name)

    return decision, probs_by_name, info


def predict_classification_model(model, image_path: str):
    """Run disease/pest classification model."""

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

    probabilities = result.probs.data.cpu().numpy()

    ranked = sorted(
        enumerate(probabilities),
        key=lambda item: float(item[1]),
        reverse=True,
    )

    best_index, best_score = ranked[0]

    best_name = model.names[int(best_index)]

    return (
        best_name,
        float(best_score),
        ranked,
    )


# ============================================================
# Startup: load models and treatment database
# ============================================================

@app.on_event("startup")
def load_models_and_db():

    root = PROJECT_ROOT

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

    app.state.router_model = None
    app.state.disease_model = None
    app.state.pest_model = None

    app.state.treatment_available = False
    app.state.get_recommendation = None

    # Router

    try:
        if router_path.exists():
            app.state.router_model = YOLO(
                str(router_path)
            )
    except Exception:
        app.state.router_model = None

    # Disease

    try:
        if disease_path.exists():
            app.state.disease_model = YOLO(
                str(disease_path)
            )
    except Exception:
        app.state.disease_model = None

    # Pest

    try:
        if pest_path.exists():
            app.state.pest_model = YOLO(
                str(pest_path)
            )
    except Exception:
        app.state.pest_model = None

    # Treatment database

    try:
        from data.treatment_database import get_recommendation

        app.state.get_recommendation = get_recommendation
        app.state.treatment_available = True

    except Exception:
        app.state.get_recommendation = None
        app.state.treatment_available = False


# ============================================================
# Root endpoint
# ============================================================

@app.get("/")
def root():

    return {
        "message": "Grape Pest/Disease Detection API is running"
    }


# ============================================================
# Health endpoint
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "ok",
        "router_model": bool(
            app.state.router_model
        ),
        "disease_model": bool(
            app.state.disease_model
        ),
        "pest_model": bool(
            app.state.pest_model
        ),
        "treatment_database": bool(
            app.state.treatment_available
        ),
        "xai": True,
    }


# ============================================================
# Prediction
# ============================================================

ALLOWED_EXT = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}


def is_image_filename(filename: str) -> bool:

    return (
        Path(filename).suffix.lower()
        in ALLOWED_EXT
    )


@app.post("/predict")
async def predict_endpoint(
    file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # Validate upload
    # --------------------------------------------------------

    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file uploaded",
        )

    if not is_image_filename(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type",
        )

    # --------------------------------------------------------
    # Temporary image
    # --------------------------------------------------------

    tmp_dir = tempfile.mkdtemp(
        prefix="pest_detect_"
    )

    tmp_path = (
        Path(tmp_dir)
        / Path(file.filename).name
    )

    try:

        with open(tmp_path, "wb") as f:

            content = await file.read()

            f.write(content)

        # ----------------------------------------------------
        # Router
        # ----------------------------------------------------

        if not app.state.router_model:

            raise HTTPException(
                status_code=500,
                detail="Router model not available on server",
            )

        try:

            (
                decision,
                probs_by_name,
                router_info,
            ) = predict_router(
                app.state.router_model,
                str(tmp_path),
            )

        except Exception as e:

            traceback.print_exc()

            raise HTTPException(
                status_code=500,
                detail=f"Router prediction failed: {e}",
            )

        router_summary = {

            "grape_disease": float(
                probs_by_name.get(
                    "grape_disease",
                    0.0,
                )
            ),

            "grape_pest": float(
                probs_by_name.get(
                    "grape_pest",
                    0.0,
                )
            ),

            "non_grape": float(
                probs_by_name.get(
                    "non_grape",
                    0.0,
                )
            ),

            "decision": decision,
        }

        response = {

            "success": True,

            "category": None,

            "prediction": None,

            "confidence": None,

            "router": router_summary,

            "treatment": None,

        }

        # ====================================================
        # NON GRAPE
        # ====================================================

        if decision == "non_grape":

            response.update({

                "category": "non_grape",

                "prediction": "non_grape",

                "confidence": None,

            })

            return response

        # ====================================================
        # UNCERTAIN
        # ====================================================

        if decision == "UNCERTAIN":

            response.update({

                "category": "uncertain",

                "prediction": "UNCERTAIN",

                "confidence": None,

            })

            return response

        # ====================================================
        # GRAPE DISEASE
        # ====================================================

        if decision == "grape_disease":

            if not app.state.disease_model:

                raise HTTPException(
                    status_code=500,
                    detail="Disease model not available on server",
                )

            try:

                (
                    best_name,
                    best_score,
                    ranked,
                ) = predict_classification_model(
                    app.state.disease_model,
                    str(tmp_path),
                )

            except Exception as e:

                traceback.print_exc()

                raise HTTPException(
                    status_code=500,
                    detail=f"Disease prediction failed: {e}",
                )

            response.update({

                "category": "grape_disease",

                "prediction": best_name,

                "confidence": float(best_score),

            })

            # ------------------------------------------------
            # Grad-CAM
            # ------------------------------------------------

            try:

                from src.xai import generate_gradcam

                best_index = (
                    int(ranked[0][0])
                    if ranked
                    else None
                )

                if best_index is not None:

                    out_dir = (
                        PROJECT_ROOT
                        / "runs"
                        / "xai"
                        / "disease"
                    )

                    out_dir.mkdir(
                        parents=True,
                        exist_ok=True,
                    )

                    out_path = (
                        out_dir
                        / f"{Path(tmp_path).stem}_gradcam.png"
                    )

                    generate_gradcam(
                        app.state.disease_model,
                        str(tmp_path),
                        str(out_path),
                        target_class=best_index,
                    )

                    # IMPORTANT:
                    # Return browser-accessible URL,
                    # not Windows filesystem path.

                    response["xai"] = {

                        "available": True,

                        "method": "Grad-CAM",

                        "predicted_class":
                            response["prediction"],

                        "confidence":
                            response["confidence"],

                        "heatmap_path":
                            f"/xai/disease/{out_path.name}",

                    }

                else:

                    response["xai"] = {

                        "available": False,

                        "error":
                            "Failed to determine predicted class index for XAI",

                    }

            except Exception as e:

                traceback.print_exc()

                response["xai"] = {

                    "available": False,

                    "error": str(e),

                }

        # ====================================================
        # GRAPE PEST
        # ====================================================

        elif decision == "grape_pest":

            if not app.state.pest_model:

                raise HTTPException(
                    status_code=500,
                    detail="Pest model not available on server",
                )

            try:

                (
                    best_name,
                    best_score,
                    ranked,
                ) = predict_classification_model(
                    app.state.pest_model,
                    str(tmp_path),
                )

            except Exception as e:

                traceback.print_exc()

                raise HTTPException(
                    status_code=500,
                    detail=f"Pest prediction failed: {e}",
                )

            response.update({

                "category": "grape_pest",

                "prediction": best_name,

                "confidence": float(best_score),

            })

            # ------------------------------------------------
            # Grad-CAM
            # ------------------------------------------------

            try:

                from src.xai import generate_gradcam

                best_index = (
                    int(ranked[0][0])
                    if ranked
                    else None
                )

                if best_index is not None:

                    out_dir = (
                        PROJECT_ROOT
                        / "runs"
                        / "xai"
                        / "pest"
                    )

                    out_dir.mkdir(
                        parents=True,
                        exist_ok=True,
                    )

                    out_path = (
                        out_dir
                        / f"{Path(tmp_path).stem}_gradcam.png"
                    )

                    generate_gradcam(
                        app.state.pest_model,
                        str(tmp_path),
                        str(out_path),
                        target_class=best_index,
                    )

                    # IMPORTANT:
                    # Return browser-accessible URL.

                    response["xai"] = {

                        "available": True,

                        "method": "Grad-CAM",

                        "predicted_class":
                            response["prediction"],

                        "confidence":
                            response["confidence"],

                        "heatmap_path":
                            f"/xai/pest/{out_path.name}",

                    }

                else:

                    response["xai"] = {

                        "available": False,

                        "error":
                            "Failed to determine predicted class index for XAI",

                    }

            except Exception as e:

                traceback.print_exc()

                response["xai"] = {

                    "available": False,

                    "error": str(e),

                }

        # ====================================================
        # Treatment recommendation
        # ====================================================

        if (
            app.state.treatment_available
            and app.state.get_recommendation
        ):

            try:

                rec = app.state.get_recommendation(
                    response["prediction"]
                )

                response["treatment"] = rec

            except Exception:

                response["treatment"] = None

        else:

            response["treatment"] = None

        return response

    finally:

        # ----------------------------------------------------
        # Clean temporary files
        # ----------------------------------------------------

        try:

            if tmp_path.exists():
                tmp_path.unlink()

        except Exception:
            pass

        try:

            shutil.rmtree(
                tmp_dir,
                ignore_errors=True,
            )

        except Exception:
            pass