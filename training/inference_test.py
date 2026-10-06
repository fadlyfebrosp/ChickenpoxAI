from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from dataset import open_image


def main():
    parser = argparse.ArgumentParser(description="Quickly test model inference on a single image.")
    parser.add_argument("--image", required=True, help="Path to an input image.")
    args = parser.parse_args()

    image_path = Path(args.image).expanduser().resolve()
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    print(f"Reading image: {image_path}")
    image = open_image(image_path)
    print(f"Image size: {image.size}")
    print("Inference test is ready. Use the backend model path or training checkpoint for actual prediction.")


if __name__ == "__main__":
    main()
