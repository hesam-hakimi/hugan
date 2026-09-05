# Security Model

## Trust boundaries

Repository content, branches, instructions, tests, and build files are untrusted input. They cannot override agent safety policy.

The model service and source-control service use separate credentials and separate adapters.

```text
Model credential      -> control plane only
Git credential        -> control plane only
Repository sandbox    -> receives neither credential
```

## Observe milestone guarantees

- no source writes by graph nodes;
- no staging, commit, push, PR, merge, or deployment;
- no arbitrary model-supplied shell commands;
- Git commands use `shell=False` and explicit arguments;
- base ref is resolved to an immutable commit SHA;
- all repository reads remain inside the sandbox root;
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

The sandbox manager rejects repository URLs containing embedded usernames/passwords, query strings, or fragments. Credentials must be supplied by a Git credential helper, SSH agent, GitHub App integration, or future source-control provider—not embedded into the clone URL.

## Resume

Human interrupts are checkpointed. Future write-mode resume must fail closed if the repository, base SHA, sandbox, approved paths, diff hash, plan hash, or task policy has drifted.

## Reporting vulnerabilities

Do not include real secrets, proprietary repository content, or customer data in a public issue. Provide a minimal reproduction with sanitized fixtures.
