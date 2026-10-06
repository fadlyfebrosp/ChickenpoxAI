from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from torchvision.models import efficientnet_b0

from dataset import open_image


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "backend" / "models" / "chickenpox_model_best.pth"


def build_model(num_classes: int = 2) -> torch.nn.Module:
    model = efficientnet_b0(weights=None)
    model.classifier[1] = torch.nn.Linear(model.classifier[1].in_features, num_classes)
    return model


def grad_cam(model: torch.nn.Module, image_tensor: torch.Tensor, class_index: int = 1, target_layer_name: str = "features"):
    feature_maps = {}

    def feature_hook(module, inputs, outputs):
        feature_maps["maps"] = outputs

    target_layer = model
    for part in target_layer_name.split("."):
        target_layer = getattr(target_layer, part)
    handle = target_layer.register_forward_hook(feature_hook)
    model.zero_grad()
    outputs = model(image_tensor)
    score = outputs[:, class_index].sum()
    gradients = torch.autograd.grad(score, feature_maps["maps"], retain_graph=True)[0]
    handle.remove()

    weights = gradients.mean(dim=(2, 3), keepdim=True)
    cam = (weights * feature_maps["maps"]).sum(dim=1, keepdim=True)
    cam = torch.relu(cam)
    cam = cam / (cam.max() + 1e-8)
    cam = cam.squeeze(0).squeeze(0).cpu().numpy()
    return cam


def preprocess_for_model(image, image_size: int = 224):
    image = image.convert("RGB").resize((image_size, image_size))
    pixel = np.asarray(image, dtype=np.float32) / 255.0
    pixel = pixel.transpose(2, 0, 1)
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)[:, None, None]
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)[:, None, None]
    tensor = (torch.tensor(pixel) - torch.tensor(mean)) / torch.tensor(std)
    return tensor.unsqueeze(0)


def save_grad_cam(image_path: Path, output_path: Path, class_index: int = 1):
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model checkpoint not found: {MODEL_PATH}")

    checkpoint = torch.load(MODEL_PATH, map_location="cpu")
    model = build_model(num_classes=len(checkpoint.get("class_names", ["Healthy Skin", "Chickenpox"])))
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    image = open_image(image_path)
    tensor = preprocess_for_model(image)
    cam = grad_cam(model, tensor, class_index=class_index)

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    axes[0].imshow(np.asarray(image))
    axes[0].set_title("Original Image")
    axes[0].axis("off")

    heatmap = axes[1].imshow(cam, cmap="jet", alpha=0.7)
    axes[1].set_title("Grad-CAM")
    axes[1].axis("off")
    fig.colorbar(heatmap, ax=axes[1], fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    print(f"Grad-CAM saved to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a Grad-CAM heatmap for a single image.")
    parser.add_argument("--image", required=True, help="Path to the image for Grad-CAM visualization.")
    parser.add_argument("--output", default=str(PROJECT_ROOT / "results" / "grad_cam.png"), help="Path to save the Grad-CAM image.")
    parser.add_argument("--class-index", type=int, default=1, help="Class index to visualize.")
    args = parser.parse_args()

    save_grad_cam(Path(args.image).expanduser().resolve(), Path(args.output), class_index=args.class_index)
