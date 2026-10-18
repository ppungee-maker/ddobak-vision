"""CLI: ddobak-vision extract <공문 사진>."""

from __future__ import annotations

import argparse
from pathlib import Path

from .extract import extract_document
from .overlay import render_overlay
from .providers.anthropic_provider import AnthropicVisionProvider
from .providers.base import VisionProvider
from .providers.mock_provider import MockProvider


def _build_provider(name: str) -> VisionProvider:
    if name == "mock":
        return MockProvider()
    if name == "anthropic":
        return AnthropicVisionProvider()
    raise ValueError(f"알 수 없는 provider: {name}")


def cmd_extract(args: argparse.Namespace) -> int:
    image_path = Path(args.image)
    if not image_path.exists():
        print(f"[!] 이미지 없음: {image_path}")
        return 1

    extraction = extract_document(image_path, provider=_build_provider(args.provider))

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = image_path.stem

    json_path = out_dir / f"{stem}-extraction.json"
    json_path.write_text(extraction.model_dump_json(indent=2), encoding="utf-8")
    overlay_path = render_overlay(extraction, out_path=out_dir / f"{stem}-overlay.png")

    print(f"[✓] 추출 {len(extraction.items)}건 → {json_path}")
    print(f"[✓] 3색 오버레이 → {overlay_path}")
    for item in extraction.items:
        mark = "✓" if item.verified else ("✗" if item.verified is False else "-")
        print(f"  [{mark}] ({item.color.value}) {item.label}: {item.raw_text}")
    for warning in extraction.warnings:
        print(f"  [경고] {warning}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ddobak-vision", description="또박또박 — 멀티모달 추출 CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    extract_p = sub.add_parser(
        "extract", help="공문 사진 1장을 읽어 추출 JSON + 3색 오버레이 이미지 생성"
    )
    extract_p.add_argument("image", help="공문 사진 경로")
    extract_p.add_argument("--provider", choices=["mock", "anthropic"], default="mock")
    extract_p.add_argument("--out-dir", default="output_example")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "extract":
        return cmd_extract(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
