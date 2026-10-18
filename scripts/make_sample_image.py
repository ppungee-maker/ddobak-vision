"""샘플 공문 placeholder 이미지 생성 (실제 공문 30장 수집은 RAG/데이터 담당 몫 — 기획서 역할분담 참고).

여기서는 파이프라인을 end-to-end로 시연할 최소 placeholder 한 장만 만든다.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent.parent / "sample_data" / "sample-자동차세고지서.jpg"
FONT_PATH = Path("/Library/Fonts/NanumGothic.ttf")

WIDTH, HEIGHT = 1000, 1400


def main() -> None:
    img = Image.new("RGB", (WIDTH, HEIGHT), "white")
    draw = ImageDraw.Draw(img)
    title_font = ImageFont.truetype(str(FONT_PATH), 40)
    body_font = ImageFont.truetype(str(FONT_PATH), 28)

    draw.rectangle([0, 0, WIDTH - 1, HEIGHT - 1], outline="black", width=2)
    draw.text((60, 60), "2026년 자동차세 납부고지서", fill="black", font=title_font)
    draw.text((60, 160), "납부금액: 금 48,200원", fill="black", font=body_font)
    draw.text((60, 240), "납부기한: 2026.10.31까지", fill="black", font=body_font)
    draw.text((100, 980), "구비서류: 신분증, 차량등록증 사본", fill="black", font=body_font)
    draw.text((60, 1300), "대전광역시 ○○구청 세무과", fill="black", font=body_font)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, quality=90)
    print(f"[✓] {OUT}")


if __name__ == "__main__":
    main()
