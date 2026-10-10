import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import wait_validation_checks as checks


def feed(state='SUCCESS', bucket='pass'):
    return {'name': checks.FEED_CHECK, 'state': state, 'bucket': bucket}


class WaitTests(unittest.TestCase):
    def test_missing_feed_is_pending(self):
        self.assertEqual(checks.check_state([], []), 'pending')

    def test_feed_and_required_must_succeed(self):
        self.assertEqual(checks.check_state([feed()], []), 'pass')
        self.assertEqual(checks.check_state([feed()], [feed('IN_PROGRESS', 'pending')]), 'pending')

    def test_skipped_failed_and_cancelled_checks_block(self):
        for bucket in ('fail', 'cancel', 'skipping'):
            self.assertEqual(checks.check_state([feed('FAILURE', bucket)], []), 'fail')
            self.assertEqual(checks.check_state([feed()], [feed('FAILURE', bucket)]), 'fail')

    @patch.object(checks, 'gh_json', return_value={'state': 'OPEN', 'headRefOid': 'other'})
    def test_changed_head_blocks(self, gh):
        with self.assertRaisesRegex(RuntimeError, 'head changed'):
            checks.wait('https://github.com/zoyored/dogs/pull/86', 'expected')

    @patch.object(checks, 'gh_json')
    def test_approval_required_is_explicit(self, gh):
        gh.side_effect = [{'state': 'OPEN', 'headRefOid': 'sha'}, [], [],
                          {'workflow_runs': [{'conclusion': 'action_required'}]}]
        with self.assertRaisesRegex(RuntimeError, 'requires approval'):
            checks.wait('https://github.com/zoyored/dogs/pull/86', 'sha')

    @patch.object(checks.time, 'sleep')
    @patch.object(checks, 'gh_json')
    def test_missing_checks_then_success(self, gh, sleep):
        gh.side_effect = [{'state': 'OPEN', 'headRefOid': 'sha'}, [], [], {'workflow_runs': []},
                          {'state': 'OPEN', 'headRefOid': 'sha'}, [feed()], [feed()]]
        checks.wait('https://github.com/zoyored/dogs/pull/86', 'sha')
        sleep.assert_called_once()

    def test_timeout_blocks(self):
        with self.assertRaisesRegex(RuntimeError, 'Timed out'):
            checks.wait('https://github.com/zoyored/dogs/pull/86', 'sha', timeout=0)


if __name__ == '__main__':
    unittest.main()
