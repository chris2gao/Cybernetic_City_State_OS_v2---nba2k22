"""Packet shape, raw YAML and required-field regression cases."""
from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import task_packet_input as reader


def packet():
    return {
        "task_id": "test-task", "branch": "codex/test", "exact_base_sha": "a" * 40,
        "allowed_changed_paths": ["src/**"], "required_tests": ["unit tests"],
        "prohibitions": ["force_push"],
        "publisher": {"expected_remote_master_head": "a" * 40,
                      "expected_remote_head": "b" * 40},
    }


class TestPacketShapes(unittest.TestCase):
    def test_canonical_wrapper(self):
        result = reader.normalize_packet({"task_packet": packet()})
        self.assertEqual(result.source_format, "wrapped_v1")
        self.assertEqual(result.body, packet())
        self.assertEqual(result.normalized_fields, ())

    def test_legacy_flat_is_explicit(self):
        result = reader.normalize_packet(packet())
        self.assertEqual(result.source_format, "legacy_flat")

    def test_mixed_wrapper_never_falls_back(self):
        for sibling in ("branch", "notes"):
            with self.subTest(sibling=sibling), self.assertRaisesRegex(
                reader.PacketInputError, "mixed_wrapped"
            ):
                reader.normalize_packet({"task_packet": packet(), sibling: "x"})

    def test_falsey_root_or_body_rejected(self):
        for value in (None, False, 0, "", [], {}):
            for data in (value, {"task_packet": value}):
                with self.subTest(data=data), self.assertRaises(reader.PacketInputError):
                    reader.normalize_packet(data)

    def test_legacy_prohibitions_alias_reported_without_mutating_input(self):
        data = packet()
        data["explicit_prohibitions"] = data.pop("prohibitions")
        snapshot = copy.deepcopy(data)
        result = reader.normalize_packet(data)
        self.assertEqual(result.body["prohibitions"], ["force_push"])
        self.assertEqual(result.normalized_fields, ("explicit_prohibitions->prohibitions",))
        self.assertEqual(data, snapshot)

    def test_canonical_wrapper_requires_canonical_prohibitions(self):
        data = packet()
        data["explicit_prohibitions"] = data.pop("prohibitions")
        with self.assertRaisesRegex(reader.PacketInputError, "field_missing:prohibitions"):
            reader.normalize_packet({"task_packet": data})

    def test_equal_alias_is_reported_and_conflicting_alias_rejected(self):
        data = packet()
        data["explicit_prohibitions"] = ["force_push"]
        self.assertEqual(reader.normalize_packet(data).normalized_fields,
                         ("explicit_prohibitions:equal_to_prohibitions",))
        for alias in ([], ["rebase"], False):
            data["explicit_prohibitions"] = alias
            with self.subTest(alias=alias), self.assertRaises(reader.PacketInputError):
                reader.normalize_packet(data)

    def test_publication_head_is_not_master_fallback_or_conflict(self):
        data = packet()
        result = reader.normalize_packet(data)
        self.assertNotEqual(result.body["publisher"]["expected_remote_head"],
                            result.body["publisher"]["expected_remote_master_head"])
        del data["publisher"]["expected_remote_master_head"]
        self.assertNotIn("expected_remote_master_head",
                         reader.normalize_packet(data).body["publisher"])


