"""Wait for the real PR checks, including their initial registration delay."""
import argparse
import json
import subprocess
import time

FEED_CHECK = 'Validate event data and generated feeds'


def check_state(checks, required):
    """Return pending/pass/fail. Missing or skipped feed checks never pass."""
    feed = [c for c in checks if c['name'] == FEED_CHECK]
    watched = feed + required
    if any(c['bucket'] in ('fail', 'cancel', 'skipping') for c in watched):
        return 'fail'
    if not feed or any(c['state'] != 'SUCCESS' for c in watched):
        return 'pending'
    return 'pass'


def gh_json(*args, missing_checks=False):
    result = subprocess.run(['gh', *args], text=True, capture_output=True)
    message = (result.stderr + result.stdout).lower()
    if missing_checks and any(text in message for text in ('no checks reported', 'no required checks reported')):
        return []
    # gh pr checks uses exit 1 for failed checks and 8 for pending checks.
    allowed = (0, 1, 8) if args[0:2] == ('pr', 'checks') else (0,)
    if result.returncode not in allowed or not result.stdout.strip():
        raise RuntimeError(result.stderr.strip() or 'GitHub returned no check data')
    return json.loads(result.stdout)


def wait(pr, sha, timeout=600, interval=10):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        info = gh_json('pr', 'view', pr, '--json', 'headRefOid,state')
        if info['state'] != 'OPEN' or info['headRefOid'] != sha:
            raise RuntimeError('PR closed or its head changed; refusing to merge another revision')
        fields = 'name,state,bucket'
        checks = gh_json('pr', 'checks', pr, '--json', fields, missing_checks=True)
        required = gh_json('pr', 'checks', pr, '--required', '--json', fields, missing_checks=True)
        state = check_state(checks, required)
        if state == 'pass':
            print('Feed validation and all reported required checks succeeded.')
            return
        if state == 'fail':
            raise RuntimeError('Feed validation or a required check failed, was cancelled or skipped')
        # Approval-gated runs have no jobs or check runs, so inspect runs too.
        parts = pr.rstrip('/').split('/')
        repository = '/'.join(parts[-4:-2])
        runs = gh_json('api', f'repos/{repository}/actions/runs?head_sha={sha}&event=pull_request&per_page=100')
        if any(r.get('conclusion') == 'action_required' for r in runs['workflow_runs']):
            raise RuntimeError('PR workflow requires approval. Check that the PR was created with the configured GitHub App token.')
        print('Waiting for PR checks to register or finish...', flush=True)
        time.sleep(min(interval, max(0, deadline - time.monotonic())))
    raise RuntimeError(f'Timed out after {timeout}s; PR remains open and unmerged')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pr', help='GitHub PR URL')
    parser.add_argument('sha', help='Expected PR head SHA')
    parser.add_argument('--timeout', type=int, default=600)
    args = parser.parse_args()
    try:
        wait(args.pr, args.sha, args.timeout)
    except (RuntimeError, ValueError, KeyError) as error:
        print(f'::error::{error}')
        raise SystemExit(1)
