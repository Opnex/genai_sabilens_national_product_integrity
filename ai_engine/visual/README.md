# Vision Intelligence

## Overview

This module implements the **Vision Intelligence Layer** of the SabiLens system.

Its responsibility is to visually verify whether a scanned consumer product
matches an authentic reference product using computer vision.

The system performs:

- Region detection using **YOLOv8**
- Feature extraction using **ResNet50 embeddings**
- Similarity comparison with authentic reference products
- Packaging damage detection
- Authenticity confidence estimation

This component outputs a **visual authenticity verdict** that is later fused with
OCR and knowledge-based reasoning in the SabiLens architecture.

---

# System Architecture
Product Image
↓
YOLO Region Detector
(logo, barcode, expiry, brand colors)

↓

CNN Feature Extractor
(ResNet50)

↓

Embedding Generator

↓

Similarity Engine
(cosine similarity with reference embeddings)

↓

Damage Detection
(packaging blur / degradation)

↓

Confidence Fusion

↓

Authentic | Suspicious | Fake


---

# Project Structure
AI_Engineer_1/

vision_engine/
│
├── models/
│ └── feature_extractor.py
│
├── similarity/
│ └── similarity_engine.py
│
├── regions/
│ ├── region_detector.py
│ └── region_cropper.py
│
├── embeddings/
│ └── generate_embeddings.py
│
├── pipeline/
│ └── visual_pipeline.py
│

reference_dataset/ # authentic product images

test_images/ # images for testing

test_similarity.py
test_visual_pipeline.py
test_region_detector.py

data.yaml
requirements.txt


---

# Key Components

## 1. Reference Dataset

Authentic product images collected from multiple views:

- front
- back
- left
- right
- top
- bottom

These serve as the **ground truth visual references**.

---

## 2. Feature Extraction

A **ResNet50 CNN model** is used to extract visual embeddings from images.
image → ResNet50 → feature vector (embedding)


These embeddings represent the visual characteristics of authentic packaging.

---

## 3. Embedding Database

All reference embeddings are stored in:
reference_embeddings.pkl


This enables **fast similarity comparison** during inference.

---

## 4. Region Detection

A **YOLOv8 detector** identifies important packaging areas:

- brand logo
- barcode
- expiry date
- brand colors
- NAFDAC number

This focuses the similarity comparison on **critical visual regions**.

---

## 5. Similarity Engine

The extracted embeddings are compared against the reference database using:
cosine similarity.


The system identifies the **closest matching authentic product**.

---

## 6. Damage Detection

Packaging integrity is evaluated using a blur-based damage score:
damage_score ∈ [0,1]


Higher values indicate **possible tampering or degradation**.

---

## 7. Confidence Fusion

Visual similarity and damage score are combined to compute an authenticity confidence:
confidence = similarity × (1 − damage_score)


Final classification:

| Confidence | Verdict |
|-------------|--------|
| > 0.6 | Authentic |
| 0.3 – 0.6 | Suspicious |
| < 0.3 | Fake |

---

# Example Output

Final classification:

| Confidence | Verdict |
|-------------|--------|
| > 0.6 | Authentic |
| 0.3 – 0.6 | Suspicious |
| < 0.3 | Fake |

---

# Example Output
================ SABILENS VISUAL INSPECTION ================

Detected Product Match : Golden_terra_soya_oil_5L

Visual Similarity Score: 0.256
Damage Score : 0.4
Authenticity Confidence: 0.154

FINAL VERDICT: FAKE

============================================================


---

# Installation

Create a virtual environment and install dependencies.