class TestRequiredFields(unittest.TestCase):
    def test_missing_required_field_rejected(self):
        for field in ("task_id", "branch", "exact_base_sha", "allowed_changed_paths",
                      "required_tests", "prohibitions"):
            data = packet()
            del data[field]
            with self.subTest(field=field), self.assertRaisesRegex(
                reader.PacketInputError, f"field_missing:{field}"
            ):
                reader.normalize_packet(data)

    def test_string_fields_reject_falsey_and_boolean_values(self):
        for field in ("task_id", "branch"):
            for value in (None, False, True, 0, "", "  ", [], {}):
                data = packet()
                data[field] = value
                with self.subTest(field=field, value=value), self.assertRaises(reader.PacketInputError):
                    reader.normalize_packet(data)

    def test_list_types_and_items_rejected(self):
        for field in ("allowed_changed_paths", "required_tests", "prohibitions"):
            for value in (None, False, True, 0, "src/**", {}, [False], [True], [0], [None], [""]):
                data = packet()
                data[field] = value
                with self.subTest(field=field, value=value), self.assertRaises(reader.PacketInputError):
                    reader.normalize_packet(data)

    def test_nonempty_scope_and_tests_but_explicit_empty_prohibitions(self):
        for field in ("allowed_changed_paths", "required_tests"):
            data = packet()
            data[field] = []
            with self.subTest(field=field), self.assertRaises(reader.PacketInputError):
                reader.normalize_packet(data)
        data = packet()
        data["prohibitions"] = []
        self.assertEqual(reader.normalize_packet(data).body["prohibitions"], [])

    def test_full_sha_required_for_each_declared_head(self):
        for field in ("exact_base_sha", "expected_remote_head", "expected_remote_master_head"):
            for value in (None, False, True, 0, "", "a" * 39, "a" * 41, "g" * 40, "HEAD"):
                data = packet()
                target = data if field == "exact_base_sha" else data["publisher"]
                target[field] = value
                with self.subTest(field=field, value=value), self.assertRaisesRegex(
                    reader.PacketInputError, "40_hex_sha"
                ):
                    reader.normalize_packet(data)

    def test_optional_publisher_and_big_task_types(self):
        for field, bad_values in (("publisher", (False, None, [], "")),
                                  ("big_task", (0, 1, None, [], "true"))):
            for value in bad_values:
                data = packet()
                data[field] = value
                with self.subTest(field=field, value=value), self.assertRaises(reader.PacketInputError):
                    reader.normalize_packet(data)


class TestRawYaml(unittest.TestCase):
    def test_legal_merge_override_and_merge_sequence(self):
        text = """defaults: &defaults {branch: old, role: execution}
other: &other {branch: ignored, count: 1}
body:
  <<: [*defaults, *other]
  branch: new
"""
        data = reader.load_yaml_text(text)
        self.assertEqual(data["body"], {"branch": "new", "role": "execution", "count": 1})

    def test_legal_packet_merge_override(self):
        text = """task_packet:
  task_id: test
  branch: codex/test
  exact_base_sha: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
  allowed_changed_paths: &paths [src/**]
  required_tests: [unit]
  prohibitions: []
  publisher:
    <<: &baseline {expected_remote_master_head: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa}
    expected_remote_master_head: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
"""
        result = reader.normalize_packet(reader.load_yaml_text(text))
        self.assertEqual(result.body["publisher"]["expected_remote_master_head"], "b" * 40)

    def test_duplicate_explicit_keys_rejected_before_merge(self):
        for text in ("a: 1\na: 2\n", "body: {a: 1, a: 1}\n",
                     "a: &a {x: 1, x: 2}\nb: {<<: *a, x: 3}\n",
                     "a: &a {x: 1}\nb: {<<: *a, <<: *a}\n"):
            with self.subTest(text=text), self.assertRaisesRegex(
                reader.PacketInputError, "duplicate_explicit_key"
            ):
                reader.load_yaml_text(text)

    def test_repeated_noncyclic_aliases_are_legal(self):
        data = reader.load_yaml_text("a: &a [x, y]\nb: [*a, *a]\n")
        self.assertEqual(data["b"], [["x", "y"], ["x", "y"]])

    def test_cycles_are_structured_input_errors(self):
        for text in ("a: &a [*a]\n", "a: &a {x: *a}\n", "a: &a {<<: *a}\n"):
            with self.subTest(text=text), self.assertRaisesRegex(reader.PacketInputError, "yaml_cycle"):
                reader.load_yaml_text(text)

    def test_invalid_yaml_and_key_types_rejected(self):
        for text in ("a: [\n", "a: {<<: nope}\n", "true: value\n", "[x]: y\n", "---\n---\n"):
            with self.subTest(text=text), self.assertRaises(reader.PacketInputError):
                reader.load_yaml_text(text)

    def test_bad_utf8_is_structured_input_error(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "packet.yml"
            path.write_bytes(b"task_packet: \xff")
            with self.assertRaisesRegex(reader.PacketInputError, "packet_read_error:UnicodeDecodeError"):
                reader.read_packet(path)

    def test_boolean_packet_fields_from_yaml_are_rejected(self):
        for literal in ("true", "false", "yes", "no", "on", "off"):
            data = reader.load_yaml_text(f"task_id: {literal}\n")
            full = packet()
            full.update(data)
            with self.subTest(literal=literal), self.assertRaises(reader.PacketInputError):
                reader.normalize_packet(full)


if __name__ == "__main__":
    unittest.main()
