"""Claude 비전으로 실제 공문 사진을 읽는 제공자.

`ANTHROPIC_API_KEY` 환경변수가 필요하다. 모델에게 "구겨진 사진 속 표·도장·뒷면까지
읽고 항목 좌표를 뽑는다"(기획서)는 작업을 JSON 스키마로 강제해서 시킨다 — 자유 서술형
답변을 받으면 overlay 단계에서 좌표를 못 쓰므로, 스키마를 벗어나면 즉시 실패시킨다.
"""

from __future__ import annotations

import base64
import json
import mimetypes
import re
from pathlib import Path

from anthropic import Anthropic

from .base import RawExtraction, VisionProvider

DEFAULT_MODEL = "claude-sonnet-5"

_SYSTEM_PROMPT = """\
너는 한국 공문(고지서·가정통신문·주민센터 안내문 등) 사진을 읽는 비전 분석기다.
사진 원본 위에 "3색 빨간펜"을 긋기 위한 항목을 뽑아라:
- red: 내야 할 돈 (납부 금액)
- blue: 지켜야 할 기한 (마감일, 신청 기간)
- green: 챙겨야 할 서류/준비물

반드시 아래 JSON 스키마만 출력한다. 설명 문장, 코드펜스, 다른 텍스트는 절대 포함하지 마라:

{
  "document_text": "<사진에서 읽은 본문 전체 텍스트>",
  "items": [
    {
      "color": "red|blue|green",
      "label": "<쉬운 말로 풀어쓴 짧은 설명>",
      "raw_text": "<원문에 적힌 그대로의 값>",
      "bbox": [x, y, w, h],
      "confidence": 0.0~1.0
    }
  ]
}

bbox는 이미지 전체를 1x1로 봤을 때의 비율 좌표다 (x,y=좌상단, w,h=너비/높이, 모두 0~1).
표·도장·뒷면에 적힌 내용도 빠뜨리지 말고 찾아서 포함하라. 해당 색의 항목이 없으면
items에서 그냥 생략한다(빈 값으로 억지로 채우지 않는다).
"""


class AnthropicVisionProvider(VisionProvider):
    def __init__(self, *, model: str = DEFAULT_MODEL, api_key: str | None = None) -> None:
        self._client = Anthropic(api_key=api_key)
        self._model = model

    def extract(self, image_path: Path) -> RawExtraction:
        media_type = mimetypes.guess_type(image_path.name)[0] or "image/jpeg"
        image_b64 = base64.b64encode(image_path.read_bytes()).decode("ascii")

        response = self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            system=_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_b64,
                            },
                        },
                        {
                            "type": "text",
                            "text": "이 공문 사진에서 항목을 뽑아 JSON으로만 답하라.",
                        },
                    ],
                }
            ],
        )

        text = "".join(block.text for block in response.content if block.type == "text")
        return _parse_json_response(text)


def _parse_json_response(text: str) -> RawExtraction:
    """```json ... ``` 코드펜스가 섞여 와도 흡수해서 파싱한다 (API 응답은 모델 출력이라 흔들림)."""
    stripped = text.strip()
    fence_match = re.search(r"```(?:json)?\s*(.*?)\s*```", stripped, re.DOTALL)
    payload = fence_match.group(1) if fence_match else stripped

    data = json.loads(payload)
    if "items" not in data or "document_text" not in data:
        raise ValueError(f"응답이 RawExtraction 스키마를 따르지 않음: {data!r}")
    return data  # type: ignore[return-value]
