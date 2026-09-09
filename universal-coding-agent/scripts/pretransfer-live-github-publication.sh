#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

: "${UCA_GITHUB_TOKEN:?UCA_GITHUB_TOKEN must be set in the environment}"
: "${UCA_GITHUB_REPOSITORY:?UCA_GITHUB_REPOSITORY must be set in the environment}"
: "${UCA_GITHUB_ACCOUNT_IDENTITY:?UCA_GITHUB_ACCOUNT_IDENTITY must be set in the environment}"
: "${UCA_GITHUB_LIVE_REPOSITORY_URL:?UCA_GITHUB_LIVE_REPOSITORY_URL must be set}"
: "${UCA_GITHUB_LIVE_BASE_BRANCH:?UCA_GITHUB_LIVE_BASE_BRANCH must be set}"
: "${UCA_GITHUB_LIVE_BASE_SHA:?UCA_GITHUB_LIVE_BASE_SHA must be set}"
: "${UCA_GITHUB_LIVE_HEAD_BRANCH:?UCA_GITHUB_LIVE_HEAD_BRANCH must be set}"
: "${SSH_AUTH_SOCK:?SSH_AUTH_SOCK must identify the host-owned SSH agent}"

STATE_ROOT="${1:-$HOME/.uca-pretransfer-github-publication/$(date -u +%Y%m%dT%H%M%SZ)}"
mkdir -p "$STATE_ROOT"

python -m universal_coding_agent.testlab.github_publication_live \
  --state-root "$STATE_ROOT" \
  --source-root "$(git rev-parse --show-toplevel)" \
  --repository-url "$UCA_GITHUB_LIVE_REPOSITORY_URL" \
  --base-branch "$UCA_GITHUB_LIVE_BASE_BRANCH" \
  --base-sha "$UCA_GITHUB_LIVE_BASE_SHA" \
  --head-branch "$UCA_GITHUB_LIVE_HEAD_BRANCH"
