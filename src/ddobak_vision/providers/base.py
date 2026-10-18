"""비전 추출 제공자 인터페이스.

실제 유료 비전 LLM API 키가 없어도 채점자가 파이프라인 전체를 돌려볼 수 있도록,
기본값은 `MockProvider`로 두고 `AnthropicVisionProvider`로 교체 가능하게 추상화한다
(레포 컨벤션: docs/00-실행가이드.md 참고 패턴).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TypedDict


class RawItem(TypedDict):
    color: str  # "red" | "blue" | "green"
    label: str
    raw_text: str
    bbox: list[float]  # [x, y, w, h] 0~1 정규화
    confidence: float


class RawExtraction(TypedDict):
    items: list[RawItem]
    document_text: str


class VisionProvider(ABC):
    """공문 이미지 1장을 읽어 구조화 JSON(RawExtraction)을 반환하는 제공자."""

    @abstractmethod
    def extract(self, image_path: Path) -> RawExtraction: ...
