from __future__ import annotations

import argparse
import shutil
from pathlib import Path


DEFAULT_SOURCE_DIR = Path(r"D:\ChickenpoxAI\dataset\Monkeypox Skin Image Dataset")
TARGET_ROOT = Path(r"D:\ChickenpoxAI\dataset")


def build_required_structure(root: Path) -> None:
    for split in ("train", "validation", "test"):
        for cls in ("healthy", "chickenpox"):
            (root / split / cls).mkdir(parents=True, exist_ok=True)


def clear_split_dirs(root: Path) -> None:
    for split in ("train", "validation", "test"):
        split_dir = root / split
        if split_dir.exists():
            for child in split_dir.iterdir():
                if child.is_dir():
                    for file in child.iterdir():
                        if file.is_file():
                            file.unlink()
                    for inner in list(child.iterdir()):
                        if inner.is_dir():
                            shutil.rmtree(inner)
                elif child.is_file():
                    child.unlink()


def build_source_mapping(use_all_classes: bool = False):
    if use_all_classes:
        return {
            "healthy": ["Normal"],
            "chickenpox": ["Chickenpox", "Measles", "Monkeypox"],
        }
    return {
        "healthy": ["Normal"],
        "chickenpox": ["Chickenpox"],
    }


def prepare_dataset(source_dir: Path, target_root: Path, use_all_classes: bool = False, random_seed: int = 42) -> dict:
    from sklearn.model_selection import train_test_split

    build_required_structure(target_root)
    clear_split_dirs(target_root)

    source_map = build_source_mapping(use_all_classes)
    dataset_items = []
    for class_name, source_names in source_map.items():
        for source_name in source_names:
            class_dir = source_dir / source_name
            if not class_dir.exists():
                continue
            for item in sorted(class_dir.iterdir(), key=lambda p: p.name.lower()):
                if item.is_file():
                    dataset_items.append((item, class_name))

    if len(dataset_items) < 2:
        raise ValueError("Not enough valid images found in the source dataset.")

    train_items, temp_items = train_test_split(
        dataset_items,
        train_size=0.70,
        random_state=random_seed,
        stratify=[label for _, label in dataset_items],
    )
    validation_items, test_items = train_test_split(
        temp_items,
        test_size=0.5,
        random_state=random_seed,
        stratify=[label for _, label in temp_items],
    )

    split_map = {
        "train": train_items,
        "validation": validation_items,
        "test": test_items,
    }

    counts = {"healthy": 0, "chickenpox": 0}
    for split_name, items in split_map.items():
        for source_file, class_name in items:
            destination = target_root / split_name / class_name / source_file.name
            destination.parent.mkdir(parents=True, exist_ok=True)
            if not destination.exists():
                shutil.copy2(source_file, destination)
            counts[class_name] += 1

    return counts


def main():
    parser = argparse.ArgumentParser(description="Prepare the available dataset for the two-class ChickenpoxAI binary task.")
    parser.add_argument("--source", type=str, default=str(DEFAULT_SOURCE_DIR), help="Source folder containing class folders like Normal/Chickenpox/Monkeypox/Measles.")
    parser.add_argument("--target", type=str, default=str(TARGET_ROOT), help="Target dataset root for the project.")
    parser.add_argument("--use-all-classes", action="store_true", help="Include Measles and Monkeypox as non-healthy negative classes when creating the two-class dataset.")
    args = parser.parse_args()

    source_dir = Path(args.source).expanduser().resolve()
    target_root = Path(args.target).expanduser().resolve()

    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    print(f"Reading dataset from: {source_dir}")
    counts = prepare_dataset(source_dir, target_root, use_all_classes=args.use_all_classes)

    print("Prepared dataset summary:")
    print(f"  healthy: {counts['healthy']}")
    print(f"  chickenpox: {counts['chickenpox']}")
    print(f"Target dataset root: {target_root}")
    print("Note: For a strict Chickenpox-vs-Healthy task, use only Normal and Chickenpox classes.")


if __name__ == "__main__":
    main()
