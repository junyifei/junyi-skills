#!/usr/bin/env python3

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("check_output_guards.py")
SPEC = importlib.util.spec_from_file_location("check_output_guards", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class OutputGuardTests(unittest.TestCase):
    def test_conditional_reader_and_candidate_status_pass(self):
        text = "如果你也在维护自己的工作流，可以先区分方法与配置。迁移仍在候选阶段。"
        self.assertEqual(MODULE.check(text, "none", "candidate", "none"), [])

    def test_unsupported_scope_fails(self):
        violations = MODULE.check("这是绝大多数创作者都会有的恐惧。", "none", "candidate", "none")
        self.assertEqual(violations[0]["kind"], "unsupported-scope")

    def test_path_status_and_cta_fail(self):
        text = "/home/example/private.md\n迁移已完成。\n欢迎加我微信。"
        kinds = [item["kind"] for item in MODULE.check(text, "none", "candidate", "none")]
        self.assertEqual(kinds, ["absolute-path", "status-overclaim", "unauthorized-cta"])

    def test_audit_language_does_not_trigger_claim_checks(self):
        text = "不得写成已发布，也不能声称所有人都会这样；不升华成每个人都适用；不引导加我微信。"
        self.assertEqual(MODULE.check(text, "none", "candidate", "none"), [])

    def test_deleted_source_quote_does_not_trigger_scope_check(self):
        text = "删去原文句子：事业、家庭、成长，从来就没法切割开。"
        self.assertEqual(MODULE.check(text, "none", "candidate", "none"), [])

    def test_scope_evidence_can_allow_population_wording(self):
        text = "在已说明的样本中，大多数受访者选择了第一项。"
        self.assertEqual(MODULE.check(text, "provided", "candidate", "none"), [])

    def test_unqualified_audience_prediction_fails(self):
        text = "这个标题会让创作者直接代入。"
        violations = MODULE.check(text, "none", "candidate", "none")
        self.assertEqual(violations[0]["kind"], "unsupported-audience-prediction")

    def test_conditional_audience_prediction_passes(self):
        text = "如果创作者已经有同样顾虑，这个入口可能更容易代入。"
        self.assertEqual(MODULE.check(text, "none", "candidate", "none"), [])

    def test_unproven_open_status_fails(self):
        violations = MODULE.check("我直接把自己的开放了。", "none", "candidate", "none")
        self.assertEqual(violations[0]["kind"], "status-overclaim")

    def test_common_belief_without_evidence_fails(self):
        violations = MODULE.check("这篇文章修正一个常见看法。", "none", "candidate", "none")
        self.assertEqual(violations[0]["kind"], "unsupported-scope")

    def test_target_reader_core_concern_without_definition_fails(self):
        violations = MODULE.check("这个标题贴近目标读者的核心顾虑。", "none", "candidate", "none")
        self.assertEqual(violations[0]["kind"], "unsupported-audience-prediction")


if __name__ == "__main__":
    unittest.main()
