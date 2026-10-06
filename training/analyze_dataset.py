from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

from dataset import VALID_EXTENSIONS, collect_image_files, image_hash


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_ROOT = PROJECT_ROOT / "dataset"
RESULTS_DIR = PROJECT_ROOT / "results"


def list_dataset_folders(root: Path):
    splits = ["train", "validation", "test"]
    found = {split: root / split for split in splits if (root / split).exists()}
    if not found:
        return []
    return found


def collect_split_counts(dataset_root: Path):
    results = {"total": 0, "healthy": 0, "chickenpox": 0, "train": 0, "validation": 0, "test": 0}
    for split in ("train", "validation", "test"):
        split_dir = dataset_root / split
        if not split_dir.exists():
            continue
        for class_name in ("healthy", "chickenpox"):
            class_dir = split_dir / class_name
            if not class_dir.exists():
                continue
            count = len(collect_image_files(class_dir))
            results[class_name] += count
            results[split] += count
            results["total"] += count
    return results


def iter_split_files(root: Path):
    for split in ("train", "validation", "test"):
        split_dir = root / split
        if not split_dir.exists():
            continue
        for path in split_dir.rglob("*"):
            if path.is_file() and path.suffix.lower() in VALID_EXTENSIONS:
                yield path


def detect_corrupt_images(root: Path):
    corrupt = []
    for path in iter_split_files(root):
        try:
            with Image.open(path) as img:
                img.verify()
        except Exception:
            corrupt.append(path)
    return corrupt


def find_duplicates(root: Path):
    hashes = {}
    duplicates = []
    for path in iter_split_files(root):
        digest = image_hash(path)
        if digest in hashes:
            duplicates.append({"hash": digest, "paths": [hashes[digest], str(path)]})
        else:
            hashes[digest] = str(path)
    return duplicates


def summarize_image_sizes(root: Path):
    sizes = []
    for path in iter_split_files(root):
        try:
            with Image.open(path) as image:
                sizes.append(image.size)
        except Exception:
            continue
    return sizes


def save_distribution_plot(class_counts: Counter, output_path: Path):
    labels = list(class_counts.keys())
    values = [class_counts[key] for key in labels]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(labels, values, color=["#4caf50", "#f44336"])
    ax.set_title("Class Distribution")
    ax.set_xlabel("Class")
    ax.set_ylabel("Number of images")
    for container in ax.containers:
        ax.bar_label(container, label_type="edge")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def main():
    if not DATASET_ROOT.exists():
        raise FileNotFoundError(f"Dataset folder not found: {DATASET_ROOT}")

    split_counts = collect_split_counts(DATASET_ROOT)
    class_counts = Counter()
    for split in ("train", "validation", "test"):
        split_dir = DATASET_ROOT / split
        if not split_dir.exists():
            continue
        for class_name in ("healthy", "chickenpox"):
            class_path = split_dir / class_name
            if class_path.exists():
                class_counts[class_name] += len(collect_image_files(class_path))

    corrupt = detect_corrupt_images(DATASET_ROOT)
    duplicates = find_duplicates(DATASET_ROOT)
    image_sizes = summarize_image_sizes(DATASET_ROOT)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    save_distribution_plot(class_counts, RESULTS_DIR / "dataset_distribution.png")

    print("=== ChickenpoxAI Dataset Analysis ===")
    print(f"Total images: {split_counts['total']}")
    print(f"Healthy Skin: {class_counts.get('healthy', 0)}")
    print(f"Chickenpox: {class_counts.get('chickenpox', 0)}")
    print(f"Training images: {split_counts.get('train', 0)}")
    print(f"Validation images: {split_counts.get('validation', 0)}")
    print(f"Testing images: {split_counts.get('test', 0)}")
    print("Class distribution:")
    for key in ("healthy", "chickenpox"):
        print(f"  - {key}: {class_counts.get(key, 0)}")

    if image_sizes:
        widths = [size[0] for size in image_sizes]
        heights = [size[1] for size in image_sizes]
        print(f"Image width range: {min(widths)} - {max(widths)}")
        print(f"Image height range: {min(heights)} - {max(heights)}")
        print(f"Unique image sizes: {sorted(set(image_sizes))[:10]}")
    else:
        print("Image size: no valid images found.")

    print(f"Corrupt or unreadable images: {len(corrupt)}")
    if corrupt:
        for item in corrupt[:10]:
            print(f"  - {item}")

    print(f"Possible duplicate groups: {len(duplicates)}")
    if duplicates:
        for entry in duplicates[:5]:
            print(f"  - hash={entry['hash']}, files={entry['paths']}")

    total = max(sum(class_counts.values()), 1)
    proportions = {label: count / total for label, count in class_counts.items()}
    if max(proportions.values()) > 0.75:
        print("Warning: class imbalance detected. Consider class weighting, weighted sampling, or augmentation strategies.")
    else:
        print("Class balance looks acceptable for a binary classification task.")

    print(f"Dataset report saved to: {RESULTS_DIR / 'dataset_distribution.png'}")


if __name__ == "__main__":
    main()
