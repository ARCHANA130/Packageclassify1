from fastapi import FastAPI, File, UploadFile, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
import numpy as np
import tensorflow as tf
import io

app = FastAPI()

# Allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model
model = tf.keras.models.load_model("model.h5")
class_names = ["Box", "Paper", "Plastic"]

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
