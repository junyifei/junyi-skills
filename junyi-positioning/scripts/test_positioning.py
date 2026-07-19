#!/usr/bin/env python3
"""Regression tests for the canonical IP strategy-book contract."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("check_strategy_book.py")
SPEC = importlib.util.spec_from_file_location("check_strategy_book", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def valid_book() -> str:
    b00_fields = "\n".join(f"- {term}：示例" for term in MODULE.B00_TERMS)
    b09_fields = "\n".join(f"- {term}：示例" for term in MODULE.B09_TERMS)
    bodies = {
        "B00": b00_fields,
        "B01": "【事实】F01\n【推断】I01\n【假设】H01\n【未知】U01",
        "B02": "个人真实资产与 100 题内容燃料",
        "B03": "用户情境与需求",
        "B04": "用户变化",
        "B05": "成为主定位前必须通过的基础检查",
        "B06": "内容主线",
        "B07": "能力证明",
        "B08": "产品商业",
        "B09": b09_fields,
        "B10": "30 天与 90 天验证",
        "B11": "风险、未知与修订",
    }
    chapters = "\n\n".join(f"## {key}｜章节\n\n{bodies[key]}" for key in MODULE.CHAPTERS)
    return f"# IP战略书\n\n{chapters}\n"


class StrategyBookChecks(unittest.TestCase):
    def test_valid_book_passes(self) -> None:
        errors, warnings = MODULE.check_text(valid_book())
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_missing_chapter_fails(self) -> None:
        text = valid_book().replace("## B08｜章节\n\n产品商业\n\n", "")
        errors, _ = MODULE.check_text(text)
        self.assertTrue(any("B00-B11" in error for error in errors))

    def test_reordered_chapters_fail(self) -> None:
        text = valid_book()
        b10 = MODULE.chapter_body(text, "B10")
        b11 = MODULE.chapter_body(text, "B11")
        text = text.replace(b10, "__B10__").replace(b11, b10).replace("__B10__", b11)
        errors, _ = MODULE.check_text(text)
        self.assertTrue(any("B00-B11" in error for error in errors))

    def test_missing_b00_contract_fails(self) -> None:
        text = valid_book().replace("- 真正买方：示例\n", "")
        errors, _ = MODULE.check_text(text)
        self.assertIn("B00 missing required field: 真正买方", errors)

    def test_missing_boundary_fails(self) -> None:
        text = valid_book().replace("- 隐私边界：示例\n", "")
        errors, _ = MODULE.check_text(text)
        self.assertIn("B09 missing required boundary: 隐私边界", errors)

    def test_absolute_path_and_forbidden_name_fail(self) -> None:
        private_path = "/" + "Users/example/private/SecretName"
        text = valid_book() + f"\n{private_path}\n"
        errors, _ = MODULE.check_text(text, forbid_names=["SecretName"])
        self.assertTrue(any("absolute user path" in error for error in errors))
        self.assertTrue(any("forbidden case-specific name" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
