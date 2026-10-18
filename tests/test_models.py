from __future__ import annotations

import pytest
from pydantic import ValidationError

from ddobak_vision.models import BBox, ColorTag, ExtractedItem


def test_bbox_to_pixels_converts_normalized_ratio_to_image_size():
    bbox = BBox(x=0.5, y=0.25, w=0.2, h=0.1)
    left, top, right, bottom = bbox.to_pixels(1000, 2000)
    assert (left, top, right, bottom) == (500, 500, 700, 700)


def test_color_tag_rgb_is_distinct_per_color():
    rgbs = {tag.rgb for tag in ColorTag}
    assert len(rgbs) == 3


def test_extracted_item_rejects_blank_label():
    with pytest.raises(ValidationError):
        ExtractedItem(
            id="x",
            color=ColorTag.RED,
            label="   ",
            raw_text="금 1,000원",
            bbox=BBox(x=0, y=0, w=0.1, h=0.1),
        )
