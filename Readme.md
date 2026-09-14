# 🍇 Early Pest Infestation Detection System

## Machine Learning Based Grape Disease and Pest Detection

Early Pest Infestation Detection System is an image-based machine learning system developed to assist in the early identification of grape leaf diseases and pest infestations.

The system accepts an image through a web-based interface and uses an AI-based routing mechanism to determine whether the uploaded image belongs to a grape disease, grape pest, non-grape, or uncertain category. Based on the router decision, the image is directed to the appropriate specialized classification model.

The system provides the predicted class, confidence score, Grad-CAM visual explanation, management guidance when available, and detection history through an interactive dashboard.

---

# 📌 Project Overview

Grape cultivation can be affected by different diseases and pest infestations that can reduce crop health, quality, and yield.

Traditional identification methods generally depend on manual observation and expert knowledge. This can be time-consuming and may not always be accessible to all users.

The Early Pest Infestation Detection System provides an automated image-based approach for identifying grape leaf diseases and pest infestations.

The system combines:

- Machine Learning
- Image Classification
- AI-based Image Routing
- Explainable AI
- Grad-CAM
- FastAPI
- React
- Detection History
- Management Guidance
- Interactive Dashboard

---

# 🎯 Problem Statement

Early identification of grape diseases and pest infestations is important for reducing crop damage and supporting timely management.

Manual identification can be difficult because it depends on visual inspection and agricultural expertise. Similar symptoms can also make identification challenging.

Therefore, there is a need for an image-based intelligent system that can analyze grape leaf images and automatically identify possible diseases or pest infestations.

---

# 🎯 Objectives

The main objectives of the Early Pest Infestation Detection System are:

1. To develop an image-based machine learning system for identifying grape leaf diseases.

2. To develop a machine learning classification model for identifying supported grape pest categories.

3. To implement an AI-based router that determines whether an uploaded image belongs to grape disease, grape pest, non-grape, or uncertain categories.

4. To automatically route grape disease images to the disease classification model.

5. To automatically route grape pest images to the pest classification model.

6. To provide the predicted class along with its confidence score.

7. To integrate Grad-CAM Explainable AI for visualizing the image regions that contributed to a prediction.

8. To provide management and treatment guidance when information is available.

9. To develop a user-friendly web application for image upload and prediction.

10. To maintain detection history so that previous analyses can be reviewed.

---

# ⭐ Key Features

## 🍃 Disease Detection

The system uses a trained image classification model to identify supported grape leaf disease categories.

## 🐞 Pest Detection

The system uses a separate classification model for identifying supported grape pest categories.

## 🧠 AI Router

The AI router is used before the specialized classifiers.

The router categorizes an uploaded image into:

- Grape Disease
- Grape Pest
- Non-Grape
- Uncertain

This helps prevent unrelated images from being directly processed by the disease or pest classification models.

## 📊 Confidence Score

The system displays the confidence associated with the predicted class.

## 🔥 Explainable AI

Grad-CAM is integrated to generate a heatmap showing the image regions that contributed most to the model's prediction.

## 📋 Detection History

Completed detection results can be stored and reviewed through the dashboard.

## 💊 Management Guidance

The system can display management and treatment information associated with the predicted condition when information is available in the treatment database.

## 📊 Dashboard

The dashboard provides:

- Disease class information
- Pest class information
- Model performance
- System status
- Detection history
- Workflow information

---

# 🔄 System Workflow

