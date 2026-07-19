#!/usr/bin/env python3
"""Tests for the static-site validator."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("validate_static_site.py")
SPEC = importlib.util.spec_from_file_location("validate_static_site", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


GOOD_HTML = """<!doctype html>
<html lang="zh-CN"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>示例官网</title><meta name="description" content="可信的示例官网">
<meta property="og:title" content="示例官网"><meta property="og:description" content="可信的示例官网">
<meta property="og:image" content="https://example.com/og.jpg"><link rel="icon" href="favicon.svg">
</head><body><main><h1>示例官网</h1><img src="photo.svg" alt="创作者肖像"></main></body></html>"""


class StaticSiteValidatorTests(unittest.TestCase):
    def make_site(self, html: str = GOOD_HTML) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        (root / "index.html").write_text(html, encoding="utf-8")
        (root / "favicon.svg").write_text("<svg xmlns='http://www.w3.org/2000/svg'/>", encoding="utf-8")
        (root / "photo.svg").write_text("<svg xmlns='http://www.w3.org/2000/svg'/>", encoding="utf-8")
        return root

    def test_complete_site_passes(self) -> None:
        errors, warnings = MODULE.validate_site(self.make_site())
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_requires_root_index(self) -> None:
        root = self.make_site()
        (root / "index.html").rename(root / "about.html")
        errors, _ = MODULE.validate_site(root)
        self.assertIn("missing index.html at the published root", errors)

    def test_requires_language_title_and_viewport(self) -> None:
        root = self.make_site("<html><head></head><body><h1>x</h1></body></html>")
        errors, _ = MODULE.validate_site(root)
        self.assertTrue(any("missing html lang" in item for item in errors))
        self.assertTrue(any("missing non-empty title" in item for item in errors))
        self.assertTrue(any("missing viewport meta" in item for item in errors))

    def test_requires_image_alt(self) -> None:
        root = self.make_site(GOOD_HTML.replace(' alt="创作者肖像"', ""))
        errors, _ = MODULE.validate_site(root)
        self.assertTrue(any("missing alt attribute" in item for item in errors))

    def test_detects_broken_local_asset(self) -> None:
        root = self.make_site(GOOD_HTML.replace("photo.svg", "missing.svg"))
        errors, _ = MODULE.validate_site(root)
        self.assertTrue(any("missing local src target" in item for item in errors))

    def test_detects_path_escape(self) -> None:
        root = self.make_site(GOOD_HTML.replace("photo.svg", "../private.svg"))
        errors, _ = MODULE.validate_site(root)
        self.assertTrue(any("escapes site root" in item for item in errors))

    def test_detects_private_path_and_secret(self) -> None:
        private_path = "/" + "Users/example/private"
        secret_assignment = "api" + '_key="abcdefghijklmnopqrstuv"'
        html = GOOD_HTML.replace(
            "</body>",
            f"<p>{private_path}</p><script>const {secret_assignment};</script></body>",
        )
        errors, _ = MODULE.validate_site(self.make_site(html))
        self.assertTrue(any("private path" in item for item in errors))
        self.assertTrue(any("assigned secret" in item for item in errors))

    def test_metadata_gaps_are_warnings(self) -> None:
        html = GOOD_HTML.replace('<meta property="og:image" content="https://example.com/og.jpg">', "")
        _, warnings = MODULE.validate_site(self.make_site(html))
        self.assertTrue(any("missing og:image" in item for item in warnings))

    def test_javascript_url_is_rejected(self) -> None:
        html = GOOD_HTML.replace("</main>", '<a href="javascript:void(0)">坏链接</a></main>')
        errors, _ = MODULE.validate_site(self.make_site(html))
        self.assertTrue(any("javascript: URL" in item for item in errors))


if __name__ == "__main__":
    unittest.main()
