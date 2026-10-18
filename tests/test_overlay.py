from __future__ import annotations

from pathlib import Path

from PIL import Image

from ddobak_vision.extract import extract_document
from ddobak_vision.overlay import render_overlay
from ddobak_vision.providers.mock_provider import MockProvider


def test_render_overlay_writes_image_matching_source_size(blank_image: Path, tmp_path: Path):
    extraction = extract_document(blank_image, provider=MockProvider())
    out_path = tmp_path / "overlay.png"

    result_path = render_overlay(extraction, out_path=out_path)

    assert result_path == out_path
    assert out_path.exists()
    with Image.open(blank_image) as src, Image.open(out_path) as out:
        assert src.size == out.size
