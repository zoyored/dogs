# Daily validation GitHub App setup

The daily validator creates and merges validation-state PRs with a dedicated GitHub App. GitHub requires approval for PR workflows triggered by the built-in `GITHUB_TOKEN`; a dedicated App token lets the normal PR checks run automatically. The workflow still waits for the feed check and every reported required check to succeed before merging the exact checked commit.

## One-time account setup

1. Open https://github.com/settings/apps/new and register a private App, for example `dogs-validation-zoyored` (choose another name if unavailable).
2. Set Homepage URL to https://github.com/zoyored/dogs. Disable **Webhook → Active**; no webhook or callback URL is needed. Set installation availability to **Only on this account**.
3. Grant only these **Repository permissions**:
   - Contents: Read and write
   - Pull requests: Read and write
   - Actions: Read-only
   - Checks: Read-only
   - Commit statuses: Read-only
   - Metadata: Read-only (mandatory)
4. Create the App. Copy its **Client ID**. Generate a private key and download the PEM file. Do not paste the key into a PR, commit, chat or workflow log.
5. Use **Install App** and install it on `zoyored`, choosing **Only select repositories → dogs**.
6. At https://github.com/zoyored/dogs/settings/variables/actions create repository variable `DOGS_AUTOMATION_APP_CLIENT_ID` with the Client ID.
7. At https://github.com/zoyored/dogs/settings/secrets/actions create repository secret `DOGS_AUTOMATION_APP_PRIVATE_KEY` with the complete PEM contents, including BEGIN/END lines.

No administration, workflow-writing or Actions-writing permission is needed. The runtime token is limited to `dogs` and revoked at job cleanup. The built-in token retains only Contents read access. Branch protection remains enabled.

## Activate and verify

After setup, merge the workflow fix PR and manually run **Daily event validation** with `full=false`. Confirm:

- the App token step succeeds;
- the new validation-state PR is authored by the dedicated App;
- **Validate event data and generated feeds** starts without manual approval;
- the daily workflow waits for successful checks and merges that exact PR head;
- the proposal workflow starts after the validation-state merge (the App token allows push-triggered workflows).

The daily workflow runs a local feed-consistency check before pushing and uses a 10-minute bounded wait for PR checks. A missing check never counts as success. A failed, cancelled, skipped or approval-required check prevents merging. Each retry uses a separate review branch. Superseded validation PRs are closed only after a successful merge.

For PR #86, which was created using the old token, approve its workflow once through GitHub and merge only after successful checks, or let a successful new daily run supersede it. Do not merge it without validation.

Only the validation-state PR is auto-merged. Proposal and final calendar-change review gates remain as documented in `automation.md`.
