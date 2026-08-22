"""
Router evaluation script - measures exactly the breakdown requested:

    disease   -> disease / pest / non_grape / UNCERTAIN
    pest      -> disease / pest / non_grape / UNCERTAIN
    non_grape -> disease / pest / non_grape / UNCERTAIN

WHY THIS EXISTS
-------------------------------------------------------------------------
Top-1 accuracy on the router's own test split (dataset/router/test/) only
tells you how well it re-recognizes images from the same source/style it
trained on. It does NOT tell you whether the "confidently wrong" problem
you reported is fixed. To find that out, you need a held-out folder of
images the model has never seen in ANY form (not train, not val, not
test) - ideally gathered from different sources than your original
dataset - evaluated with the real decision logic from
predict_router_v2.py (not raw top-1).

EXPECTED FOLDER LAYOUT for --test-dir:

    <test-dir>/
        grape_disease/   (images you know are grape disease)
        grape_pest/      (images you know are grape pest)
        non_grape/       (images you know are not grape at all)

USAGE
    python evaluate_router.py --model runs/classify/router_yolov8n_v2/weights/best.pt --test-dir dataset/unseen_test

Run this once per model (v1 and v2) against the SAME unseen folder to
get a fair, apples-to-apples comparison - see the printed summary at
the end for how to read the result.
"""

import argparse
from pathlib import Path

from predict_router_v2 import CLASS_NAMES, load_router, predict_image

OUTCOME_COLUMNS = ("grape_disease", "grape_pest", "non_grape", "UNCERTAIN")
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def gather_images(folder: Path):
    return sorted(p for p in folder.iterdir() if p.suffix.lower() in IMAGE_EXTS)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="Path to router .pt weights")
    parser.add_argument(
        "--test-dir",
        required=True,
        help="Folder with grape_disease/, grape_pest/, non_grape/ subfolders of UNSEEN images",
    )
    args = parser.parse_args()

    model_path = Path(args.model)
    test_dir = Path(args.test_dir)

    model = load_router(model_path)

    # counts[true_class][predicted_outcome] = count
    counts = {c: {o: 0 for o in OUTCOME_COLUMNS} for c in CLASS_NAMES}
    totals = {c: 0 for c in CLASS_NAMES}

    for true_class in CLASS_NAMES:
        class_dir = test_dir / true_class
        if not class_dir.exists():
            print(f"WARNING: missing folder {class_dir}, skipping.")
            continue

        images = gather_images(class_dir)
        totals[true_class] = len(images)

        for img_path in images:
            decision, _info = predict_image(model, str(img_path))
            counts[true_class][decision] += 1

    # ---- Print confusion table ----
    print("=" * 78)
    print(f"Model: {model_path}")
    print(f"Test dir: {test_dir}")
    print("=" * 78)

    header = f"{'TRUE CLASS':<16}" + "".join(f"{c:>16}" for c in OUTCOME_COLUMNS) + f"{'TOTAL':>8}"
    print(header)
    print("-" * len(header))
    for true_class in CLASS_NAMES:
        row = f"{true_class:<16}"
        for outcome in OUTCOME_COLUMNS:
            row += f"{counts[true_class][outcome]:>16}"
        row += f"{totals[true_class]:>8}"
        print(row)

    print("\n" + "=" * 78)
    print("KEY SAFETY METRICS")
    print("=" * 78)

    def rate(true_class, outcome):
        t = totals[true_class]
        return (counts[true_class][outcome] / t * 100) if t else float("nan")

    print(f"disease   -> disease   (correct)      : {rate('grape_disease','grape_disease'):.1f}%")
    print(f"disease   -> pest      (DANGEROUS)     : {rate('grape_disease','grape_pest'):.1f}%")
    print(f"disease   -> UNCERTAIN (safe reject)   : {rate('grape_disease','UNCERTAIN'):.1f}%")
    print()
    print(f"pest      -> pest      (correct)      : {rate('grape_pest','grape_pest'):.1f}%")
    print(f"pest      -> disease   (DANGEROUS)     : {rate('grape_pest','grape_disease'):.1f}%")
    print(f"pest      -> UNCERTAIN (safe reject)   : {rate('grape_pest','UNCERTAIN'):.1f}%")
    print()
    print(f"non_grape -> non_grape (correct)      : {rate('non_grape','non_grape'):.1f}%")
    print(f"non_grape -> disease   (DANGEROUS)     : {rate('non_grape','grape_disease'):.1f}%")
    print(f"non_grape -> pest      (DANGEROUS)     : {rate('non_grape','grape_pest'):.1f}%")
    print(f"non_grape -> UNCERTAIN (safe reject)   : {rate('non_grape','UNCERTAIN'):.1f}%")

    print("\n" + "=" * 78)
    print("HOW TO JUDGE 'genuinely better' (not just higher Top-1)")
    print("=" * 78)
    print(
        "Run this script against the SAME unseen folder for both\n"
        "router_yolov8n (v1) and router_yolov8n_v2 (v2), then compare:\n\n"
        "  1. The three DANGEROUS rows must go DOWN in v2. These are the\n"
        "     'confidently wrong' cases you reported - a threshold cannot\n"
        "     fix these, only better-learned features can.\n"
        "  2. Some UNCERTAIN rate INCREASE is expected and fine - it means\n"
        "     genuinely ambiguous images are being rejected instead of\n"
        "     forced into a class, which was requirement #12.\n"
        "  3. If DANGEROUS rows do not drop, the fix is not augmentation\n"
        "     parameters - it means the two source datasets (disease vs\n"
        "     pest images) differ systematically enough (background,\n"
        "     camera, lighting) that no amount of augmentation can fully\n"
        "     compensate, and new unseen images should be added directly\n"
        "     to router training data with a similar look to your real\n"
        "     deployment conditions."
    )


if __name__ == "__main__":
    main()
