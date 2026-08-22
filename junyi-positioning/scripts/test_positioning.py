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

SCORE_SCRIPT = Path(__file__).with_name("score_candidates.py")
SCORE_SPEC = importlib.util.spec_from_file_location("score_candidates", SCORE_SCRIPT)
assert SCORE_SPEC and SCORE_SPEC.loader
SCORE_MODULE = importlib.util.module_from_spec(SCORE_SPEC)
SCORE_SPEC.loader.exec_module(SCORE_MODULE)

SKILL_TEXT = Path(__file__).parents[1].joinpath("SKILL.md").read_text(encoding="utf-8")
FORWARD_TEST_TEXT = (
    Path(__file__).parents[1]
    .joinpath("references", "forward-test-cases.md")
    .read_text(encoding="utf-8")
)


def valid_book() -> str:
    b00_fields = "\n".join(f"- {term}：示例" for term in MODULE.B00_TERMS)
    b09_fields = "\n".join(f"- {term}：示例" for term in MODULE.B09_TERMS)
    bodies = {
        "B00": b00_fields,
        "B01": "【事实】F01\n【推断】I01\n【假设】H01\n【未知】U01",
        "B02": "个人真实资产、跨场景能力复现与 100 题内容燃料",
        "B03": "用户情境、需求与买方适配与拒绝",
        "B04": "用户变化、结果阶梯与 7／30 天持续使用",
        "B05": "成为主定位前必须通过的基础检查",
        "B06": "内容主线",
        "B07": "能力证明、能力信任、理解信任与判断信任",
        "B08": "产品商业",
        "B09": b09_fields,
        "B10": "30 天与 90 天验证、端到端证据链、唯一主要变量与停止条件",
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

    def test_missing_v04_contract_fails(self) -> None:
        text = valid_book().replace("跨场景能力复现", "能力盘点")
        errors, _ = MODULE.check_text(text)
        self.assertIn("B02 missing required field: 跨场景能力复现", errors)


class CandidateDecisionChecks(unittest.TestCase):
    def candidate(self, gate_status: str, *, evidence: list[str] | None = None) -> dict:
        return {
            "name": "候选方向",
            "gates": {key: gate_status for key in SCORE_MODULE.GATES},
            "scores": {key: 5 for key in SCORE_MODULE.WEIGHTS},
            "evidence": evidence if evidence is not None else ["E001"],
        }

    def test_failed_basic_rejects_even_with_perfect_score(self) -> None:
        raw = self.candidate("pass")
        raw["gates"]["payment_test"] = "fail"
        result, errors = SCORE_MODULE.validate_candidate(raw, 1)
        self.assertEqual(errors, [])
        self.assertEqual(result["score"], 100.0)
        self.assertEqual(result["outcome"], "reject")

    def test_unknown_basic_needs_evidence(self) -> None:
        raw = self.candidate("pass")
        raw["gates"]["ability_trust"] = "unknown"
        result, errors = SCORE_MODULE.validate_candidate(raw, 1)
        self.assertEqual(errors, [])
        self.assertEqual(result["outcome"], "needs evidence")

    def test_missing_evidence_is_visible(self) -> None:
        result, errors = SCORE_MODULE.validate_candidate(self.candidate("pass", evidence=[]), 1)
        self.assertEqual(errors, [])
        self.assertTrue(result["evidence_warning"])

    def test_rejected_high_score_does_not_rank_above_eligible(self) -> None:
        rejected, rejected_errors = SCORE_MODULE.validate_candidate(self.candidate("pass"), 1)
        rejected["gates"]["payment_test"] = "fail"
        rejected["outcome"] = SCORE_MODULE.outcome_for(rejected["gates"])

        eligible_raw = self.candidate("pass")
        eligible_raw["name"] = "可用方向"
        eligible_raw["scores"] = {key: 3 for key in SCORE_MODULE.WEIGHTS}
        eligible, eligible_errors = SCORE_MODULE.validate_candidate(eligible_raw, 2)

        self.assertEqual(rejected_errors + eligible_errors, [])
        table = SCORE_MODULE.to_markdown([rejected, eligible])
        self.assertLess(table.index("可用方向"), table.index("候选方向"))
        self.assertIn("rejected directions never rank above eligible ones", table)


class SimulationBoundaryChecks(unittest.TestCase):
    def test_skill_declares_sandbox_test_boundary(self) -> None:
        for phrase in (
            "真实资料驱动的沙盒测试",
            "不能把测试中的“接受／确认”解释为正式经营决策",
            "不覆盖当前 `IP战略书.md`",
            "先检索可能存在的答案",
            "不需要有 Obsidian、知识库、旧战略书、成交数据",
            "一次只请对方讲一个真实事件",
            "不依赖脚本、PyYAML、特定知识库软件或联网环境",
        ):
            self.assertIn(phrase, SKILL_TEXT)

    def test_forward_case_covers_real_person_simulation(self) -> None:
        self.assertIn("真人实测不等于正式改版授权", FORWARD_TEST_TEXT)
        self.assertIn("直到使用者追问时才说明测试边界", FORWARD_TEST_TEXT)

    def test_forward_case_covers_stranger_without_knowledge_base(self) -> None:
        self.assertIn("陌生使用者没有知识库也能开始", FORWARD_TEST_TEXT)
        self.assertIn("不因缺少脚本、PyYAML 或联网环境而阻断", FORWARD_TEST_TEXT)


if __name__ == "__main__":
    unittest.main()
