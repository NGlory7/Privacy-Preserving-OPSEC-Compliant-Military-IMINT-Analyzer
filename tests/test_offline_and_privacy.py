"""Fast tests: no model weights needed."""

import io
import socket
import urllib.request

import pytest
from PIL import Image

from src.opsec import network_guard
from src.opsec.metadata_sanitizer import MetadataSanitizer
from src.reasoning.correlation_engine import CorrelationEngine


def _image_with_gps() -> Image.Image:
    img = Image.new("RGB", (64, 48), (90, 110, 70))
    exif = img.getexif()
    exif[0x010F] = "TestCam"          # Make
    exif[0x0110] = "Model X"          # Model
    gps = exif.get_ifd(0x8825)
    gps[1], gps[2] = "N", (41.0, 0.0, 0.0)
    gps[3], gps[4] = "E", (29.0, 0.0, 0.0)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", exif=exif)
    buf.seek(0)
    return Image.open(buf)


def test_metadata_and_gps_are_removed():
    src = _image_with_gps()
    leaks = MetadataSanitizer.extract_metadata(src)
    assert leaks["has_gps"] and leaks["device_info"]["Make"] == "TestCam"

    clean, audit = MetadataSanitizer.sanitize(src)
    assert audit["gps_eliminated"] is True
    assert audit["remaining_exif_tags"] == 0
    buf = io.BytesIO()
    clean.save(buf, format="JPEG")
    assert not Image.open(io.BytesIO(buf.getvalue())).getexif()


def test_network_guard_blocks_outbound_and_counts():
    with network_guard.offline() as report:
        # urllib wraps the error in URLError (an OSError); the attempt is still counted
        with pytest.raises(OSError, match="blocked by AegisIMINT network guard"):
            urllib.request.urlopen("http://example.com", timeout=2)
        with pytest.raises(network_guard.OutboundNetworkBlocked):
            socket.create_connection(("1.1.1.1", 443), timeout=2)
    assert report["blocked_attempts"] == 2


def test_network_guard_allows_loopback_and_restores():
    srv = socket.socket()
    srv.bind(("127.0.0.1", 0))
    srv.listen(1)
    port = srv.getsockname()[1]
    with network_guard.offline():
        c = socket.create_connection(("127.0.0.1", port), timeout=2)
        c.close()
    srv.close()
    assert socket.create_connection is network_guard._original_create_connection


def test_attribution_is_inconclusive_without_evidence():
    out = CorrelationEngine.correlate([])
    assert out["inconclusive"] and out["top_candidate_nation"] == "Inconclusive"


def test_attribution_ignores_low_confidence_evidence():
    out = CorrelationEngine.correlate([{"kind": "weapon", "id": "wpn_ak74m", "probability": 0.1}])
    assert out["inconclusive"] and len(out["evidence_ignored"]) == 1


def test_single_widely_exported_item_stays_inconclusive():
    # Kirpi is used by Turkey and Ukraine with similar catalog weights: one sighting can't separate them
    out = CorrelationEngine.correlate([{"kind": "vehicle", "id": "veh_kirpi", "probability": 0.9}])
    assert out["inconclusive"]
    assert out["all_ranked_nations"][0]["country"] == "Turkey"
    assert all(e["kind"] == "vehicle" for e in out["evidence_used"])


def test_independent_evidence_makes_attribution_conclusive():
    out = CorrelationEngine.correlate([
        {"kind": "vehicle", "id": "veh_kirpi", "probability": 0.9},
        {"kind": "camouflage", "id": "camo_turkish_digital", "probability": 0.8},
        {"kind": "weapon", "id": "wpn_mpt76", "probability": 0.7},
    ])
    assert not out["inconclusive"]
    assert out["top_candidate_nation"] == "Turkey"
