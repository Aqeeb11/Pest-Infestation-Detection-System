from pathlib import Path
import sys
import os
from typing import Optional, Dict, Any

import numpy as np
from PIL import Image

import torch
import torch.nn as nn

try:
    import cv2
except Exception:
    cv2 = None

from ultralytics import YOLO


# ============================================================
# Class lists (project-specific) used to infer model category
# ============================================================

DISEASE_CLASSES = [
    "Bacterial Rot",
    "Black Measles",
    "Black Rot",
    "Downy Mildew",
    "Healthy Leaves",
    "Leaf Blight",
    "Powdery Mildew",
]

PEST_CLASSES = [
    "Ampelophaga",
    "Brevipalpus_lewisi",
    "Cicadella_viridis",
    "Colomerus_vitis",
    "Erythroneura_apicalis",
    "Lycorma_delicatula",
    "Miridae",
    "Oides_decempunctata",
    "Panonchus_citri",
    "Papilio_xuthus",
    "Parathrene_regalis",
    "Phyllocoptes_oleiverus",
    "Polyphagotarsonemus_latus",
    "Pseudococcus_comstocki",
    "Trialeurodes_vaporariorum",
    "Viteus_vitifoliae",
    "Xylotrechus",
]


# ============================================================
# Utilities for finding the underlying torch model and layer
# ============================================================

def get_torch_model(yolo_model: YOLO) -> nn.Module:
    """
    Extract the underlying torch.nn.Module from an Ultralytics YOLO wrapper.

    This function is defensive: it tries a few common attribute names
    used by different Ultralytics releases and returns the first
    torch.nn.Module it finds.
    """

    # YOLO wrapper often exposes .model which is the torch model
    candidates = [
        getattr(yolo_model, "model", None),
        getattr(getattr(yolo_model, "model", None), "model", None),
    ]

    for c in candidates:
        if isinstance(c, nn.Module):
            return c

    # Fallback: sometimes the YOLO object itself is callable and holds the module
    if isinstance(yolo_model, nn.Module):
        return yolo_model

    raise ValueError("Unable to locate underlying torch model inside YOLO wrapper")


def find_target_layer(module: nn.Module) -> nn.Module:
    """
    Select a convolutional layer to use for Grad-CAM.

    Strategy: search modules in reverse order and pick the first
    instance of `nn.Conv2d`. This usually corresponds to the last
    convolutional feature map before pooling/classifier in CNNs.

    We avoid hard-coding layer names so the function remains robust
    across minor architecture differences in YOLOv8 classification models.
    """

    conv_layers = [m for m in module.modules() if isinstance(m, nn.Conv2d)]

    if not conv_layers:
        raise ValueError("No Conv2d layers found in model; unsupported architecture for Grad-CAM")

    # Choose last conv layer
    return conv_layers[-1]


# ============================================================
# Grad-CAM implementation
# ============================================================

def _preprocess_image(image_path: Path, img_size: int = 640, device=None) -> torch.Tensor:
    """Load image with PIL and prepare a tensor for the model.

    We resize to `img_size` (square), convert to RGB, scale to [0,1]
    and produce a batched tensor with shape (1,3,H,W).
    """

    img = Image.open(image_path).convert("RGB")

    # Resize while preserving aspect ratio by default YOLO predict does its own sampling.
    img_resized = img.resize((img_size, img_size), Image.BILINEAR)

    arr = np.array(img_resized).astype(np.float32) / 255.0
    # HWC -> CHW
    tensor = torch.from_numpy(arr).permute(2, 0, 1).unsqueeze(0)

    if device is not None:
        tensor = tensor.to(device)

    # Ensure gradients enabled
    tensor.requires_grad = True

    return tensor, img


def _apply_colormap_on_image(org_img: np.ndarray, activation_map: np.ndarray, colormap=cv2.COLORMAP_JET, alpha=0.4):
    """Overlay heatmap on image using OpenCV if available.

    `org_img` should be uint8 RGB numpy array.
    `activation_map` should be float32 0..1 same HxW as org_img.
    """

    if cv2 is None:
        raise RuntimeError("OpenCV is required for creating heatmap overlays. Install opencv-python.")

    heatmap = np.uint8(255 * activation_map)
    heatmap = cv2.applyColorMap(heatmap, colormap)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)

    overlay = cv2.addWeighted(org_img, 1.0 - alpha, heatmap, alpha, 0)

    return overlay


