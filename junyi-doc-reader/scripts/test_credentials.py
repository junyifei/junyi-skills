#!/usr/bin/env python3

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))
import feishu_fetcher


class CredentialBoundaryTests(unittest.TestCase):
    def test_reads_only_scoped_environment_variables(self):
        with patch.dict(
            os.environ,
            {
                "DOC_READER_FEISHU_APP_ID": "example-id",
                "DOC_READER_FEISHU_APP_SECRET": "example-secret",
            },
            clear=True,
        ):
            self.assertEqual(
                feishu_fetcher._read_credentials_from_env(),
                ("example-id", "example-secret"),
            )

    def test_missing_secret_fails_closed(self):
        with patch.dict(os.environ, {"DOC_READER_FEISHU_APP_ID": "example-id"}, clear=True):
            with self.assertRaises(SystemExit):
                feishu_fetcher._read_credentials_from_env()

    def test_public_fetcher_has_no_platform_config_path(self):
        source = Path(feishu_fetcher.__file__).read_text(encoding="utf-8")
        self.assertNotIn("openclaw.json\")", source)
        self.assertNotIn("CONFIG_PATH", source)


if __name__ == "__main__":
    unittest.main()