```text
                  ┌───────────────────────┐
                  │     User Uploads      │
                  │        Image          │
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │      AI Router        │
                  └───────────┬───────────┘
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
      Grape Disease      Grape Pest        Non-Grape
             │                │                │
             ▼                ▼                ▼
      Disease Model       Pest Model         Reject
             │                │
             └────────┬───────┘
                      │
                      ▼
               Predicted Class
                      │
                      ▼
               Confidence Score
                      │
             ┌────────┴────────┐
             │                 │
             ▼                 ▼
          Grad-CAM        Management
         Explanation       Guidance
             │                 │
             └────────┬────────┘
                      ▼
                Final Result
                      │
                      ▼
              Detection History

              # 🏗️ System Architecture

```text
                         IMAGE INPUT
                              │
                              ▼
                    ┌─────────────────┐
                    │    FastAPI      │
                    │     Backend     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    AI Router    │
                    └────────┬────────┘
                             │
             ┌───────────────┼───────────────┐
             │               │               │
             ▼               ▼               ▼
       Grape Disease     Grape Pest      Non-Grape
             │               │
             ▼               ▼
      Disease Model      Pest Model
             │               │
             └───────┬───────┘
                     │
                     ▼
              Prediction Result
                     │
          ┌──────────┼──────────┐
          │          │          │
          ▼          ▼          ▼
     Confidence   Grad-CAM   Guidance
          │          │          │
          └──────────┼──────────┘
                     │
                     ▼
                Web Dashboard
                     │
                     ▼
              Detection History
              # 🧠 AI Router

The AI Router is the first decision-making stage of the system.

Instead of directly sending every uploaded image to a disease or pest model, the router first determines the category of the image.

The router categorizes an uploaded image into:

- Grape Disease
- Grape Pest
- Non-Grape
- Uncertain

This helps ensure that the uploaded image is sent to the appropriate specialized classification model.

## Router Process

```text
Input Image
     │
     ▼
 AI Router
     │
     ├── Grape Disease ──► Disease Model
     │
     ├── Grape Pest ─────► Pest Model
     │
     ├── Non-Grape ───────► Reject
     │
     └── Uncertain ───────► Reject / Request another image

     # 🍃 Disease Classification Model

The disease classification component uses **YOLOv8n Classification** to identify supported grape leaf disease categories.

## Training Configuration

| Parameter | Value |
|---|---|
| Model | YOLOv8n Classification |
| Task | Image Classification |
| Image Size | 224 × 224 |
| Epochs | 30 |
| Batch Size | 16 |
| Transfer Learning | Enabled |

## Disease Model Performance

**Top-1 Test Accuracy: 99.77%**

The accuracy was obtained using the held-out test dataset during project evaluation.
# 🐞 Pest Classification Model

The pest classification component uses a separate machine learning classification model to identify supported grape pest categories.

## Pest Model Performance

**Top-1 Test Accuracy: 90.95%**

The accuracy was obtained using the held-out test dataset during project evaluation.
# 🔥 Explainable AI — Grad-CAM

The system integrates **Grad-CAM (Gradient-weighted Class Activation Mapping)** to provide a visual explanation of the classification model's prediction.

Grad-CAM generates a heatmap that highlights the important regions of the input image that contributed to the model's prediction.

## Grad-CAM Process

```text
Original Image
      │
      ▼
Classification Model
      │
      ▼
Predicted Class
      │
      ▼
Grad-CAM
      │
      ▼
Heatmap Explanation
# 📊 Dataset

The project uses multiple image datasets and dataset sources for different components of the system.

## 1. Grapevine Leaf Variety & Disease Dataset (GLVD)

The GLVD dataset was used for the grape leaf disease classification component.

### Dataset Source

**Zenodo:**

https://zenodo.org/records/18937397

### Disease Classes

- Bacterial Rot
- Black Measles
- Black Rot
- Downy Mildew
- Healthy Leaves
- Leaf Blight
- Powdery Mildew

## 2. Classification Dataset

A classification dataset stored through Google Drive was also used during project development.

### Dataset Source

**Google Drive:**

https://drive.google.com/drive/folders/1ntmFAYessXYRLl8yuD_sPqdyPRtzxwyz?usp=drive_link

The dataset is maintained separately from the GitHub repository because large image datasets are not stored directly in the repository.

## 3. PlantVillage Dataset

