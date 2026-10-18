"""추출 결과 스키마.

기획서의 "3색 빨간펜"을 그대로 타입으로 못박는다: 빨강=낼 돈, 파랑=기한, 초록=챙길 서류.
좌표(bbox)는 이미지 해상도에 무관하도록 0~1 정규화 비율로 둔다 — 원본 사진이 어떤
크기로 들어오든 overlay 단계에서 실제 픽셀로 변환한다.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator


class ColorTag(str, Enum):
    """3색 빨간펜 색상 — 기획서 의미 그대로."""

    RED = "red"  # 낼 돈 (납부 금액)
    BLUE = "blue"  # 기한 (마감일)
    GREEN = "green"  # 챙길 서류 (준비물)

    @property
    def rgb(self) -> tuple[int, int, int]:
        return {
            ColorTag.RED: (220, 38, 38),
            ColorTag.BLUE: (37, 99, 235),
            ColorTag.GREEN: (22, 163, 74),
        }[self]


class BBox(BaseModel):
    """정규화 바운딩 박스 — x, y, w, h 모두 [0, 1] 비율."""

    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)
    w: float = Field(gt=0, le=1)
    h: float = Field(gt=0, le=1)

    def to_pixels(self, image_width: int, image_height: int) -> tuple[int, int, int, int]:
        """(left, top, right, bottom) 픽셀 좌표로 변환."""
        left = round(self.x * image_width)
        top = round(self.y * image_height)
        right = round((self.x + self.w) * image_width)
        bottom = round((self.y + self.h) * image_height)
        return left, top, right, bottom


class ExtractedItem(BaseModel):
    """공문 원본 위 한 군데에 그어진 형광펜 한 줄."""

    id: str
    color: ColorTag
    label: str  # 쉬운 말 풀이 (예: "앱 납부 금액")
    raw_text: str  # 원문에서 그대로 읽은 값 (예: "금 48,200원")
    bbox: BBox
    page: int = 1
    confidence: float = Field(default=1.0, ge=0, le=1)

    # double_check 단계에서 채워짐 (amount/date 계열만 해당, None=해당 없음)
    parsed_amount_won: int | None = None
    parsed_date_iso: str | None = None
    verified: bool | None = None
    verify_note: str | None = None

    @field_validator("raw_text", "label")
    @classmethod
    def _not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("빈 문자열은 허용하지 않음")
        return v


class DocumentExtraction(BaseModel):
    """공문 한 장(여러 페이지 가능)의 전체 추출 결과."""

    source_image: str
    items: list[ExtractedItem] = Field(default_factory=list)
    document_text: str = ""  # 비전 LLM이 함께 반환한 원문 전체 텍스트 (이중 확인용)
    warnings: list[str] = Field(default_factory=list)

    def items_by_color(self, color: ColorTag) -> list[ExtractedItem]:
        return [it for it in self.items if it.color == color]
