"""API 키 없이 파이프라인을 끝까지 돌려볼 수 있는 결정적 목 제공자.

실제 비전 LLM 대신, "전형적인 공문 한 장"에 대한 고정된 추출 결과를 돌려준다.
좌표는 실제 사진 속 위치가 아니라 데모용 placeholder — 실제 제공자(AnthropicVisionProvider)로
바꾸면 진짜 좌표가 나온다.
"""

from __future__ import annotations

from pathlib import Path

from .base import RawExtraction, VisionProvider


class MockProvider(VisionProvider):
    def extract(self, image_path: Path) -> RawExtraction:
        document_text = (
            "지방세(자동차세) 납부 안내\n"
            "납부금액: 금 48,200원\n"
            "납부기한: 2026.10.31까지\n"
            "구비서류: 신분증, 차량등록증 사본\n"
            "문의: 주민센터 세무과\n"
        )
        return {
            "document_text": document_text,
            "items": [
                {
                    "color": "red",
                    "label": "앱 납부 금액",
                    "raw_text": "금 48,200원",
                    "bbox": [0.62, 0.18, 0.30, 0.06],
                    "confidence": 0.95,
                },
                {
                    "color": "blue",
                    "label": "납부 기한",
                    "raw_text": "2026.10.31까지",
                    "bbox": [0.62, 0.26, 0.30, 0.06],
                    "confidence": 0.93,
                },
                {
                    "color": "green",
                    "label": "챙길 서류",
                    "raw_text": "신분증, 차량등록증 사본",
                    "bbox": [0.10, 0.70, 0.55, 0.08],
                    "confidence": 0.88,
                },
            ],
        }
