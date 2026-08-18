# Safe Mode Foundation

Safe Mode is the first write-capable milestone of the Universal Coding Agent. It is intentionally limited to a human-approved, text-only patch inside an isolated Git sandbox.

It does **not** stage, commit, push, create or edit a pull request, merge, deploy, or modify the source checkout.

## Control flow

```text
Safe task + approved manifest + trusted test policy
    → immutable sandbox at approved base SHA
    → repository index
    → human scope approval interrupt
    → bounded implementer JSON
    → deterministic patch inspection
    → git apply --check
    → rollback checkpoint
    → patch application in sandbox
    → fixed-profile focused tests
    → independent reviewer
    → retain passing patch or perform patch-scoped rollback
    → final evidence report
```

## Mandatory safety contracts

### Frozen repository identity

The approved change manifest contains an immutable `base_sha`. Safe Mode resolves the requested Git ref and blocks before implementation when the sandbox SHA does not match.

### Approved path manifest

Every allowed file is listed exactly once with one operation:

- `modify` for an existing regular file;
- `create` for an absent file.

Safe Mode currently rejects deletes, renames, copies, symlink changes, binary patches, duplicate diff sections, path traversal, absolute paths, and changes under denied prefixes.

### Human scope approval

The graph always interrupts before invoking the implementer. Approval is bound to:

- base SHA;
- prior plan hash;
- canonical scope hash;
- exact allowed paths and operations;
- denied prefixes;
- fixed test profile IDs;
- acceptance criteria.

Resume requires the same LangGraph thread ID and state directory.

### Patch-only implementation

The model returns a typed `PatchProposal`. It cannot directly write files or run commands. The control plane validates the unified diff and applies it with fixed `git` argv and `shell=False`.

### Trusted focused-test policy

The model cannot invent shell commands. A trusted operator-owned policy maps profile IDs to exact argv arrays, working directories, timeouts, and bounded output limits. The approved manifest selects only profile IDs that exist in that policy.

### Independent review

The reviewer receives the original task, approved scope, actual diff, focused-test evidence, exact changed paths, and post-change file state. A patch is retained only when:

- scope was approved;
- patch validation passed;
- all focused tests passed;
- no out-of-scope workspace change occurred;
- reviewer verdict is exactly `PASS`.

`PASS_WITH_CONDITIONS`, `BLOCKED`, `FAIL`, test failure, or any safety error triggers rollback.

### Patch-scoped rollback

Before application, Safe Mode writes a rollback checkpoint containing base SHA, plan hash, scope hash, patch hash, and exact changed paths. Rollback reverses only the approved patch; it never performs `git reset --hard` or a repository-wide clean.

## Scope manifest example

```json
{
  "manifest_version": "1",
  "base_sha": "0123456789abcdef0123456789abcdef01234567",
  "plan_hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "allowed_changes": [
    {
      "path": "src/example.py",
      "operation": "modify",
      "purpose": "Implement the approved contract."
    },
    {
      "path": "tests/test_example.py",
      "operation": "create",
      "purpose": "Add deterministic contract coverage."
    }
  ],
  "denied_prefixes": [
    ".git",
    ".ssh",
    ".env",
    ".venv",
    "venv",
    "node_modules",
    "secrets",
    "credentials"
  ],
  "test_profiles": ["focused-tests"],
  "acceptance_criteria": [
    "The approved contract is implemented.",
    "Focused tests pass.",
    "No path outside the manifest changes."
  ],
  "max_patch_bytes": 200000,
  "max_changed_files": 16
}
```

## Trusted policy example

```json
{
  "policy_version": "1",
  "profiles": [
    {
      "profile_id": "focused-tests",
      "argv": ["python", "-m", "pytest", "-q", "tests/test_example.py", "-p", "no:cacheprovider"],
      "cwd": ".",
      "timeout_seconds": 300,
      "output_limit": 20000
    }
  ]
}
```

## CLI

Start a Safe Mode task:

```bash
uca \
  --state-root /durable/state \
  --provider-factory package.adapter:create_provider \
  safe \
  --repository https://example.test/owner/repository.git \
  --ref feature/approved-base \
  --task-file task.md \
  --scope-file approved-scope.json \
  --policy-file trusted-policy.json \
  --task-id safe-task-001 \
  --thread-id safe-task-001
```

The first invocation pauses at `scope_approval`.

Inspect state:

```bash
uca --state-root /durable/state safe-status --thread-id safe-task-001
```

Approve and continue:

```bash
uca \
  --state-root /durable/state \
  --provider-factory package.adapter:create_provider \
  safe-resume \
  --thread-id safe-task-001 \
  --decision approve
```

Rejecting the scope produces a blocked final report without invoking the implementer.

## One-command local qualification

```bash
bash scripts/safe-smoke.sh
```

The smoke qualification proves:

- separate start and resume invocations;
- mandatory scope approval;
- immutable-base verification;
- exact path enforcement;
- patch application only in the sandbox;
- fixed-profile focused testing;
- independent review;
- source repository preservation;
- no new Git commit;
- final retained patch on `PASS`;
- patch-scoped rollback on conditional review in unit coverage.

## Deliberate exclusions

Safe Mode Foundation does not provide:

- arbitrary shell access;
- package installation selected by the model;
- file deletion, rename, copy, binary, or symlink modification;
- staging or commits;
- push or pull-request operations;
- merge or deployment;
- automatic scope expansion;
- automatic approval of reviewer conditions;
- direct mutation of the source checkout.
