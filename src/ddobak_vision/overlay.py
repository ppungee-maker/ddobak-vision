"""3색 빨간펜 오버레이.

기획서: "찍은 사진 원본 위에 빨강=낼 돈, 파랑=기한, 초록=챙길 서류를 형광펜처럼 표시".
원본을 수정하지 않고 반투명 레이어를 합성해 따로 저장한다.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from .models import DocumentExtraction

_FILL_ALPHA = 90  # 형광펜 반투명도 (0=투명, 255=불투명)
_OUTLINE_WIDTH = 3


def render_overlay(extraction: DocumentExtraction, *, out_path: Path) -> Path:
    base = Image.open(extraction.source_image).convert("RGBA")
    highlight = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(highlight)

    for item in extraction.items:
        left, top, right, bottom = item.bbox.to_pixels(*base.size)
        r, g, b = item.color.rgb
        draw.rectangle(
            [left, top, right, bottom],
            fill=(r, g, b, _FILL_ALPHA),
            outline=(r, g, b, 255),
            width=_OUTLINE_WIDTH,
        )

    merged = Image.alpha_composite(base, highlight).convert("RGB")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    merged.save(out_path)
    return out_path
