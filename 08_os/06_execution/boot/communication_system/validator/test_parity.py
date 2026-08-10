from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import yaml

try:
    from .parity import assert_endpoint_parity, score_cross_model, validate_correction, verify_immutable_published_message
    from .validate_communication_system import CommunicationValidationError
except ImportError:
    from parity import assert_endpoint_parity, score_cross_model, validate_correction, verify_immutable_published_message
    from validate_communication_system import CommunicationValidationError


def message(message_type="result"):
    value = {
        "message_id": "task-001::sender-01::00002", "task_id": "task-001",
        "title": "Correction", "message_type": message_type,
        "sender_endpoint_id": "sender-01", "sender_task_role": "execution",
        "expected_recipient_endpoint_id": "receiver-01",
        "expected_recipient_task_role": "review", "content": "Corrected result.",
        "required_refs": [],
    }
    return value


class ParityTests(unittest.TestCase):
    def test_published_bytes_are_immutable(self):
        with self.assertRaisesRegex(CommunicationValidationError, "mutation_prohibited"):
            verify_immutable_published_message(b"original", b"changed")

    def test_correction_requires_existing_superseded_message(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            previous = root / "messages/sender-01/00001_result.yml"
            previous.parent.mkdir(parents=True)
            previous.write_text("result\n", encoding="utf-8")
            correction = message("correction")
            correction["supersedes"] = "messages/sender-01/00001_result.yml"
            validate_correction(correction, task_root=root)
            correction.pop("supersedes")
            with self.assertRaisesRegex(CommunicationValidationError, "requires_supersedes"):
                validate_correction(correction, task_root=root)

    def test_local_and_web_message_parity(self):
        assert_endpoint_parity(message(), dict(message()))
        web = message()
        web["content"] = "Changed"
        with self.assertRaisesRegex(CommunicationValidationError, "parity_mismatch"):
            assert_endpoint_parity(message(), web)


if __name__ == "__main__":
    unittest.main()

