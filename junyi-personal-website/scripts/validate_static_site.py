#!/usr/bin/env python3
"""Check a static website for common publication blockers and metadata gaps."""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


PRIVATE_PATH_RE = re.compile(r"(?:/" r"Users/[^\s\"'<>]+|[A-Za-z]:\\Users\\[^\s\"'<>]+)")
SECRET_PATTERNS = (
    ("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{30,}\b")),
    ("generic assigned secret", re.compile(r"(?i)\b(?:api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{16,}['\"]")),
)


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.html_lang = ""
        self.title_depth = 0
        self.title_text: list[str] = []
        self.h1_count = 0
        self.metas: list[dict[str, str]] = []
        self.links: list[dict[str, str]] = []
        self.images: list[dict[str, str]] = []
        self.resources: list[tuple[str, str]] = []
        self.favicons = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        tag = tag.lower()
        if tag == "html":
            self.html_lang = data.get("lang", "").strip()
        elif tag == "title":
            self.title_depth += 1
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "meta":
            self.metas.append(data)
        elif tag == "a":
            self.links.append(data)
            if data.get("href"):
                self.resources.append(("href", data["href"]))
        elif tag == "img":
            self.images.append(data)
            if data.get("src"):
                self.resources.append(("src", data["src"]))
            if data.get("srcset"):
                for candidate in data["srcset"].split(","):
                    url = candidate.strip().split(" ", 1)[0]
                    if url:
                        self.resources.append(("srcset", url))
        elif tag in {"script", "source", "video", "audio", "iframe"} and data.get("src"):
            self.resources.append(("src", data["src"]))
        elif tag == "link":
            rel = set(data.get("rel", "").lower().split())
            if "icon" in rel or "shortcut" in rel and "icon" in rel:
                self.favicons += 1
            if data.get("href"):
                self.resources.append(("href", data["href"]))

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title" and self.title_depth:
            self.title_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.title_depth:
            self.title_text.append(data)


def _meta_exists(parser: PageParser, *, name: str | None = None, prop: str | None = None) -> bool:
    for meta in parser.metas:
        if name and meta.get("name", "").lower() == name.lower() and meta.get("content", "").strip():
            return True
        if prop and meta.get("property", "").lower() == prop.lower() and meta.get("content", "").strip():
            return True
    return False


def _local_target(page: Path, site_root: Path, raw_url: str) -> Path | None:
    url = raw_url.strip()
    if not url or url.startswith(("#", "mailto:", "tel:", "sms:", "data:")):
        return None
    parsed = urlsplit(url)
    if parsed.scheme or parsed.netloc or url.startswith("//"):
        return None
    clean = unquote(parsed.path)
    if not clean:
        return None
    if clean.startswith("/"):
        target = site_root / clean.lstrip("/")
    else:
        target = page.parent / clean
    return target.resolve(strict=False)


def validate_site(site_root: Path) -> tuple[list[str], list[str]]:
    root = site_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    if not root.is_dir():
        return [f"site root is not a directory: {site_root}"], warnings
    if not (root / "index.html").is_file():
        errors.append("missing index.html at the published root")

    html_files = sorted(root.rglob("*.html"))
    if not html_files:
        errors.append("no HTML files found")
        return errors, warnings

    for page in html_files:
        relative = page.relative_to(root).as_posix()
        text = page.read_text(encoding="utf-8", errors="replace")
        parser = PageParser()
        parser.feed(text)

        if not parser.html_lang:
            errors.append(f"{relative}: missing html lang")
        if not "".join(parser.title_text).strip():
            errors.append(f"{relative}: missing non-empty title")
        if parser.h1_count != 1:
            warnings.append(f"{relative}: expected one H1, found {parser.h1_count}")
        if not _meta_exists(parser, name="viewport"):
            errors.append(f"{relative}: missing viewport meta")
        if not _meta_exists(parser, name="description"):
            warnings.append(f"{relative}: missing meta description")
        if not _meta_exists(parser, prop="og:title"):
            warnings.append(f"{relative}: missing og:title")
        if not _meta_exists(parser, prop="og:description"):
            warnings.append(f"{relative}: missing og:description")
        if not _meta_exists(parser, prop="og:image"):
            warnings.append(f"{relative}: missing og:image")
        if not parser.favicons:
            warnings.append(f"{relative}: missing favicon link")

        for index, image in enumerate(parser.images, start=1):
            if "alt" not in image:
                errors.append(f"{relative}: image {index} missing alt attribute")

        for index, link in enumerate(parser.links, start=1):
            href = link.get("href", "").strip()
            if not href:
                warnings.append(f"{relative}: link {index} has empty href")
            if href.lower().startswith("javascript:"):
                errors.append(f"{relative}: link {index} uses javascript: URL")
            if link.get("target", "").lower() == "_blank":
                rel_tokens = set(link.get("rel", "").lower().split())
                if "noopener" not in rel_tokens:
                    warnings.append(f"{relative}: _blank link {index} missing rel=noopener")

        for kind, url in parser.resources:
            target = _local_target(page, root, url)
            if target is None:
                continue
            try:
                target.relative_to(root)
            except ValueError:
                errors.append(f"{relative}: {kind} escapes site root: {url}")
                continue
            candidate = target / "index.html" if target.is_dir() else target
            if not candidate.exists():
                errors.append(f"{relative}: missing local {kind} target: {url}")

        if PRIVATE_PATH_RE.search(text):
            errors.append(f"{relative}: contains a machine-specific private path")
        for label, pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"{relative}: contains a possible {label}")

    return errors, warnings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site", type=Path, help="Published static-site directory")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors, warnings = validate_site(args.site)
    if args.json:
        print(json.dumps({"errors": errors, "warnings": warnings}, ensure_ascii=False, indent=2))
    else:
        for warning in warnings:
            print(f"WARNING: {warning}")
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        if not errors and not (args.strict and warnings):
            print(f"PASS: {args.site} ({len(warnings)} warnings)")
    return 1 if errors or (args.strict and warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
