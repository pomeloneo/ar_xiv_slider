"""Delivery retries preserve both successful notification and learner evidence."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location('finalizer', Path(__file__).resolve().parents[1] / 'scripts/finalize-batch.py')
finalizer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(finalizer)


class HistoryTests(unittest.TestCase):
    def test_verification_retry_preserves_sent_receipt_and_real_answer(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'history.jsonl'
            previous = {'arxiv_base_id': '2609.12345', 'publication': {'commit': 'same'},
                        'notification_status': 'sent', 'notification': {'message_id': 'receipt'},
                        'learner_answer': 'My actual reasoning', 'mastery_verified': True, 'pending_question': None}
            path.write_text(json.dumps(previous) + '\n')
            pending = {'arxiv_base_id': '2609.12345', 'publication': {'commit': 'same'},
                       'notification_status': 'not_sent', 'learner_answer': None, 'mastery_verified': False,
                       'pending_question': 'Old unanswered question'}
            finalizer.update_history(path, [pending])
            saved = json.loads(path.read_text())
            self.assertEqual(saved['notification_status'], 'sent')
            self.assertEqual(saved['notification']['message_id'], 'receipt')
            self.assertEqual(saved['learner_answer'], 'My actual reasoning')
            self.assertTrue(saved['mastery_verified'])
            self.assertEqual(pending['notification_status'], 'sent')
            self.assertIsNone(saved['pending_question'])
            self.assertEqual(pending['learner_answer'], 'My actual reasoning')
            self.assertIsNone(pending['pending_question'])


if __name__ == '__main__':
    unittest.main()
