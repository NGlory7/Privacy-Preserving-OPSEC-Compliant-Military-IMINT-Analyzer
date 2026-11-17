"""
One-time model download (the only step that needs the network).

    python tools/download_models.py

Downloads OWLv2, CLIP ViT-L/14 and the YuNet face detector into ./models.
Afterwards the analyzer runs fully offline.
"""

import os
import sys
import urllib.request
from pathlib import Path

os.environ["AEGIS_ALLOW_DOWNLOAD"] = "1"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from huggingface_hub import snapshot_download  # noqa: E402

from src.models import CLIP_ID, HF_CACHE, MODELS_DIR, OWL_ID, YUNET_PATH, YUNET_URL  # noqa: E402

MODELS_DIR.mkdir(exist_ok=True)

for repo in (OWL_ID, CLIP_ID):
    print(f"[*] {repo}")
    # Only the PyTorch safetensors + configs; skip TF/Flax duplicates
    snapshot_download(repo, cache_dir=HF_CACHE,
                      allow_patterns=["*.json", "*.txt", "*.safetensors", "*.model", "merges.txt", "vocab.json"])

if not YUNET_PATH.is_file():
    print("[*] YuNet face detector")
    urllib.request.urlretrieve(YUNET_URL, YUNET_PATH)

print(f"[+] Models ready in {MODELS_DIR}. The analyzer can now run offline.")
