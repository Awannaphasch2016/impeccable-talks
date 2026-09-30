"""The telegram pack exposes the slack-mini surface: a supervised adapter and /healthz."""

import ast
import pathlib
import tomllib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class PackSurfaceTest(unittest.TestCase):
    def test_pack_service_matches_slack_mini_shape(self):
        doc = tomllib.loads((ROOT / "pack.toml").read_text(encoding="utf-8"))
        self.assertEqual(doc["pack"]["name"], "telegram")
        self.assertEqual(doc["pack"]["schema"], 2)
        service = doc["service"][0]
        self.assertEqual(service["name"], "telegram")
        self.assertEqual(service["kind"], "proxy_process")
        self.assertEqual(service["process"]["health_path"], "/healthz")
        self.assertEqual(service["process"]["command"][-1], "./adapter/bridge.py")

    def test_bridge_serves_healthz_and_post_message(self):
        source = (ROOT / "adapter" / "bridge.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        functions = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        }
        self.assertTrue({"health", "post_message", "serve", "serve_unix"} <= functions)
        self.assertIn('"/healthz"', source)
        self.assertIn('"/post-message"', source)


if __name__ == "__main__":
    unittest.main()
