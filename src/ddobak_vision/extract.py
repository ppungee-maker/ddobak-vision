"""전체 파이프라인 진입점: 제공자 호출 → 스키마 검증 → 이중 확인."""

from __future__ import annotations

from pathlib import Path

from .double_check import double_check
from .models import BBox, ColorTag, DocumentExtraction, ExtractedItem
from .providers.base import VisionProvider
from .providers.mock_provider import MockProvider


def extract_document(
    image_path: Path,
    *,
    provider: VisionProvider | None = None,
) -> DocumentExtraction:
    provider = provider or MockProvider()
    raw = provider.extract(image_path)

    items: list[ExtractedItem] = []
    warnings: list[str] = []
    for i, raw_item in enumerate(raw["items"], start=1):
        try:
            x, y, w, h = raw_item["bbox"]
            item = ExtractedItem(
                id=f"item-{i}",
                color=ColorTag(raw_item["color"]),
                label=raw_item["label"],
                raw_text=raw_item["raw_text"],
                bbox=BBox(x=x, y=y, w=w, h=h),
                confidence=raw_item.get("confidence", 1.0),
            )
            items.append(item)
        except Exception as exc:  # noqa: BLE001 — 모델 출력은 신뢰 못 하므로 항목 단위로만 격리
            warnings.append(f"{i}번째 항목 파싱 실패, 건너뜀: {exc}")

    extraction = DocumentExtraction(
        source_image=str(image_path),
        items=items,
        document_text=raw.get("document_text", ""),
        warnings=warnings,
    )
    return double_check(extraction)
