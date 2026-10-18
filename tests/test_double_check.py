from __future__ import annotations

from ddobak_vision.double_check import double_check
from ddobak_vision.models import BBox, ColorTag, DocumentExtraction, ExtractedItem


def _item(color: ColorTag, raw_text: str) -> ExtractedItem:
    return ExtractedItem(
        id="item-1",
        color=color,
        label="라벨",
        raw_text=raw_text,
        bbox=BBox(x=0, y=0, w=0.1, h=0.1),
    )


def test_amount_matching_document_text_is_verified():
    extraction = DocumentExtraction(
        source_image="x.jpg",
        items=[_item(ColorTag.RED, "금 48,200원")],
        document_text="납부금액: 금 48,200원",
    )
    result = double_check(extraction)
    assert result.items[0].verified is True
    assert result.items[0].parsed_amount_won == 48200
    assert result.warnings == []


def test_amount_not_found_in_document_text_is_flagged():
    extraction = DocumentExtraction(
        source_image="x.jpg",
        items=[_item(ColorTag.RED, "금 99,999원")],
        document_text="납부금액: 금 48,200원",
    )
    result = double_check(extraction)
    assert result.items[0].verified is False
    assert len(result.warnings) == 1


def test_date_matching_document_text_is_verified():
    extraction = DocumentExtraction(
        source_image="x.jpg",
        items=[_item(ColorTag.BLUE, "2026.10.31까지")],
        document_text="납부기한: 2026.10.31까지",
    )
    result = double_check(extraction)
    assert result.items[0].verified is True
    assert result.items[0].parsed_date_iso == "2026-10-31"


def test_unparseable_date_is_flagged_not_crashed():
    extraction = DocumentExtraction(
        source_image="x.jpg",
        items=[_item(ColorTag.BLUE, "다음 공고 시까지")],
        document_text="아무 날짜도 없음",
    )
    result = double_check(extraction)
    assert result.items[0].verified is False
    assert result.items[0].parsed_date_iso is None


def test_green_items_are_not_verified_amount_or_date():
    extraction = DocumentExtraction(
        source_image="x.jpg",
        items=[_item(ColorTag.GREEN, "신분증 지참")],
        document_text="아무 내용",
    )
    result = double_check(extraction)
    assert result.items[0].verified is None
    assert result.warnings == []
