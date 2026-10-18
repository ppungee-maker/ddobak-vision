"""금액(red)·날짜(blue) 이중 확인.

기획서의 "금액·날짜 이중 확인": 공문의 금액·기한은 놓치면 가산금/기회비용으로 바로
이어지는 민감 필드라, item.raw_text 혼자만 믿지 않고 같은 추출 결과의 document_text
본문에도 같은 값이 실제로 등장하는지 다시 대조해 verified 플래그를 단다 — 비전 LLM이
raw_text만 다르게 환각했을 때 잡아내기 위한 2차 패스.
"""

from __future__ import annotations

import re
from datetime import date

from .models import ColorTag, DocumentExtraction

_AMOUNT_RE = re.compile(r"([\d][\d,]*)\s*원")
_DATE_RE_FULL = re.compile(r"(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})")
_DATE_RE_MD = re.compile(r"(\d{1,2})월\s*(\d{1,2})일")


def _parse_amount_won(text: str) -> int | None:
    m = _AMOUNT_RE.search(text)
    if not m:
        return None
    return int(m.group(1).replace(",", ""))


def _parse_date_iso(text: str, *, fallback_year: int) -> str | None:
    m = _DATE_RE_FULL.search(text)
    if m:
        y, mo, d = (int(g) for g in m.groups())
        try:
            return date(y, mo, d).isoformat()
        except ValueError:
            return None
    m = _DATE_RE_MD.search(text)
    if m:
        mo, d = (int(g) for g in m.groups())
        try:
            return date(fallback_year, mo, d).isoformat()
        except ValueError:
            return None
    return None


def double_check(extraction: DocumentExtraction) -> DocumentExtraction:
    """extraction.items를 제자리에서 검증하고 같은 객체를 돌려준다."""
    doc_text = extraction.document_text
    doc_amounts = {int(m.group(1).replace(",", "")) for m in _AMOUNT_RE.finditer(doc_text)}
    doc_month_days = {(int(mo), int(d)) for mo, d in _DATE_RE_MD.findall(doc_text)}
    doc_full_dates: set[str] = set()
    for y, mo, d in _DATE_RE_FULL.findall(doc_text):
        try:
            doc_full_dates.add(date(int(y), int(mo), int(d)).isoformat())
        except ValueError:
            continue

    this_year = date.today().year

    for item in extraction.items:
        if item.color == ColorTag.RED:
            parsed = _parse_amount_won(item.raw_text)
            item.parsed_amount_won = parsed
            if parsed is None:
                item.verified = False
                item.verify_note = "raw_text에서 금액 숫자를 파싱하지 못함"
            else:
                item.verified = parsed in doc_amounts
                if not item.verified:
                    item.verify_note = (
                        "raw_text 금액이 document_text 본문에서 재확인되지 않음 (오타/환각 의심)"
                    )

        elif item.color == ColorTag.BLUE:
            parsed = _parse_date_iso(item.raw_text, fallback_year=this_year)
            item.parsed_date_iso = parsed
            if parsed is None:
                item.verified = False
                item.verify_note = "raw_text에서 날짜를 파싱하지 못함"
            else:
                mo, d = int(parsed[5:7]), int(parsed[8:10])
                item.verified = parsed in doc_full_dates or (mo, d) in doc_month_days
                if not item.verified:
                    item.verify_note = (
                        "raw_text 날짜가 document_text 본문에서 재확인되지 않음 (오타/환각 의심)"
                    )

        if item.verified is False:
            extraction.warnings.append(f"[{item.id}] {item.verify_note}")

    return extraction
