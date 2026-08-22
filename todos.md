AUTHORIZED.

Proceed with LOCAL_HOTFIX_HF1_V2_RELEASE_GATE_REPAIR_7 using exactly the bounded 12-file scope you identified.

Authorization includes:

- 1 new shared policy-free physical containment primitive
- the 9 listed production files
- the 2 listed test files
- compile
- lint
- focused Repair-7 tests
- Repair-5 / Repair-6 regression tests
- WriteAuthorization tests
- full unit suite
- package verification using already-installed dependencies

Do not expand the file scope.

Do not modify:
- consumer repositories
- etl-framework-adb
- resources/prompts/**
- .github/**
- AGENT.md / AGENTS.md
- package-lock.json
- historical Phase-H baselines
- Oracle/framework contracts

Do not install or download dependencies.
Do not commit.
Do not push.
Do not Keep.
Do not install the VSIX.

If any additional production or test file becomes necessary, STOP before modifying it and report the exact reason for a scope amendment.

Proceed with implementation and validation.

APPLY_LOCAL_HOTFIX_HF1_V2_RELEASE_GATE_REPAIR_7
