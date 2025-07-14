from fastapi import FastAPI, File, UploadFile, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
import numpy as np
import tensorflow as tf
import io
from ultralytics import YOLO
import torch
import glob
app = FastAPI()

# Allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from fastapi.staticfiles import StaticFiles
app.mount("/runs", StaticFiles(directory="runs"), name="runs")
# Load model
model = tf.keras.models.load_model("model.h5")
class_names = ["Box", "Paper", "Plastic"]

# Load YOLO model once at startup
yolo_model = YOLO("best.pt")
yolo_wrapper_classes = ['plastic', 'paper', 'box']
yolo_defect_classes = ['stain', 'torn', 'wet', 'shrink']

@app.get("/")
async def root():
    return {"message": "API is running"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    image = image.resize((224, 224))  # Use your model's input size
    img_array = np.array(image) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    predictions = model.predict(img_array)
    predicted_class = class_names[np.argmax(predictions[0])] # or your custom logic
    # confidence = float(np.max(predictions))

    return {"class": predicted_class}

# --- Add this section below ---

class PointsRequest(BaseModel):
    material: str
    damage_data: dict

def classify_damage(damage_percent):
    if damage_percent <= 30:
        return 'A'
    elif damage_percent < 50:
        return 'B'
    else:
        return 'C'

def calculate_total_points(material, damage_data):
    material = material.lower()
    points = {
        "wrapper": {
            "torn": {"A": 50, "B": 20, "C": 0},
            "stain": {"A": 20, "B": 10, "C": 0},
            "wet": {"A": 20, "B": 10, "C": 0},
            "burnt": {"A": 0, "B": 0, "C": 0},
            "shrink": {"A": 30, "B": 20, "C": 0}
        },
        "paper": {
            "torn": {"A": 30, "B": 10, "C": 0},
            "stain": {"A": 10, "B": 0, "C": 0},
            "wet": {"A": 10, "B": 0, "C": 0},
            "burnt": {"A": 0, "B": 0, "C": 0},
            "shrink": {"A": 30, "B": 10, "C": 0}
        },
        "plastic": {
            "torn": {"A": 10, "B": 0, "C": 0},
            "stain": {"A": 10, "B": 0, "C": 0},
            "wet": {"A": 30, "B": 10, "C": 0},
            "burnt": {"A": 0, "B": 0, "C": 0},
            "shrink": {"A": 50, "B": 20, "C": 0}
        }
    }

    if material not in points:
        return {"error": "Invalid material"}

    total_score = 0
    detail_scores = {}

    for damage_type, percent in damage_data.items():
        damage_type = damage_type.lower()
        if damage_type not in points[material]:
            detail_scores[damage_type] = "Invalid damage type"
            continue

        damage_class = classify_damage(percent)
        score = points[material][damage_type][damage_class]
        total_score += score
        detail_scores[damage_type] = {
            "percent": percent,
            "class": damage_class,
            "points": score
        }

    return {"total_score": total_score, "details": detail_scores}

@app.post("/calculate_points")
async def calculate_points(request: PointsRequest):
    result = calculate_total_points(request.material, request.damage_data)
    return result

@app.post("/detect_defects")
async def detect_defects(file: UploadFile = File(...)):
    contents = await file.read()
    # Save to a temporary file or use BytesIO
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_img:
        temp_img.write(contents)
        temp_img_path = temp_img.name

    try:
        results = yolo_model.predict(
            source=temp_img_path,
            conf=0.05,
            save=True
        )
        r = results[0]
        class_pixel_counts = {}
        if hasattr(results[0], 'save_dir'):
    # Find the saved image in the directory
       
            files = glob.glob(str(results[0].save_dir) + "/*.jpg")
            if files:
                saved_img_path = files[0].replace("\\", "/") 

        if r.masks is not None:
            mask_array = r.masks.data.cpu().numpy()
            classes = r.boxes.cls.cpu().numpy().astype(int)
            for idx, cls_idx in enumerate(classes):
                class_name = yolo_model.names[cls_idx]
                mask_pixels = mask_array[idx].sum()
                if class_name not in class_pixel_counts:
                    class_pixel_counts[class_name] = 0
                class_pixel_counts[class_name] += mask_pixels

        wrapper_area = sum(
            class_pixel_counts.get(cls, 0) for cls in yolo_wrapper_classes
        )
        percentages = {}
        for defect in yolo_defect_classes:
            defect_area = class_pixel_counts.get(defect, 0)
            pct = (defect_area / wrapper_area * 100) if wrapper_area > 0 else 0.0
            percentages[defect] = pct

        # Convert all numpy types to Python native types for JSON serialization
        percentages_py = {k: float(v) for k, v in percentages.items()}
        class_pixel_counts_py = {k: int(v) for k, v in class_pixel_counts.items()}
        wrapper_area_py = int(wrapper_area)

        return {
            "wrapper_area": wrapper_area_py,
            "defect_percentages": percentages_py,
            "pixel_counts": class_pixel_counts_py,
            "masked_image_path": saved_img_path.replace("C:/Users/Archana/Desktop/ProjectPackage/app/", "") if saved_img_path else None
            
        }
    finally:
        os.remove(temp_img_path)
