# ChickenpoxAI

ChickenpoxAI is a local research and education demo for exploring skin-image classification. It includes a React web interface, a FastAPI service, and a locally running Ollama vision-language model. A separate EfficientNet-B0 training and evaluation pipeline is retained for machine-learning/deep-learning experiments.

> **Not a medical device:** The output is an AI-generated visual estimate, not a diagnosis, screening result, or treatment recommendation. It can be wrong. Do not use it to make health decisions; consult a qualified healthcare professional.

## Contents

- [What it does](#what-it-does)
- [How it works](#how-it-works)
- [Project layout](#project-layout)
- [Requirements](#requirements)
- [Run the application](#run-the-application)
- [Prepare a dataset](#prepare-a-dataset)
- [Train and evaluate EfficientNet](#train-and-evaluate-efficientnet)
- [API reference](#api-reference)
- [Privacy and safe use](#privacy-and-safe-use)
- [Troubleshooting](#troubleshooting)
- [License and third-party terms](#license-and-third-party-terms)

## What it does

- Accepts a skin image through a responsive English/Indonesian web interface.
- Shows a best-guess label (`Healthy Skin` or `Chickenpox`) and a brief observation of visible features.
- Runs image interpretation using Ollama and the local `medgemma:4b` model.
- Provides a separate PyTorch transfer-learning pipeline for training and evaluating EfficientNet-B0.
- Includes dataset analysis and optional Grad-CAM visualization for the EfficientNet experiment.

The active FastAPI `/predict` route uses MedGemma; it does **not** load the EfficientNet checkpoint. The web app reports a single best guess, not a calibrated confidence score or a guaranteed accuracy. GenAI can hallucinate, and visual similarity alone cannot establish the cause of a rash.

## How it works

```text
Browser (React + Vite)
        │ image upload
        ▼
FastAPI (localhost:8000)
        │ local HTTP request
        ▼
Ollama (localhost:11434) ── medgemma:4b
```

The separate EfficientNet experiment uses the following flow:

```text
Labeled dataset → dataset preparation → EfficientNet-B0 training
                                      → test-set evaluation
```

Training or evaluating EfficientNet does not change the model used by the active web prediction route.

## Project layout

```text
ChickenpoxAI/
├── backend/
│   ├── main.py                 # FastAPI endpoints
│   ├── model.py                # Local Ollama/MedGemma integration
│   ├── preprocessing.py        # Uploaded-image validation
│   ├── schemas.py              # API response schemas
│   ├── config.py               # Backend defaults
│   ├── requirements.txt
│   └── models/                 # Local EfficientNet checkpoints (not committed)
├── dataset/                    # Local image data (not committed)
│   ├── train/
│   ├── validation/
│   └── test/
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── results/                    # Generated reports and plots (not committed)
├── training/
│   ├── analyze_dataset.py
│   ├── dataset.py
│   ├── prepare_dataset.py
│   ├── train.py
│   ├── evaluate.py
│   ├── grad_cam.py
│   ├── inference_test.py
│   └── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

Dataset images, model checkpoints, generated plots, frontend build output, and installed frontend packages are excluded from Git by default. See [`.gitignore`](.gitignore).

## Requirements

- Windows, macOS, or Linux. Commands below use Windows PowerShell.
- Python 3.11 is the tested environment for the pinned Python dependencies.
- Node.js and npm, for the frontend.
- [Ollama](https://ollama.com/download) installed and running.
- Enough system memory and disk space for the `medgemma:4b` model. Inference may be slow on systems without sufficient GPU memory because some work can run on the CPU.
- A real, appropriately licensed image dataset if you want to run the training experiments.

## Run the application

### 1. Get the code

```powershell
git clone https://github.com/fadlyfebrosp/ChickenpoxAI.git
Set-Location ChickenpoxAI
```

### 2. Install and start Ollama

Install Ollama, then download the model used by the backend:

```powershell
ollama pull medgemma:4b
```

Keep the Ollama application/service running. Its local API is expected at `http://127.0.0.1:11434`.

### 3. Install and start the backend

Open a PowerShell terminal in the project root:

```powershell
Set-Location backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

If PowerShell blocks activation, either enable script activation according to your organization's policy or invoke the environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Check the service at `http://localhost:8000/health`. The `vision_model_available` value should be `true` when Ollama is running and the model is installed.

### 4. Install and start the frontend

Open a second PowerShell terminal at the project root:

```powershell
Set-Location frontend
npm install
npm run dev
```

Open the local URL printed by Vite, usually `http://localhost:5173`.

The frontend's API service currently targets `http://localhost:8000`. For a local setup, keep the backend on that address. Do not expose the development server or API to an untrusted network without first reviewing and changing the development CORS and host settings.

## Prepare a dataset

The dataset is not included in this repository. Use only images you have permission to use, and check the original dataset's license and terms before copying or distributing it.

### Supported binary folder layout

The EfficientNet experiment expects two class folders in each split:

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

Supported image extensions are `.jpg`, `.jpeg`, `.png`, and `.webp`. Keep the same two class folders in all splits. The intended label mapping is:

| Training folder | Source class |
| --- | --- |
| `healthy` | `Normal` |
| `chickenpox` | `Chickenpox` |

For a source directory containing `Normal`, `Chickenpox`, `Measles`, and `Monkeypox` subfolders, prepare the binary dataset with:

```powershell
Set-Location training
python prepare_dataset.py --source "D:\path\to\Monkeypox Skin Image Dataset" --target "D:\ChickenpoxAI\dataset"
```

The script uses `Normal` and `Chickenpox` by default and makes a stratified 70%/15%/15% train/validation/test split. **It clears the existing files inside `dataset\train`, `dataset\validation`, and `dataset\test` before copying the new split. Back up any data in those folders before running it.**

The optional `--use-all-classes` switch maps `Measles` and `Monkeypox` into the `chickenpox` folder as well. This does not create a multi-class model: it deliberately groups those images under one binary label and changes what the label means. Only use it if that is appropriate for your experiment.

Before training, inspect your data:

```powershell
python analyze_dataset.py
```

The analysis checks image counts, sizes, corrupt images, and duplicate files, and writes a class-distribution plot under `results/`. Review duplicates and possible overlap across splits yourself. The split helper keeps copied file paths in only one split, but it cannot ensure that near-duplicate images, images of the same person, or related captures are independent.

## Train and evaluate EfficientNet

Run the commands from the `training` directory after preparing the dataset.

### Train

```powershell
python train.py
```

The default configuration uses EfficientNet-B0 with ImageNet pretrained weights, 224-pixel inputs, batch size 32, learning rate `0.0001`, up to 20 epochs, and early stopping (patience 5). The first run may download pretrained weights. The best checkpoint is written to:

```text
backend/models/chickenpox_model_best.pth
```

Training history and plots are written to `results/`. Adjust the supported options if needed:

```powershell
python train.py --help
python train.py --epochs 30 --batch-size 16 --image-size 224 --seed 42
```

Use a batch size that fits your hardware. Training may run on CPU or CUDA, depending on the installed PyTorch build and available hardware.

### Evaluate

After training, evaluate the checkpoint against the held-out test split:

```powershell
python evaluate.py
```

The script reports accuracy, precision, recall, F1, sensitivity, specificity, balanced accuracy, ROC-AUC when calculable, and a classification report. It writes `results/confusion_matrix.png` and `results/evaluation_metrics.json`.

Do not train on the test split or use it repeatedly to tune the model. Report the dataset size, class balance, split method, and relevant per-class metrics alongside aggregate accuracy. A small or biased dataset can produce misleading results; no metric or UI change can guarantee 99% or 100% real-world accuracy.

### Optional Grad-CAM

Grad-CAM is an interpretability visualization for the trained EfficientNet checkpoint, not a disease confirmation:

```powershell
python grad_cam.py --image "D:\path\to\example.jpg"
```

The default image is saved to `results/grad_cam.png`. Use `python grad_cam.py --help` to choose another output path or class index.

`inference_test.py` only loads an image and reports its dimensions; it is a basic image-reading check, not a model prediction command.

## API reference

FastAPI's interactive documentation is available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### `GET /health`

Checks whether the backend can see the configured local Ollama model:

```json
{
  "status": "ok",
  "vision_model_available": true
}
```

### `POST /predict`

Send `multipart/form-data` with:

| Field | Required | Description |
| --- | --- | --- |
| `image` | Yes | `.jpg`, `.jpeg`, `.png`, or `.webp` image, up to 10 MB |
| `language` | No | `id` (default) or `en` for the visual observation language |

PowerShell example using `curl.exe`:

```powershell
curl.exe -X POST "http://localhost:8000/predict" `
  -F "image=@D:\path\to\skin-image.jpg" `
  -F "language=id"
```

Successful response:

```json
{
  "prediction": "Chickenpox",
  "visual_observation": "Deskripsi singkat mengenai ciri yang terlihat.",
  "model": "medgemma:4b",
  "status": "estimate"
}
```

`prediction` is limited to `Healthy Skin` or `Chickenpox`. The response does not contain a percentage or calibrated confidence value. Invalid input returns HTTP 400; an unavailable local model returns HTTP 503; an inference failure returns HTTP 502.

## Privacy and safe use

- The browser sends the selected image to the backend configured by the frontend. The backend sends image content to the Ollama API at the configured local address. In the default configuration these services run on the same computer; the image is not sent to a hosted ChickenpoxAI inference API.
- The application does not intentionally save uploaded images to a project folder. Avoid uploading identifiable or sensitive images, and review the behavior of your local operating system, Ollama installation, and any logging or monitoring tools you use.
- The backend accepts images up to 10 MB and validates their file extension and readability. This is not a complete production security review.
- The backend currently enables permissive CORS, and its built-in entry point defaults to binding all interfaces. The command in this README explicitly binds Uvicorn to loopback for local use; keep the service private unless you deliberately configure and secure it for another environment.
- Outputs can be incorrect or biased, especially for blurry, low-quality, atypical, or out-of-distribution images. Do not use the application to diagnose, rule out, or treat a condition.
- This project is intended for research and education, not clinical, emergency, or commercial decision-making.

## Troubleshooting

| Problem | Things to check |
| --- | --- |
| `ollama` is not recognized | Install Ollama, open a new terminal, and confirm `ollama --version`. |
| Model unavailable / `/health` says `false` | Start Ollama and run `ollama pull medgemma:4b`; check that Ollama's local API is responding. |
| Prediction reports Ollama unavailable | Confirm Ollama is running at `http://127.0.0.1:11434` and that the backend can reach it. |
| Upload returns HTTP 400 | Use a readable JPG, JPEG, PNG, or WEBP image smaller than 10 MB. |
| Training says a split is missing | Check the required `dataset\train`, `dataset\validation`, and `dataset\test` folders and their class subfolders. |
| Evaluation cannot find a checkpoint | Run `python train.py` first and check for `backend\models\chickenpox_model_best.pth`. |
| Training runs out of memory | Reduce the batch size, for example `python train.py --batch-size 8`. |
| Frontend cannot reach the backend | Start the backend on port 8000 and check that the browser can access `http://localhost:8000/health`. |

## License and third-party terms

The ChickenpoxAI source code in this repository is made available under the [MIT License](LICENSE). The MIT license applies to this project's code only, unless a file or separate notice says otherwise.

It does **not** grant rights to:

- image datasets or other assets; their owners' licenses, consent requirements, and terms must be checked separately;
- the MedGemma model or Ollama software; MedGemma is subject to the [Health AI Developer Foundations terms](https://developers.google.com/health-ai-developer-foundations/terms), and Ollama has its own license;
- Python, JavaScript, or other third-party dependencies, which remain subject to their respective licenses.

The MIT License disclaims warranties and liability for the software. It does not change the medical and research-use limitations described above.
