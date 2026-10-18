from __future__ import annotations

from pathlib import Path

from ddobak_vision.extract import extract_document
from ddobak_vision.models import ColorTag
from ddobak_vision.providers.mock_provider import MockProvider


def test_extract_document_with_mock_provider_returns_three_verified_items(blank_image: Path):
    extraction = extract_document(blank_image, provider=MockProvider())

    assert extraction.source_image == str(blank_image)
    assert len(extraction.items) == 3
    assert {item.color for item in extraction.items} == {
        ColorTag.RED,
        ColorTag.BLUE,
        ColorTag.GREEN,
    }

    red_item = extraction.items_by_color(ColorTag.RED)[0]
    assert red_item.verified is True
    assert red_item.parsed_amount_won == 48200

    blue_item = extraction.items_by_color(ColorTag.BLUE)[0]
    assert blue_item.verified is True
    assert blue_item.parsed_date_iso == "2026-10-31"
