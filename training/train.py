from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from torch import nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.models import EfficientNet_B0_Weights, efficientnet_b0

from dataset import build_transforms, split_dataset


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_ROOT = PROJECT_ROOT / "dataset"
RESULTS_DIR = PROJECT_ROOT / "results"
MODEL_DIR = PROJECT_ROOT / "backend" / "models"
MODEL_PATH = MODEL_DIR / "chickenpox_model_best.pth"


def set_seed(seed: int = 42) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def build_model(num_classes: int = 2) -> nn.Module:
    weights = EfficientNet_B0_Weights.DEFAULT
    model = efficientnet_b0(weights=weights)
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    return model


def ensure_dataset_ready(dataset_root: Path) -> Tuple[Path, Path, Path]:
    if not (dataset_root / "train").exists() and not (dataset_root / "validation").exists() and not (dataset_root / "test").exists():
        if any(child.is_dir() for child in dataset_root.iterdir() if child.name not in {"train", "validation", "test"}):
            split_dataset(dataset_root)

    train_dir = dataset_root / "train"
    validation_dir = dataset_root / "validation"
    test_dir = dataset_root / "test"

    for split_dir in (train_dir, validation_dir, test_dir):
        if not split_dir.exists():
            raise FileNotFoundError(
                f"Expected dataset split '{split_dir.name}' is missing. Please place real image data into {dataset_root}."
            )

    return train_dir, validation_dir, test_dir


def get_class_names(train_dir: Path) -> List[str]:
    class_dirs = sorted([p.name for p in train_dir.iterdir() if p.is_dir()])
    if not class_dirs:
        raise ValueError(f"No class directories found in {train_dir}.")
    return class_dirs


def create_dataloaders(
    train_dir: Path,
    validation_dir: Path,
    image_size: int,
    batch_size: int,
) -> Tuple[DataLoader, DataLoader, List[str]]:
    class_names = get_class_names(train_dir)
    train_dataset = datasets.ImageFolder(str(train_dir), transform=build_transforms(image_size, is_train=True))
    validation_dataset = datasets.ImageFolder(str(validation_dir), transform=build_transforms(image_size, is_train=False))

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=2, pin_memory=torch.cuda.is_available())
    validation_loader = DataLoader(validation_dataset, batch_size=batch_size, shuffle=False, num_workers=2, pin_memory=torch.cuda.is_available())
    return train_loader, validation_loader, class_names


def evaluate_model(model: nn.Module, loader: DataLoader, device: torch.device) -> Dict[str, float]:
    model.eval()
    total_loss = 0.0
    predictions = []
    targets = []
    criterion = nn.CrossEntropyLoss()

    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device)
            labels = labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            total_loss += loss.item() * images.size(0)
            predictions.extend(outputs.argmax(dim=1).cpu().tolist())
            targets.extend(labels.cpu().tolist())

    avg_loss = total_loss / max(len(loader.dataset), 1)
    metrics = {
        "loss": avg_loss,
        "accuracy": accuracy_score(targets, predictions),
        "precision": precision_score(targets, predictions, average="binary", zero_division=0),
        "recall": recall_score(targets, predictions, average="binary", zero_division=0),
        "f1": f1_score(targets, predictions, average="binary", zero_division=0),
    }
    return metrics


def plot_history(history: Dict[str, List[float]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for metric_name, values in history.items():
        if not values:
            continue
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(range(1, len(values) + 1), values, marker="o", linewidth=2)
        ax.set_title(metric_name.replace("_", " ").title())
        ax.set_xlabel("Epoch")
        ax.set_ylabel(metric_name)
        fig.tight_layout()
        fig.savefig(output_dir / f"{metric_name}.png", dpi=150)
        plt.close(fig)


def save_checkpoint(model: nn.Module, class_names: List[str], image_size: int, metrics: Dict[str, float], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = {
        "model_state_dict": model.state_dict(),
        "class_names": class_names,
        "image_size": image_size,
        "training_metrics": metrics,
        "model_architecture": "efficientnet_b0",
    }
    torch.save(checkpoint, path)


def train_model(args: argparse.Namespace) -> None:
    set_seed(args.seed)
    DATASET_ROOT.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    train_dir, validation_dir, _ = ensure_dataset_ready(DATASET_ROOT)
    train_loader, validation_loader, class_names = create_dataloaders(
        train_dir=train_dir,
        validation_dir=validation_dir,
        image_size=args.image_size,
        batch_size=args.batch_size,
    )

    if len(class_names) != 2:
        raise ValueError(f"This project expects exactly 2 classes. Found {class_names}.")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_model(num_classes=2).to(device)

    for param in model.parameters():
        param.requires_grad = False
    for param in model.classifier.parameters():
        param.requires_grad = True

    criterion = nn.CrossEntropyLoss()
    optimizer = AdamW(model.classifier.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay)
    scheduler = ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=2, threshold=1e-4)

    history = {"training_loss": [], "validation_loss": [], "training_accuracy": [], "validation_accuracy": []}
    best_val_loss = float("inf")
    patience_counter = 0

    for epoch in range(1, args.epochs + 1):
        model.train()
        running_loss = 0.0
        running_correct = 0
        total_samples = 0

        for images, labels in train_loader:
            images = images.to(device)
            labels = labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            running_correct += (outputs.argmax(dim=1) == labels).sum().item()
            total_samples += labels.size(0)

        train_loss = running_loss / total_samples
        train_accuracy = running_correct / total_samples
        history["training_loss"].append(train_loss)
        history["training_accuracy"].append(train_accuracy)

        val_metrics = evaluate_model(model, validation_loader, device)
        history["validation_loss"].append(val_metrics["loss"])
        history["validation_accuracy"].append(val_metrics["accuracy"])

        scheduler.step(val_metrics["loss"])

        print(
            f"Epoch {epoch}/{args.epochs} | train_loss={train_loss:.4f} | train_acc={train_accuracy:.4f} | "
            f"val_loss={val_metrics['loss']:.4f} | val_acc={val_metrics['accuracy']:.4f}"
        )

        if val_metrics["loss"] < best_val_loss - 1e-5:
            best_val_loss = val_metrics["loss"]
            patience_counter = 0
            save_checkpoint(model, class_names, args.image_size, val_metrics, MODEL_PATH)
        else:
            patience_counter += 1
            if patience_counter >= args.patience:
                print(f"Early stopping triggered at epoch {epoch}.")
                break

    plot_history(history, RESULTS_DIR)

    with open(PROJECT_ROOT / "results" / "training_history.json", "w", encoding="utf-8") as file:
        json.dump(history, file, indent=2)

    print(f"Best model checkpoint saved to: {MODEL_PATH}")
    print(f"Training plots saved to: {RESULTS_DIR}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train ChickenpoxAI with EfficientNet-B0 transfer learning.")
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--learning-rate", type=float, default=1e-4)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--patience", type=int, default=5)
    parser.add_argument("--weight-decay", type=float, default=1e-2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--prepare-only", action="store_true", help="Only prepare the dataset structure and exit.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.prepare_only:
        if not DATASET_ROOT.exists():
            DATASET_ROOT.mkdir(parents=True, exist_ok=True)
        if any(child.is_dir() for child in DATASET_ROOT.iterdir() if child.name not in {"train", "validation", "test"}):
            split_dataset(DATASET_ROOT)
        print(f"Dataset is ready at: {DATASET_ROOT}")
    else:
        train_model(args)
