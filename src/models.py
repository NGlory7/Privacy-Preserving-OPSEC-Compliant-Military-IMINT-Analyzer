"""
Local model registry.

All model weights live under ``models/`` inside the repository and are loaded with
``local_files_only=True``. Downloading happens exactly once, explicitly, through
``python tools/download_models.py``. After that the analyzer never needs the network,
and ``src.opsec.network_guard`` enforces it at runtime.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = ROOT / "models"
HF_CACHE = MODELS_DIR / "hf"

# Open-vocabulary object detector (Apache-2.0)
OWL_ID = "google/owlv2-base-patch16-ensemble"
# Image-text embedding model for fine-grained identification (MIT)
CLIP_ID = "openai/clip-vit-large-patch14"
# Face detector from the OpenCV model zoo (MIT)
YUNET_URL = (
    "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/"
    "face_detection_yunet_2023mar.onnx"
)
YUNET_PATH = MODELS_DIR / "face_detection_yunet_2023mar.onnx"

# Never let transformers / huggingface_hub reach out on their own.
if not os.environ.get("AEGIS_ALLOW_DOWNLOAD"):
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")


class ModelsMissingError(RuntimeError):
    """Raised when weights have not been downloaded yet."""

    def __init__(self, what: str):
        super().__init__(
            f"{what} weights not found under {MODELS_DIR}. "
            "Run `python tools/download_models.py` once (requires network), then the analyzer runs offline."
        )


def device() -> str:
    import torch

    return "cuda" if torch.cuda.is_available() else "cpu"


@lru_cache(maxsize=1)
def load_owl():
    """Returns (processor, model) for OWLv2."""
    import torch
    from transformers import Owlv2ForObjectDetection, Owlv2Processor

    try:
        processor = Owlv2Processor.from_pretrained(OWL_ID, cache_dir=HF_CACHE, local_files_only=True)
        model = Owlv2ForObjectDetection.from_pretrained(OWL_ID, cache_dir=HF_CACHE, local_files_only=True)
    except OSError as exc:
        raise ModelsMissingError("OWLv2") from exc
    dtype = torch.float16 if device() == "cuda" else torch.float32
    return processor, model.to(device(), dtype=dtype).eval()


@lru_cache(maxsize=1)
def load_clip():
    """Returns (processor, model) for CLIP."""
    import torch
    from transformers import CLIPModel, CLIPProcessor

    try:
        processor = CLIPProcessor.from_pretrained(CLIP_ID, cache_dir=HF_CACHE, local_files_only=True)
        model = CLIPModel.from_pretrained(CLIP_ID, cache_dir=HF_CACHE, local_files_only=True)
    except OSError as exc:
        raise ModelsMissingError("CLIP") from exc
    dtype = torch.float16 if device() == "cuda" else torch.float32
    return processor, model.to(device(), dtype=dtype).eval()


def models_available() -> dict:
    """Cheap check (no loading) used by the UI and tests."""
    def has(repo_id: str) -> bool:
        folder = HF_CACHE / ("models--" + repo_id.replace("/", "--")) / "snapshots"
        return folder.is_dir() and any(folder.iterdir())

    return {"owlv2": has(OWL_ID), "clip": has(CLIP_ID), "yunet": YUNET_PATH.is_file()}
