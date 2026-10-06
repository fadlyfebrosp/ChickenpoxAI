from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from sklearn.metrics import accuracy_score, balanced_accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from torchvision import datasets
from torchvision.models import efficientnet_b0

from dataset import build_transforms


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_ROOT = PROJECT_ROOT / "dataset"
MODEL_PATH = PROJECT_ROOT / "backend" / "models" / "chickenpox_model_best.pth"
RESULTS_DIR = PROJECT_ROOT / "results"


def build_model(num_classes: int = 2) -> torch.nn.Module:
    model = efficientnet_b0(weights=None)
    model.classifier[1] = torch.nn.Linear(model.classifier[1].in_features, num_classes)
    return model


def load_model(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Model checkpoint not found: {path}")

    checkpoint = torch.load(path, map_location=torch.device("cpu"))
    class_names = checkpoint.get("class_names", ["Healthy Skin", "Chickenpox"])
    model = build_model(num_classes=len(class_names))
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    return model, class_names


def evaluate_model(model, test_loader, class_names):
    all_probs = []
    true_labels = []
    predicted_labels = []

    with torch.no_grad():
        for images, labels in test_loader:
            outputs = model(images)
            probs = torch.softmax(outputs, dim=1)
            all_probs.append(probs.cpu().numpy())
            true_labels.extend(labels.cpu().numpy())
            predicted_labels.extend(outputs.argmax(dim=1).cpu().numpy())

    y_true = np.array(true_labels)
    y_pred = np.array(predicted_labels)
    probs = np.concatenate(all_probs, axis=0)

    positive_index = next(
        (
            index
            for index, name in enumerate(class_names)
            if "chickenpox" in str(name).replace(" ", "").lower()
        ),
        1,
    )
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average="binary", pos_label=positive_index, zero_division=0)
    recall = recall_score(y_true, y_pred, average="binary", pos_label=positive_index, zero_division=0)
    f1 = f1_score(y_true, y_pred, average="binary", pos_label=positive_index, zero_division=0)
    balanced_accuracy = balanced_accuracy_score(y_true, y_pred)
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tp = cm[positive_index, positive_index]
    fn = cm[positive_index, :].sum() - tp
    fp = cm[:, positive_index].sum() - tp
    tn = cm.sum() - tp - fn - fp
    specificity = tn / (tn + fp) if (tn + fp) else 0.0
    sensitivity = tp / (tp + fn) if (tp + fn) else 0.0

    report = {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "specificity": float(specificity),
        "sensitivity": float(sensitivity),
        "balanced_accuracy": float(balanced_accuracy),
    }

    try:
        roc_auc = roc_auc_score(y_true == positive_index, probs[:, positive_index])
        report["roc_auc"] = float(roc_auc)
    except ValueError:
        report["roc_auc"] = None

    return report, y_true, y_pred, probs


def save_confusion_matrix(y_true, y_pred, class_names, output_path: Path):
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(class_names)
    ax.set_yticklabels(class_names)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title("Confusion Matrix")
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, cm[i, j], ha="center", va="center", color="white" if cm[i, j] > cm.max() / 2 else "black")
    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def main():
    if not (DATASET_ROOT / "test").exists():
        raise FileNotFoundError(f"No test split found at {DATASET_ROOT / 'test'}. Place your data there before evaluation.")

    test_dataset = datasets.ImageFolder(str(DATASET_ROOT / "test"), transform=build_transforms(image_size=224, is_train=False))
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=32, shuffle=False, num_workers=2)

    model, class_names = load_model(MODEL_PATH)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    report, y_true, y_pred, probs = evaluate_model(model, test_loader, class_names)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    save_confusion_matrix(y_true, y_pred, class_names, RESULTS_DIR / "confusion_matrix.png")

    print("=== ChickenpoxAI Evaluation ===")
    print(f"Accuracy: {report['accuracy']:.4f}")
    print(f"Precision: {report['precision']:.4f}")
    print(f"Recall: {report['recall']:.4f}")
    print(f"F1 Score: {report['f1_score']:.4f}")
    print(f"Sensitivity: {report['sensitivity']:.4f}")
    print(f"Specificity: {report['specificity']:.4f}")
    print(f"Balanced Accuracy: {report['balanced_accuracy']:.4f}")
    if report["roc_auc"] is not None:
        print(f"ROC-AUC: {report['roc_auc']:.4f}")

    print("\nClassification Report:\n")
    display_names = [
        "Chickenpox" if "chickenpox" in str(name).replace(" ", "").lower() else "Healthy Skin"
        for name in class_names
    ]
    print(classification_report(y_true, y_pred, target_names=display_names, digits=4))

    with open(RESULTS_DIR / "evaluation_metrics.json", "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print(f"Confusion matrix saved to: {RESULTS_DIR / 'confusion_matrix.png'}")


if __name__ == "__main__":
    main()
