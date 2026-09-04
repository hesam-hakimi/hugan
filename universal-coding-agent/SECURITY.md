# Security Model

## Trust boundaries

Repository content, branches, instructions, tests, and build files are untrusted input. They cannot override agent safety policy.

The configured state root and explicitly loaded adapter factory are trusted, host-owned control
plane storage and code. Artifact hashes and immutable SQLite records detect drift and inconsistent
corruption across bounded evidence; they are not a MAC or signature against an attacker who can
rewrite the state database and every corresponding artifact coherently. Such write access is a
control-plane compromise and is outside the repository-content threat boundary.

The model service and source-control service use separate credentials and separate adapters.

```text
Model credential      -> control plane only
Git credential        -> control plane only
Repository sandbox    -> receives neither credential
```

## Observe and Safe Mode guarantees

- Observe graph nodes perform no source writes;
- Safe Mode writes only approved structured edits inside an isolated sandbox and verifies the
  canonical Git patch, fixed tests, and independent review;
- exact-patch approval performs no source-control action by itself;
- post-approval commit, feature-ref creation, or Draft-PR creation requires a separate explicit
  command and a trusted, default-disabled adapter;
- no base-branch update, non-fast-forward history rewrite, merge, or deployment authority;
- no arbitrary model-supplied shell commands;
- Git commands use `shell=False` and explicit arguments;
- base ref is resolved to an immutable commit SHA;
- repository-content reads remain inside the sandbox root; remote publication metadata is read only
  through the bounded source-control adapter;
- denied files are excluded before indexing and context compilation;
- large/raw model responses and private reasoning are not persisted;
- safe structured diagnostics are persisted instead;
- artifacts are written atomically beneath the configured state root.

## Denied paths

The default deny policy includes:

- `.git/**` content reads;
- `.env` and `.env.*` except clearly identified example templates;
- private keys and certificates;
- credential/token files;
- shell history;
- cloud credential caches;
- common Git credential files.

Git metadata required for identity checks is accessed only through fixed Git commands.

## Repository URLs

The sandbox manager rejects repository URLs containing embedded usernames/passwords, query strings,
or fragments. Credentials must be supplied through host-controlled configuration such as an SSH
agent, GitHub App integration, or source-control provider—not embedded into the clone URL or stored
in publication evidence. The built-in publication adapter disables interactive prompts and Git
credential helpers, isolates global/system configuration, and rejects unsafe sandbox-local Git
configuration and symlinked object/ref/reflog storage before publication. Local Git operations use
a private Git-directory proxy fixed to the validated sandbox Git directory, while remote reads and
pushes use a neutral temporary Git client that does not load sandbox-local configuration.

The optional GitHub Draft-PR integration is disabled until its trusted factory and host-owned
environment are explicitly configured. It pins one GitHub host, repository, and stable non-secret
account identity; keeps the bearer token inside the control-plane API transport; permits only
bounded ref reads, same-head/base PR lookup, and Draft-PR creation; rejects redirects; and emits
typed errors
without response bodies, URLs containing credentials, or secret text. Hosted Git pushes continue to
use the fixed Git adapter and ambient host SSH agent rather than embedding the API token in Git
configuration or command arguments.

The hosted GitHub qualification gate additionally requires a clean source checkout at the exact
approved Base SHA, an absent head in the isolated `uca/github-live-qualification-...` namespace,
and a state directory outside the checkout. It snapshots all remote heads and tags before and after
publication, accepts only the addition of that exact head, proves the base and tags unchanged,
reconciles the exact Draft PR through a fresh adapter, reloads the immutable receipt without an
adapter call, and scans every generated state file for the bearer token. The qualification branch
and Draft PR are retained as evidence; the gate has no merge, deployment, base-update, history-
rewrite, tag, or ref-deletion authority.

## Resume

Human interrupts are checkpointed. Safe Mode approval and publication fail closed if the repository,
base SHA, sandbox, approved paths, diff hash, plan hash, or sealed test/review evidence has drifted.

## Reporting vulnerabilities

Do not include real secrets, proprietary repository content, or customer data in a public issue. Provide a minimal reproduction with sanitized fixtures.
