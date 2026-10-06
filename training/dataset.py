from __future__ import annotations

import hashlib
import shutil
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from PIL import Image
from sklearn.model_selection import train_test_split
from torchvision import transforms

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def ensure_dataset_directories(root: Path) -> None:
    root = root.resolve()
    for split in ("train", "validation", "test"):
        for cls in ("healthy", "chickenpox"):
            (root / split / cls).mkdir(parents=True, exist_ok=True)


def collect_image_files(directory: Path) -> List[Path]:
    if not directory.exists():
        return []
    return sorted(
        [
            path
            for path in directory.iterdir()
            if path.is_file() and path.suffix.lower() in VALID_EXTENSIONS
        ],
        key=lambda p: p.name.lower(),
    )


def image_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def find_class_directories(root: Path) -> Dict[str, Path]:
    class_dirs: Dict[str, Path] = {}
    for child in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        if child.is_dir() and not child.name.startswith("."):
            class_dirs[child.name] = child
    return class_dirs


def split_dataset(
    dataset_root: Path,
    train_ratio: float = 0.70,
    validation_ratio: float = 0.15,
    test_ratio: float = 0.15,
    random_state: int = 42,
) -> Dict[str, List[Path]]:
    dataset_root = dataset_root.resolve()
    if not dataset_root.exists():
        raise FileNotFoundError(f"Dataset folder not found: {dataset_root}")

    if not (dataset_root / "train").exists() and not (dataset_root / "validation").exists() and not (dataset_root / "test").exists():
        class_dirs = find_class_directories(dataset_root)
        if not class_dirs:
            raise ValueError(f"No class folders found in {dataset_root}.")

        class_names = sorted(class_dirs)
        dataset_items: List[Tuple[Path, str]] = []
        for class_name in class_names:
            files = collect_image_files(class_dirs[class_name])
            if not files:
                continue
            dataset_items.extend((file_path, class_name) for file_path in files)

        if len(dataset_items) < 2:
            raise ValueError("Dataset is too small for train/validation/test splitting.")

        train_data, temp_data = train_test_split(
            dataset_items,
            train_size=train_ratio,
            random_state=random_state,
            stratify=[label for _, label in dataset_items],
        )
        validation_data, test_data = train_test_split(
            temp_data,
            test_size=test_ratio / (validation_ratio + test_ratio),
            random_state=random_state,
            stratify=[label for _, label in temp_data],
        )

        destination_root = dataset_root
        ensure_dataset_directories(destination_root)

        for split_name, split_items in {
            "train": train_data,
            "validation": validation_data,
            "test": test_data,
        }.items():
            for source_file, class_name in split_items:
                destination = destination_root / split_name / class_name / source_file.name
                destination.parent.mkdir(parents=True, exist_ok=True)
                if not destination.exists():
                    shutil.copy2(source_file, destination)

        return {
            "train": collect_image_files(destination_root / "train" / "healthy") + collect_image_files(destination_root / "train" / "chickenpox"),
            "validation": collect_image_files(destination_root / "validation" / "healthy") + collect_image_files(destination_root / "validation" / "chickenpox"),
            "test": collect_image_files(destination_root / "test" / "healthy") + collect_image_files(destination_root / "test" / "chickenpox"),
        }

    return {
        "train": collect_image_files(dataset_root / "train" / "healthy") + collect_image_files(dataset_root / "train" / "chickenpox"),
        "validation": collect_image_files(dataset_root / "validation" / "healthy") + collect_image_files(dataset_root / "validation" / "chickenpox"),
        "test": collect_image_files(dataset_root / "test" / "healthy") + collect_image_files(dataset_root / "test" / "chickenpox"),
    }


def build_transforms(image_size: int = 224, is_train: bool = False):
    if is_train:
        return transforms.Compose(
            [
                transforms.Resize((image_size + 32, image_size + 32)),
                transforms.RandomResizedCrop(image_size, scale=(0.85, 1.0)),
                transforms.RandomHorizontalFlip(p=0.5),
                transforms.RandomRotation(degrees=10, fill=0),
                transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1, hue=0.05),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ]
        )
    return transforms.Compose(
        [
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )


def open_image(path: Path) -> Image.Image:
    with Image.open(path) as image:
        rgb = image.convert("RGB")
        return rgb
