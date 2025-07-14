#!/usr/bin/env python3

import argparse
from ultralytics import YOLO
import numpy as np
import matplotlib.pyplot as plt

def main(img_path):
    # -----------------------------
    # 1. Load model
    # -----------------------------
    model_path = r"best.pt"
  # adjust if needed
    model = YOLO(model_path)
    print("Loaded model classes:", model.names)

    # -----------------------------
    # 2. Predict on user image
    # -----------------------------
    results = model.predict(
        source=img_path,
        conf=0.05,
        save=True
    )

    r = results[0]

    # -----------------------------
    # 3. Calculate defect percentages
    # -----------------------------
    class_pixel_counts = {}

    if r.masks is not None:
        mask_array = r.masks.data.cpu().numpy()
        classes = r.boxes.cls.cpu().numpy().astype(int)

        for idx, cls_idx in enumerate(classes):
            class_name = model.names[cls_idx]
            mask_pixels = mask_array[idx].sum()

            if class_name not in class_pixel_counts:
                class_pixel_counts[class_name] = 0

            class_pixel_counts[class_name] += mask_pixels

        print("Pixel counts per class:", class_pixel_counts)

    else:
        print("No masks detected in the image.")

    # Define wrapper and defect classes
    wrapper_classes = ['plastic', 'paper', 'box']
    defect_classes = ['stain', 'torn', 'wet', 'shrink']

    # Calculate wrapper area
    wrapper_area = sum(
        class_pixel_counts.get(cls, 0) for cls in wrapper_classes
    )
    print(f"Total wrapper area (pixels): {wrapper_area}")

    # Calculate defect percentages
    percentages = {}
    for defect in defect_classes:
        defect_area = class_pixel_counts.get(defect, 0)
        pct = (defect_area / wrapper_area * 100) if wrapper_area > 0 else 0.0
        percentages[defect] = pct

    for defect, pct in percentages.items():
        print(f"{defect}: {pct:.2f}% of wrapper area")

    # -----------------------------
    # 4. Show the image
    # -----------------------------
    if len(r.boxes) > 0:
        plt.imshow(r.plot())
    else:
        print("No detections — showing raw image.")
        plt.imshow(r.orig_img[..., ::-1])
    plt.axis('off')
    plt.show()

# ----------------------------------------
# Entry point for command-line execution
# ----------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict defects on a wrapper image.")
    parser.add_argument(
        "--image",
        type=str,
        required=True,
        help="Path to your test image"
    )
    args = parser.parse_args()
    main(args.image)
