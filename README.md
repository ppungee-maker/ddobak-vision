# ddobak-vision

> ⚠️ **연습용 레포 — 실제 제출물 아님.** 진짜 팀 레포는
> [dicia-jhoh/codyssey-m3-final](https://github.com/dicia-jhoh/codyssey-m3-final)이고,
> 이 모듈 내용은 그 레포의 `backend/app/extract.py`로 포팅해서 PR로 올렸다
> ([PR #9](https://github.com/dicia-jhoh/codyssey-m3-final/pull/9)). 여기는 그 전에
> 설계를 연습해본 개인 스테이징 레포로만 남겨둔다.

코디세이 AI Native Master 과정 Final-Project **"또박또박 — AI 공문 해독기"**(5인 팀, 팀장
오주현)의 **멀티모달 추출** 모듈. 담당: 황지영.

기획서(`붙임4_Final-Project 상세기획서`) 역할분담 기준 범위:

> 멀티모달 추출 — 비전 LLM 추출·파싱, 3색 표시 좌표, 금액·날짜 이중 확인

공문 사진 한 장을 읽어서,
1. 비전 LLM으로 항목(낼 돈 / 기한 / 챙길 서류)과 그 위치 좌표를 뽑고,
2. 원본 사진 위에 3색 형광펜(빨강=금액, 파랑=기한, 초록=서류)으로 오버레이하고,
3. 금액·날짜처럼 놓치면 손해로 이어지는 필드는 본문과 교차 대조해 한 번 더 확인한다.

## 설치

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## 사용

```bash
# API 키 없이 바로 전체 파이프라인 시연 (mock 제공자)
ddobak-vision extract sample_data/sample-자동차세고지서.jpg

# 실제 Claude 비전으로 (.env 에 ANTHROPIC_API_KEY 필요)
ddobak-vision extract <사진경로> --provider anthropic
```

결과는 `output_example/`에 `<파일명>-extraction.json`(구조화 결과)과
`<파일명>-overlay.png`(3색 오버레이 이미지) 두 개로 저장된다.

## 테스트

```bash
pytest
```

## 구조

```
src/ddobak_vision/
├── models.py              # ColorTag(red/blue/green) · BBox(정규화 좌표) · ExtractedItem · DocumentExtraction
├── providers/
│   ├── base.py             # VisionProvider 인터페이스 (RawExtraction JSON 계약)
│   ├── mock_provider.py    # API 키 없이 쓰는 결정적 데모 제공자 (기본값)
│   └── anthropic_provider.py  # Claude 비전 실제 호출
├── extract.py              # provider → RawExtraction → DocumentExtraction(pydantic 검증) → double_check
├── double_check.py         # 금액(red)·날짜(blue) 항목을 document_text 본문과 교차 대조해 verified 플래그
├── overlay.py              # 원본 위에 3색 반투명 하이라이트 합성 (PIL)
└── cli.py                  # ddobak-vision extract <이미지>
```

`VisionProvider`로 추상화해 둔 이유: 실제 공문 30장(법령·데이터 담당 몫)이 모이기 전에도,
그리고 팀 통합 전에도 mock 제공자로 파이프라인 전체(추출→검증→오버레이)가 끝까지
돌아가는 걸 보여줄 수 있어야 한다. 교체는 `--provider anthropic` 하나로 끝난다.

## 남은 일 (스캐폴딩 이후)

- [ ] RAG/데이터 담당(김기훈)의 공문 30장 테스트셋으로 `anthropic` 제공자 좌표 정확도 검증
- [ ] bbox 프롬프트 튜닝 — 현재는 1회 호출로 좌표까지 뽑게 시키는데, 복잡한 표/뒷면은
      영역 분할 2단계(레이아웃 감지 → 항목별 재질의)가 더 안정적일 수 있음
- [ ] PM(오주현)이 통합할 팀 모노레포가 정해지면 이 레포 내용을 그쪽 `extraction/` 모듈로 이식
- [ ] `double_check`는 현재 같은 호출의 `document_text` 자기 일관성만 봄 — 필요하면 별도
      OCR 패스(예: Tesseract)로 완전히 독립된 2차 소스 교차 확인으로 강화 가능