The PlantVillage dataset was used as an additional dataset source during project development. Relevant grape-related images were used for the project.

### Dataset Source

**Kaggle:**

https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset

> Dataset usage is subject to the licensing and terms of the respective dataset providers.

# 🛠️ Data Preprocessing

The image data is organized into class-wise directories before model training.

## Preprocessing Workflow

```text
Raw Dataset
     │
     ▼
Dataset Inspection
     │
     ▼
Class-wise Organization
     │
     ▼
Train / Validation / Test Split
     │
     ▼
Image Resizing
     │
     ▼
Model Training
     │
     ▼
Model Evaluation
# 💊 Management Guidance

The system includes a Python-based management and treatment database:

```text
data/treatment_database.py
# 🌐 Web Application

The Early Pest Infestation Detection System provides a user-friendly web application developed using React.

## 🏠 Landing Page

Provides an introduction to the system and access to the detection workflow.

## 🔍 Detection Page

Allows users to upload an image and receive the prediction result.

## 📊 Dashboard

The dashboard provides:

- Disease and pest information
- Model performance
- System status
- Detection history
- Workflow information

## 📋 Detection History

Allows users to review previously completed detection results.

## ❓ Help Page

Provides information about:

- Image uploading
- Confidence scores
- Detection results
- System usage
- Management guidance

## ℹ️ About Page

Provides information about the project, its purpose, and the technologies used.
# 🔄 Complete Detection Process

When a user uploads an image:

1. The user uploads an image through the web application.
2. FastAPI receives the uploaded image.
3. The AI Router analyzes the image.
4. The router determines whether the image belongs to grape disease, grape pest, non-grape, or uncertain category.
5. If the image is classified as grape disease, it is sent to the Disease Model.
6. If the image is classified as grape pest, it is sent to the Pest Model.
7. The selected model generates the predicted class.
8. The confidence score is calculated and displayed.
9. Grad-CAM generates a visual explanation when available.
10. Management guidance is retrieved when available.
11. The final result is displayed in the web application.
12. The detection result can be reviewed through the detection history.

# 📈 Results

The current project evaluation reports the following classification results:

| Model | Top-1 Test Accuracy |
|---|---:|
| Disease Model | **99.77%** |
| Pest Model | **90.95%** |

These values represent the test results obtained during project evaluation.

## Important Note

Model accuracy does not guarantee correct predictions for every real-world image.

Prediction performance can be affected by:

- Image quality
- Lighting
- Background
- Camera quality
- Leaf orientation
- Image resolution
- Environmental conditions
- Differences between training and real-world images

Therefore, the system is intended as a **decision-support system**.
# 🧪 Model Evaluation

The project contains evaluation scripts for measuring the performance of the trained models.

Important evaluation files include:

```text
src/evaluate_disease.py
src/evaluate_pest.py
src/evaluate_router.py
src/evaluate_router_confusion.py
# 💻 Technology Stack

## Frontend

- React
- JavaScript
- Vite
- CSS

## Backend

- Python
- FastAPI
- Uvicorn

## Machine Learning

- Python
- Ultralytics
- YOLOv8 Classification
- PyTorch
- NumPy

## Explainable AI

- Grad-CAM

## Data and Configuration

- YAML
- JSON
- Python

## Development and Version Control

- Visual Studio Code
- Git
- GitHub

# 📂 Project Structure

```text
Pest-Detection/
│
├── data/
│   └── treatment_database.py
│
├── dataset/
│   └── config/
│       ├── disease.yaml
│       └── pest.yaml
│
├── frontend/
│   ├── public/
│   ├── photos/
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── assets/
│       ├── App.jsx
│       ├── App.css
│       ├── index.css
│       └── main.jsx
│
├── src/
│   ├── api.py
│   ├── predict.py
│   ├── predict_disease.py
│   ├── predict_pest.py
│   ├── predict_router.py
│   ├── predict_router_v2.py
│   ├── train_disease.py
│   ├── train_pest.py
│   ├── train_router.py
│   ├── train_router_v2.py
│   ├── evaluate_disease.py
│   ├── evaluate_pest.py
│   ├── evaluate_router.py
│   ├── evaluate_router_confusion.py
│   ├── xai.py
│   └── utils/
│
├── requirements.txt
├── .gitignore
└── README.md

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/Aqeeb11/Pest-Infestation-Detection-System.git
cd Pest-Infestation-Detection-System

