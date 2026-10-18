from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image


@pytest.fixture
def blank_image(tmp_path: Path) -> Path:
    """overlay 렌더링용 최소 이미지 — 내용은 중요하지 않고 크기만 있으면 됨."""
    path = tmp_path / "blank.jpg"
    Image.new("RGB", (800, 1200), "white").save(path)
    return path
