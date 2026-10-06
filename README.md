# ChickenpoxAI

ChickenpoxAI is a research and learning demonstration for image classification. Its FastAPI inference path uses a local Ollama vision-language model to produce a best-guess label (`Healthy Skin` or `Chickenpox`) and a short visual observation. The project also retains the separate EfficientNet-B0 training/evaluation pipeline as an ML/DL experiment. Neither path is a medical diagnosis tool or guarantees accuracy.

## Overview

The project includes:

- A dataset preparation and analysis workflow
- A PyTorch transfer-learning pipeline with EfficientNet-B0 for ML/DL experiments
- Training, validation, and evaluation scripts
- A FastAPI backend using local Ollama/MedGemma vision inference
- A React + Vite frontend for uploading and analyzing images
- Optional Grad-CAM interpretability support
- English and Indonesian UI
- Clear medical disclaimer and best-guess labeling without invented confidence scores

## Project structure

```text
ChickenpoxAI/
├── dataset/
│   ├── train/
│   │   ├── healthy/
│   │   └── chickenpox/
│   ├── validation/
│   │   ├── healthy/
│   │   └── chickenpox/
│   └── test/
│       ├── healthy/
│       └── chickenpox/
├── training/
│   ├── analyze_dataset.py
│   ├── dataset.py
│   ├── train.py
│   ├── evaluate.py
│   ├── inference_test.py
│   └── requirements.txt
├── backend/
│   ├── main.py
│   ├── model.py
│   ├── preprocessing.py
│   ├── schemas.py
│   ├── config.py
│   ├── requirements.txt
│   └── models/
│       └── .gitkeep
├── frontend/
│   ├── src/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── .gitignore
├── results/
│   └── .gitkeep
├── README.md
├── .gitignore
└── .
```

## Dataset requirements

Place your real image dataset into the project root under the `dataset/` directory with class folders. Use a valid research dataset or a dataset you have permissions to use.

If your dataset looks like the one currently available at `D:\ChickenpoxAI\dataset\Monkeypox Skin Image Dataset`, note that it contains four folders:

- `Chickenpox`
- `Measles`
- `Monkeypox`
- `Normal`

For the binary ChickenpoxAI task, the cleanest mapping is:

- `Healthy Skin` = `Normal`
- `Chickenpox` = `Chickenpox`

The other classes (`Measles`, `Monkeypox`) should be ignored for the first version unless you explicitly want a wider multi-class disease model.

You can prepare the project-ready structure with:

```bash
cd training
python prepare_dataset.py --source "D:\ChickenpoxAI\dataset\Monkeypox Skin Image Dataset" --target "D:\ChickenpoxAI\dataset"
```

Recommended structure:

```text
dataset/
├── train/
│   ├── healthy/
│   └── chickenpox/
├── validation/
│   ├── healthy/
│   └── chickenpox/
└── test/
    ├── healthy/
    └── chickenpox/
```

If your dataset is not already divided into train/validation/test folders, the training pipeline can perform a stratified split automatically from a root-level class directory structure.

## Installation

### Python training and backend

```bash
cd training
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cd ../backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

### Local GenAI runtime

Install Ollama for Windows from [ollama.com/download/windows](https://ollama.com/download/windows), then open a new terminal and download the configured local vision model:

```powershell
ollama pull medgemma:4b
```

Ollama serves its local API at `http://127.0.0.1:11434`. The app sends uploaded images only to this local service; it does not send them to a cloud model. The configured MedGemma 4B vision model is intended for developer experimentation with medical text and images. Its license is governed by the [Health AI Developer Foundations terms](https://developers.google.com/health-ai-developer-foundations/terms). This laptop has 4 GB reported GPU memory, so inference may use system memory and be slower.

## Dataset preparation

Review and organize the dataset first.

```bash
cd training
python analyze_dataset.py
```

This script checks:

- total image count
- class counts
- train/validation/test counts
- image format and size
- corrupted files
- duplicate files
- class distribution
- output summary and optional plots

If the dataset is not split yet, run:

```bash
python train.py --prepare-only
```

## Training

```bash
cd training
python train.py
```

Key training defaults:

- model: EfficientNet-B0
- image size: 224x224
- batch size: 32
- learning rate: 1e-4
- optimizer: AdamW
- loss: CrossEntropyLoss
- scheduler: ReduceLROnPlateau
- epochs: 20-30
- early stopping: enabled

The model saves the best checkpoint to:

```text
backend/models/chickenpox_model_best.pth
```

## Evaluation

```bash
cd training
python evaluate.py
```

This computes:

- accuracy
- precision
- recall
- F1-score
- sensitivity
- specificity
- balanced accuracy
- ROC-AUC (if supported)
- confusion matrix
- classification report

It stores plots in `results/`.

## EfficientNet ML/DL experiment

The trained EfficientNet checkpoint and scripts remain available for research comparison. They are not used by the active FastAPI prediction route.

Run the existing image helper:

```bash
cd training
python inference_test.py --image path/to/example.jpg
```

## Backend (FastAPI)

First ensure Ollama is running and `medgemma:4b` has been pulled.

Start the API:

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open the docs:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### API endpoints

#### `GET /health`

Returns:

```json
{
  "status": "ok",
  "vision_model_available": true
}
```

#### `POST /predict`

Send a file with form-data key `image` and optional `language` (`id` or `en`).

Example response:

```json
{
  "prediction": "Chickenpox",
  "visual_observation": "Deskripsi visual singkat; tampilan visual saja tidak dapat memastikan penyakit.",
  "model": "medgemma:4b",
  "status": "estimate"
}
```

The vision-language model returns a best-guess label and a short visual observation. It does not return a confidence percentage. A guess may be wrong, especially for unclear images.

## Frontend (React + Vite)

Start the frontend:

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

Open the app at:

```text
http://localhost:5173
```

### Frontend features

- image upload
- preview before analysis
- loading state
- best-guess prediction and visual observation
- Indonesian and English language toggle
- analyze-another-image reset flow
- responsive layout
- medical disclaimer block

## Grad-CAM (optional)

The project includes optional interpretability logic. If a valid model checkpoint is available and the Grad-CAM module is enabled, the app can highlight likely areas of interest in the image. The visualized activation is not a clinical diagnosis and should be interpreted as model interpretability data only.

## Important notes

- Do not train on the test set.
- Keep train/validation/test disjoint.
- Prevent duplicate images across splits.
- Report class imbalance clearly.
- Use the test set only for final evaluation.
- The project is for research and educational use only.

## ML, DL, and GenAI

- ML is the broad field; deep learning is a subset of ML.
- Many GenAI systems, including vision-language models, are built using deep learning.
- In this project, EfficientNet is the retained ML/DL experiment, while Ollama/MedGemma is the active local GenAI image interpretation path.
- GenAI does not inherently improve accuracy; outputs can hallucinate and should not be treated as verified diagnoses.

## Medical disclaimer

> ChickenpoxAI is an AI-based image classification system developed for research and educational purposes. Its output is a model-generated visual estimate, not a medical diagnosis. Similar skin appearances may occur in different conditions. Consult a qualified healthcare professional for clinical evaluation.

## Limitations

- model quality depends on dataset quality and label correctness
- performance may degrade on blurry, low-contrast, or atypical images
- the system is not intended to replace professional diagnosis
- the GenAI result is a best guess, not a calibrated probability or guarantee of accuracy
- no user image metadata or personal identity is stored by default

## License

Use this project only with datasets and assets that you are authorized to use. Ensure the dataset licensing and provenance are reviewed before training or sharing results.