2.python -m venv venv
3.venv\Scripts\activate
4.pip install -r requirements.txt

Frontend Setup

1.cd frontend
2.npm install
3.npm run dev

Start the Backend
python -m uvicorn src.api:app --reload --port 8000
# 🧠 Model Weights

The trained model weights are intentionally excluded from the GitHub repository to keep the repository lightweight.

Examples include:

```text
*.pt
*.pth

# 📦 Dataset Setup

The datasets are not stored directly inside the GitHub repository because of their size.

Users who want to reproduce the project should obtain the datasets from their original sources.

### GLVD Dataset — Zenodo

https://zenodo.org/records/18937397

### Classification Dataset — Google Drive

https://drive.google.com/drive/folders/1ntmFAYessXYRLl8yuD_sPqdyPRtzxwyz?usp=drive_link

### PlantVillage Dataset — Kaggle

https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset

Users should follow the licensing and usage requirements of each original dataset.
# 🔒 Repository & Data Policy

Large and generated files are intentionally excluded from the GitHub repository.

## Not Included

- Dataset images
- Raw datasets
- Router dataset images
- Trained `.pt` model weights
- `.pth` model files
- YOLO training outputs
- `runs/`
- `node_modules/`
- Python cache files
- Environment files

## Included

- Source code
- Frontend source
- FastAPI backend
- AI Router
- Training scripts
- Prediction scripts
- Evaluation scripts
- Grad-CAM implementation
- Treatment database
- Dataset configuration files
- Frontend assets
- Project documentation

This keeps the repository lightweight while preserving the main project implementation.
# ⚠️ Limitations

The current system has the following limitations:

1. The system can identify only the classes represented in the trained datasets.
2. Prediction quality depends on the quality of the uploaded image.
3. Real-world images may differ from the training data.
4. Poor lighting and complex backgrounds may affect prediction quality.
5. The model may produce incorrect predictions for unfamiliar images.
6. Management guidance is limited to the information available in the project's treatment database.
7. Trained model weights are not included in the GitHub repository.
8. Large datasets are not included in the GitHub repository.

# 🚀 Future Scope

Future improvements may include:

1. Expanding the disease dataset.
2. Adding more grape disease categories.
3. Adding more grape pest categories.
4. Collecting more real-world field images.
5. Improving performance under different lighting and environmental conditions.
6. Developing a mobile application.
7. Integrating real-time camera-based detection.
8. Adding multilingual support for farmers.
9. Expanding management and treatment recommendations.
10. Cloud deployment for remote access.
11. Integration with agricultural advisory systems.
12. Developing lightweight models for mobile and edge-device deployment.
13. Continuous model improvement using newly collected images.
# 🎓 Academic Significance

The Early Pest Infestation Detection System demonstrates the integration of machine learning, explainable artificial intelligence, and web application development into an agricultural decision-support system.

The project combines:

```text
Machine Learning
       +
Image Classification
       +
AI Routing
       +
Explainable AI
       +
FastAPI
       +
React
       +
Management Guidance
       +
Detection History

# 👨‍💻 Project Information

**Project Name:** Early Pest Infestation Detection System using ML

**Project Title:** Early Pest Infestation Detection System using ML

**Domain:** Machine Learning / Artificial Intelligence / Agriculture

**Application:** Grape Leaf Disease and Pest Detection

**Project Type:** Final-Year Engineering Project