"""Model factory — EfficientNet, Xception, ViT and dedicated HF detector."""

from __future__ import annotations

from pathlib import Path

import app.ml.compat  # noqa: F401 — lzma shim for pyenv Mac builds
import torch
import torch.nn as nn
from PIL import Image
from torchvision import models


class DeepfakeClassifier(nn.Module):
    """Binary real/fake classifier wrapping a backbone."""

    def __init__(self, backbone: nn.Module, feature_dim: int):
        super().__init__()
        self.backbone = backbone
        self.classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(feature_dim, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(256, 2),
        )
        self.feature_dim = feature_dim

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        features = self.extract_features(x)
        return self.classifier(features)

    def extract_features(self, x: torch.Tensor) -> torch.Tensor:
        return self.backbone(x)


class HuggingFaceDeepfakeDetector:
    """Dedicated real/fake image detector with its own trained classifier head.

    The model is downloaded and cached by Hugging Face Transformers on first use.
    It is intentionally separate from ImageNet-pretrained EfficientNet/ViT
    backbones so an untrained classification head can never be presented as a
    deepfake detector.
    """

    def __init__(self, model_id: str, device: torch.device):
        from transformers import AutoImageProcessor, AutoModelForImageClassification

        self.model_id = model_id
        self.device = device
        self.processor = AutoImageProcessor.from_pretrained(model_id)
        self.model = AutoModelForImageClassification.from_pretrained(model_id)
        self.model.to(device)
        self.model.eval()

        label_map = {int(k): str(v).lower() for k, v in self.model.config.id2label.items()}
        fake_ids = [idx for idx, label in label_map.items() if "fake" in label]
        real_ids = [idx for idx, label in label_map.items() if "real" in label]
        if not fake_ids or not real_ids:
            raise ValueError(f"Detector {model_id!r} does not expose Real/Fake labels")
        self.fake_index = fake_ids[0]
        self.real_index = real_ids[0]

    @torch.inference_mode()
    def predict(self, image_rgb) -> float:
        image = Image.fromarray(image_rgb).convert("RGB")
        inputs = self.processor(images=image, return_tensors="pt")
        inputs = {key: value.to(self.device) for key, value in inputs.items()}
        logits = self.model(**inputs).logits
        probs = torch.softmax(logits, dim=-1)[0]
        return float(probs[self.fake_index].item())


def _efficientnet(variant: str = "b0", pretrained: bool = True) -> DeepfakeClassifier:
    weights = "DEFAULT" if pretrained else None
    if variant == "b2":
        net = models.efficientnet_b2(weights=weights)
        feature_dim = net.classifier[1].in_features
    else:
        net = models.efficientnet_b0(weights=weights)
        feature_dim = net.classifier[1].in_features
    net.classifier = nn.Identity()
    return DeepfakeClassifier(net, feature_dim)


def _xception_like(pretrained: bool = True) -> DeepfakeClassifier:
    """Xception-style backbone via ResNeXt50 (torchvision-native stand-in)."""
    weights = "DEFAULT" if pretrained else None
    net = models.resnext50_32x4d(weights=weights)
    feature_dim = net.fc.in_features
    net.fc = nn.Identity()
    return DeepfakeClassifier(net, feature_dim)


def _vit(pretrained: bool = True) -> DeepfakeClassifier:
    weights = "DEFAULT" if pretrained else None
    net = models.vit_b_16(weights=weights)
    feature_dim = net.heads.head.in_features
    net.heads.head = nn.Identity()
    return DeepfakeClassifier(net, feature_dim)


def build_model(name: str = "efficientnet", pretrained: bool = True) -> DeepfakeClassifier:
    key = name.lower().strip()
    if key in {"efficientnet", "efficientnet-b0", "efficientnet_b0"}:
        return _efficientnet("b0", pretrained=pretrained)
    if key in {"efficientnet-b2", "efficientnet_b2"}:
        return _efficientnet("b2", pretrained=pretrained)
    if key in {"xception", "xceptionnet", "resnext"}:
        return _xception_like(pretrained=pretrained)
    if key in {"vit", "vision_transformer", "vit_b_16"}:
        return _vit(pretrained=pretrained)
    raise ValueError(f"Unknown model: {name}")


def load_checkpoint(
    model: nn.Module,
    weights_path: Path | None,
    device: torch.device,
) -> tuple[nn.Module, bool]:
    """Load a compatible fine-tuned checkpoint; reject partial/mismatched weights."""
    if weights_path and weights_path.exists():
        try:
            state = torch.load(weights_path, map_location=device, weights_only=True)
            if isinstance(state, dict) and "state_dict" in state:
                state = state["state_dict"]
            if not isinstance(state, dict):
                raise ValueError("Checkpoint does not contain a state dictionary")
            state = {str(k).removeprefix("module."): v for k, v in state.items()}
            incompatible = model.load_state_dict(state, strict=False)
            if incompatible.missing_keys or incompatible.unexpected_keys:
                raise ValueError(
                    "Checkpoint architecture mismatch: "
                    f"missing={len(incompatible.missing_keys)}, "
                    f"unexpected={len(incompatible.unexpected_keys)}"
                )
            model.to(device)
            model.eval()
            return model, True
        except Exception:
            # Never label a partially loaded/random classifier as fine-tuned.
            model.to(device)
            model.eval()
            return model, False
    model.to(device)
    model.eval()
    return model, False
