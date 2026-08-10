from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

try:
    from .sender_zone import (ensure_sender_owned_path, next_sequence,
                              validate_physical_pointer_index, validate_sender_index)
    from .validate_communication_system import CommunicationValidationError
except ImportError:
    from sender_zone import (ensure_sender_owned_path, next_sequence,
                             validate_physical_pointer_index, validate_sender_index)
    from validate_communication_system import CommunicationValidationError


def entry(sequence="00001", sender="sender-01"):
    return {
        "sequence": sequence,
        "message_id": f"task-001::{sender}::{sequence}",
        "title": "Message",
        "message_type": "result",
        "expected_recipient_endpoint_id": "receiver-01",
        "expected_recipient_task_role": "review",
        "exact_message_path": f"messages/{sender}/{sequence}_result.yml",
    }


class SenderZoneTests(unittest.TestCase):
    def test_sequence_allocation_and_exhaustion(self):
        self.assertEqual(next_sequence([]), "00001")
        self.assertEqual(next_sequence([entry()]), "00002")
        with self.assertRaisesRegex(CommunicationValidationError, "sequence_exhausted"):
            next_sequence([entry("10000")])

    def test_reuse_and_out_of_order_are_rejected(self):
        with self.assertRaisesRegex(CommunicationValidationError, "strictly_monotonic"):
            next_sequence([entry("00002"), entry("00001")])
        with self.assertRaisesRegex(CommunicationValidationError, "strictly_monotonic"):
            next_sequence([entry(), entry()])

    def test_cross_sender_path_is_rejected(self):
        with self.assertRaisesRegex(CommunicationValidationError, "cross_sender"):
            ensure_sender_owned_path("messages/other/00001_result.yml", "sender-01")

    def test_index_target_and_append_only_contract(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / "messages" / "sender-01" / "00001_result.yml"
            path.parent.mkdir(parents=True)
            path.write_text("message_id: test\n", encoding="utf-8")
            current = [entry()]
            validate_sender_index(current, sender_endpoint_id="sender-01", task_root=root)
            altered = [dict(current[0], title="changed")]
            with self.assertRaisesRegex(CommunicationValidationError, "append_only"):
                validate_sender_index(altered, sender_endpoint_id="sender-01",
                                      task_root=root, baseline=current)
            path.unlink()
            with self.assertRaisesRegex(CommunicationValidationError, "target_missing"):
                validate_sender_index(current, sender_endpoint_id="sender-01", task_root=root)

    def test_physical_pointer_failure_carries_closed_evidence(self):
        with TemporaryDirectory() as temp:
            with self.assertRaises(CommunicationValidationError) as caught:
                validate_physical_pointer_index(["00001_result.yml"], [], Path(temp))
            self.assertEqual(caught.exception.payload["failure_code"], "SENDER_INDEX_INTEGRITY")
            self.assertFalse(caught.exception.payload["physical_targets_exist"])


if __name__ == "__main__":
    unittest.main()
