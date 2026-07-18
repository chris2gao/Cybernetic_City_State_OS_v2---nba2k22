from __future__ import annotations

import argparse
import importlib.util
import os
import tempfile
import time
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "chat_channel.py"
spec = importlib.util.spec_from_file_location("chat_channel", SCRIPT)
module = importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(module)

class ChatChannelTests(unittest.TestCase):
    def new(self, root):
        module.new(argparse.Namespace(root=root, topic="test", participants="codex,fable", task_ref=".ai/TASKS/x.md"))
    def post(self, root, body="pointer: x"):
        module.post(argparse.Namespace(root=root, topic="test", sender="codex", session_id="session-1", reply_to=None, body=body, body_file=None))
    def test_new_and_monotonic_atomic_posts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); self.new(root); self.post(root); self.post(root)
            names = [p.name for p in sorted((root / "test").glob("*.md"))]
            self.assertEqual(names, ["001_codex.md", "002_codex.md"])
            self.assertIn("seq: 1", (root / "test" / names[0]).read_text(encoding="utf-8"))
    def test_rejects_long_body_and_unsafe_topic(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); self.new(root)
            with self.assertRaises(ValueError): self.post(root, "\n".join("x" for _ in range(31)))
            with self.assertRaises(ValueError): module.channel(root, "../escape")
    def test_gc_only_removes_old_messages(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); self.new(root); self.post(root)
            old = root / "test" / "001_codex.md"; os.utime(old, (time.time() - 31 * 86400,) * 2)
            module.gc(argparse.Namespace(root=root, topic="test", days=30))
            self.assertFalse(old.exists()); self.assertTrue((root / "test" / "_channel.yml").exists())
if __name__ == "__main__": unittest.main()