def generate_gradcam(
    model: YOLO,
    image_path: str,
    output_path: str,
    target_class: Optional[int] = None,
    img_size: int = 640,
) -> Dict[str, Any]:
    """
    Generate a Grad-CAM heatmap for a YOLOv8 classification model.

    - `model`: an Ultralytics `YOLO` instance (classification model)
    - `image_path`: path to input image
    - `output_path`: path where overlay image will be saved
    - `target_class`: optional integer class index; if omitted the predicted class is used

    Returns a dict with predicted class, index, confidence, and heatmap path.
    """

    image_path = Path(image_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Extract torch model
    torch_model = get_torch_model(model)
    torch_model.eval()
    torch_model.to(device)

    # Select conv layer dynamically
    target_layer = find_target_layer(torch_model)

    # Containers for hooks
    activations = {}
    gradients = {}

    def forward_hook(module, inp, out):
        # Save forward activations
        activations['value'] = out.detach()

    def backward_hook(module, grad_in, grad_out):
        # Save gradients w.r.t. the activation
        gradients['value'] = grad_out[0].detach()

    fh = target_layer.register_forward_hook(forward_hook)
    bh = target_layer.register_backward_hook(backward_hook)

    try:
        # Preprocess image
        input_tensor, orig_img = _preprocess_image(image_path, img_size=img_size, device=device)

        # Forward pass through the underlying torch model to get logits
        outputs = torch_model(input_tensor)

        # Typical YOLOv8 classification returns logits shape (1, num_classes)
        if isinstance(outputs, (list, tuple)):
            # Some model wrappers return (logits, ) or similar
            logits = outputs[0]
        else:
            logits = outputs

        if not isinstance(logits, torch.Tensor):
            # Try to extract tensor if wrapped in ultralytics result
            # As a fallback try model.predict and use its probs
            raise RuntimeError("Unexpected model output type; expected torch.Tensor for logits")

        # If logits is of shape [1, C, ...] reduce spatial dimensions if present
        if logits.ndim > 2:
            # Global pool to get class scores
            logits = torch.flatten(torch.mean(logits, dim=[2, 3]), 1)

        probs = torch.nn.functional.softmax(logits, dim=1)
        conf, pred_idx = torch.max(probs, dim=1)

        pred_idx_item = int(pred_idx.item())
        conf_item = float(conf.item())

        # Use provided target_class if given
        if target_class is not None:
            class_index = int(target_class)
            if class_index < 0 or class_index >= logits.shape[1]:
                raise ValueError("target_class index out of range for model outputs")
        else:
            class_index = pred_idx_item

        # Backward on the score for the target class
        torch_model.zero_grad()
        score = logits[0, class_index]
        score.backward(retain_graph=False)

        # Retrieve activations and gradients
        if 'value' not in activations or 'value' not in gradients:
            raise RuntimeError("Failed to capture activations or gradients from the target layer")

        activation = activations['value'][0]  # C x H x W
        grad = gradients['value'][0]  # C x H x W

        # Global-average-pool the gradients to obtain the neuron importance weights
        weights = torch.mean(grad.view(grad.size(0), -1), dim=1)  # C

        # Weighted combination of forward activation maps
        cam = torch.zeros(activation.size(1), activation.size(2), device=activation.device)
        for i, w in enumerate(weights):
            cam += w * activation[i]

        cam = torch.relu(cam)

        # Normalize cam to 0..1
        cam -= cam.min()
        if cam.max() != 0:
            cam /= cam.max()

        cam_np = cam.cpu().numpy()

        # Resize activation map to original image size
        orig_w, orig_h = orig_img.size

        if cv2 is not None:
            cam_resized = cv2.resize(cam_np, (orig_w, orig_h))
        else:
            # Use PIL for resizing
            cam_img = Image.fromarray(np.uint8(cam_np * 255))
            cam_img = cam_img.resize((orig_w, orig_h), Image.BILINEAR)
            cam_resized = np.array(cam_img).astype(np.float32) / 255.0

        # Create overlay
        orig_arr = np.array(orig_img).astype(np.uint8)

        try:
            overlay = _apply_colormap_on_image(orig_arr, cam_resized, alpha=0.45)
        except Exception:
            # Fallback: blend grayscale heatmap
            heatmap_rgb = np.stack([cam_resized * 255] * 3, axis=2).astype(np.uint8)
            overlay = (0.6 * orig_arr + 0.4 * heatmap_rgb).astype(np.uint8)

        # Save overlay
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(overlay).save(str(output_path))

        # Build result
        result = {
            "predicted_class_index": class_index,
            "confidence": conf_item,
            "heatmap_path": str(output_path),
        }

        # Try to map index to class name if available
        try:
            names = getattr(model, 'names', None)
            if names and int(class_index) in names:
                result['predicted_class'] = names[int(class_index)]
            else:
                # names might be a dict mapping ints to names
                if isinstance(names, (list, tuple)) and len(names) > class_index:
                    result['predicted_class'] = names[class_index]
        except Exception:
            pass

        return result

    finally:
        # Remove hooks
        try:
            fh.remove()
        except Exception:
            pass
        try:
            bh.remove()
        except Exception:
            pass


def explain_prediction(model: YOLO, image_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Helper wrapper: runs generate_gradcam and stores results under runs/xai/<category>/
    Category is inferred from model class names.
    """

    # Infer category
    model_names = getattr(model, 'names', None)
    category = 'other'
    if model_names:
        # model_names may be dict or list
        names_list = list(model_names.values()) if isinstance(model_names, dict) else list(model_names)
        if any(n in DISEASE_CLASSES for n in names_list):
            category = 'disease'
        elif any(n in PEST_CLASSES for n in names_list):
            category = 'pest'

    if output_dir is None:
        output_dir = Path('runs') / 'xai' / category
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Create a filename based on input image
    img_name = Path(image_path).stem
    out_path = output_dir / f"{img_name}_gradcam.png"

    return generate_gradcam(model, image_path, str(out_path))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate Grad-CAM for YOLOv8 classification models')
    parser.add_argument('--model', type=str, help='Path to YOLO weights or empty to use project disease model', default='')
    parser.add_argument('--image', type=str, required=True, help='Path to input image')
    parser.add_argument('--out', type=str, default='', help='Output path (optional)')
    parser.add_argument('--class_index', type=int, default=None, help='Target class index (optional)')

    args = parser.parse_args()

    # If no model provided, attempt to load project disease model
    if args.model:
        yolo = YOLO(args.model)
    else:
        # Project default disease model path
        proj_root = Path(__file__).resolve().parents[1]
        disease_path = proj_root / 'runs' / 'classify' / 'disease_yolov8n' / 'weights' / 'best.pt'
        if not disease_path.exists():
            raise SystemExit(f"No model specified and default disease model not found at {disease_path}")
        yolo = YOLO(str(disease_path))

    out_path = args.out if args.out else None
    if out_path is None:
        # will be placed under runs/xai/disease or pest by explain_prediction
        res = explain_prediction(yolo, args.image)
    else:
        res = generate_gradcam(yolo, args.image, out_path, target_class=args.class_index)

    print(res)
