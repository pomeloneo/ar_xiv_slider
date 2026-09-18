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

    def test_digest_uses_actual_count_and_all_present_directions(self):
        papers = [
            {
                'direction': 'AI', 'title_zh': '智能体安全',
                'publication': {'overview_url': 'https://example.test/ai/'},
            },
            {
                'direction': '科技与产业', 'title_zh': '数据中心供电',
                'publication': {'overview_url': 'https://example.test/industry/'},
            },
            {
                'direction': '社会研究', 'title_zh': '住房与流动',
                'publication': {'overview_url': 'https://example.test/social/'},
            },
        ]
        digest = finalizer.build_digest(papers)
        self.assertIn('新增 3 篇完整论文学习包', digest)
        self.assertIn('AI 1 篇', digest)
        self.assertIn('社会研究 1 篇', digest)
        self.assertIn('科技与产业 1 篇', digest)
        self.assertIn('[数据中心供电](https://example.test/industry/)', digest)
        self.assertNotIn('新增 30 篇', digest)

    def test_notification_idempotency_key_is_bound_to_publication_commit(self):
        day = Path('/tmp/2026-09-18')
        first = finalizer.notification_idempotency_key(day, 'a' * 40)
        second = finalizer.notification_idempotency_key(day, 'b' * 40)
        self.assertEqual(first, 'arxiv-batch-2026-09-18-aaaaaaaaaaaa')
        self.assertNotEqual(first, second)

    def test_receipt_short_circuit_requires_same_successful_commit(self):
        current = 'a' * 40
        self.assertTrue(finalizer.successful_receipt_for_commit(
            {'ok': True, 'publication_commit': current}, current))
        self.assertFalse(finalizer.successful_receipt_for_commit(
            {'ok': True, 'publication_commit': 'b' * 40}, current))
        self.assertFalse(finalizer.successful_receipt_for_commit({'ok': True}, current))
        self.assertFalse(finalizer.successful_receipt_for_commit(
            {'ok': False, 'publication_commit': current}, current))


class HistoryEventIdentityTests(unittest.TestCase):
    def test_reselection_keeps_distinct_events_and_inherits_base_progress(self):
        # The same paper published on two different days must stay two separate
        # history events (keyed by publication), while the learner's verified
        # progress on that paper carries forward by base ID.
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'history.jsonl'
            first_event = {
                'arxiv_base_id': '2609.55555', 'version': 'v1',
                'publication_key': '2026-09-01-2609.55555',
                'notification_status': 'sent', 'notification': {'message_id': 'first'},
                'learner_answer': 'I explained the mechanism', 'mastery_verified': True,
                'pending_question': None,
            }
            path.write_text(json.dumps(first_event, ensure_ascii=False) + '\n')
            second_event = {
                'arxiv_base_id': '2609.55555', 'version': 'v2',
                'publication_key': '2026-09-18-2609.55555',
                'notification_status': 'not_sent',
                'learner_answer': None, 'mastery_verified': False,
                'pending_question': 'Fresh question for the new write-up',
            }
            finalizer.update_history(path, [second_event])

            rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
            keys = {row['publication_key'] for row in rows}
            self.assertEqual(len(rows), 2)
            self.assertEqual(keys, {'2026-09-01-2609.55555', '2026-09-18-2609.55555'})
            # The earlier delivery is untouched.
            first = next(r for r in rows if r['publication_key'] == '2026-09-01-2609.55555')
            self.assertEqual(first['notification_status'], 'sent')
            self.assertEqual(first['version'], 'v1')
            # The new event inherits real mastery evidence from the base ID.
            second = next(r for r in rows if r['publication_key'] == '2026-09-18-2609.55555')
            self.assertEqual(second['version'], 'v2')
            self.assertEqual(second['learner_answer'], 'I explained the mechanism')
            self.assertTrue(second['mastery_verified'])
            # A brand-new publication event has not itself been notified.
            self.assertEqual(second['notification_status'], 'not_sent')

    def test_legacy_row_without_publication_key_falls_back_to_base_id(self):
        # Older records stored no publication_key; they must still round-trip
        # under the base ID rather than being dropped or duplicated.
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'history.jsonl'
            legacy = {'arxiv_base_id': '2608.23416', 'publication_key': None,
                      'notification_status': 'sent', 'learner_answer': 'legacy note',
                      'mastery_verified': True, 'pending_question': None}
            path.write_text(json.dumps(legacy, ensure_ascii=False) + '\n')
            republish = {'arxiv_base_id': '2608.23416', 'publication_key': None,
                         'notification_status': 'not_sent', 'learner_answer': None,
                         'mastery_verified': False, 'pending_question': None}
            finalizer.update_history(path, [republish])
            rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]['learner_answer'], 'legacy note')
            self.assertTrue(rows[0]['mastery_verified'])
            self.assertEqual(rows[0]['notification_status'], 'sent')


if __name__ == '__main__':
    unittest.main()
