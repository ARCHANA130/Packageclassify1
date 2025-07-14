# Package & Damage Detection Project

## Overview

This project consists of a React frontend and a FastAPI backend for package material classification, damage detection, and points calculation. The backend uses a TensorFlow model for material classification and a YOLO model for defect segmentation.

---

## Backend Setup (FastAPI + TensorFlow + YOLO)

### 1. Install Dependencies

```bash
pip install fastapi uvicorn pillow numpy tensorflow ultralytics
```

### 2. Project Structure

```
app/
  main.py
  model.h5           # TensorFlow classification model
  best.pt            # YOLO segmentation model
  runs/              # YOLO output images (auto-created)
```

### 3. Run the Backend

```bash
cd app
uvicorn main:app --reload
```

- The API will be available at `http://127.0.0.1:8000/`
- Endpoints:
  - `/predict` : Classify package material
  - `/detect_defects` : Detect and segment defects, returns defect percentages and masked image path
  - `/calculate_points` : Calculate points based on detected defects
  - `/runs/...` : Serves YOLO output images

### 4. Notes

- Ensure `model.h5` and `best.pt` are present in the `app` folder.
- The backend automatically serves images from the `runs` directory.

---

## Frontend Setup (React)

### 1. Install Dependencies

```bash
cd frontend
npm install
npm install react-confetti
```

### 2. Project Structure

```
frontend/
  src/
    App.js
    App.css
  public/
    index.html
  package.json
```

### 3. Run the Frontend

```bash
npm start
```

- The frontend will be available at `http://localhost:3000/`

### 4. Features

- Upload an image of a package.
- The app calls the backend to:
  - Classify the material.
  - Detect defects and get defect percentages.
  - Calculate points based on detected damage.
  - Display results, points, and the detected masked image in a popup.

---

## Usage Steps

1. **Start the backend server** (`uvicorn main:app --reload`).
2. **Start the frontend** (`npm start`).
3. **Open the frontend in your browser** (`http://localhost:3000/`).
4. **Upload a package image** and view the results, points, and detected mask.

---

## Troubleshooting

- If you get a 404 for images, ensure the backend is serving the `runs` directory and the image path is correct.
- If you see serialization errors, make sure all NumPy types are converted to Python types before returning from the backend.
- For git errors, run git commands from the project root (where `.git` exists).

---

## Credits

- Frontend: React, styled with CSS.
- Backend: FastAPI, TensorFlow,