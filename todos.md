Continue from:

LOCAL_VSIX_BUILD_BLOCKED_UNIT_TESTS_FAILED_6_OF_1802

The user explicitly authorizes a LOCAL-ONLY release policy. This supersedes the earlier rule that every unit-test failure is automatically a packaging hard stop.

Do not blanket-waive product, runtime, or package-integrity failures.

SCOPE

* Build source:
    b2e44c3a1a051aa7fa6008931d225bc06d22e847
* Reuse only the previously verified isolated build root:
    etlfw_vsix_build_20260812_182051_2fb60be8
* Main repository, Draft PR #7, CI, credentials, and unstaged files must remain untouched.
* Do not create Commit 10.
* Do not click Keep or Undo.

CLASSIFY THE SIX FAILURES

For each failure, report:

* exact test file and test name;
* exact affected file paths;
* whether the affected files are:
    * extension runtime;
    * packaged product/customization assets;
    * maintainer-only repository assets;
    * evaluation baseline only;
* whether they appear in the actual VSIX candidate;
* whether runtime code reads or references them.

AUTHORIZED CONDITIONAL WAIVERS

1. The two stale Phase H/EvalGating baseline failures may be waived only after confirming they test baseline freshness and not runtime behavior.
2. The missing maintainer delivery prompt may be waived only if it is under .github/**, excluded from the VSIX, and never referenced by packaged runtime code.
3. The AGENT.md versus AGENTS.md convention failure may be waived only if those files are maintainer guidance, excluded from the VSIX, and not required by generated consumer assets.
4. The missing frontmatter name failure must not be automatically waived:
    * If the file is under resources/copilot/**, copied to consumer workspaces, registered by the customization catalog, or otherwise consumed by the extension, classify it as a local-product blocker.
    * If it is maintainer-only, excluded from the package, and not consumed at runtime, document and waive it.

PACKAGE-CONTRACT INVESTIGATION

Do not automatically waive the .vscodeignore failure.

1. Run the repository-declared vscode:prepublish / package:prepare command inside the isolated build root.
2. Use only the repository-local VSCE dependency to obtain the exact package candidate list.
3. Determine the complete runtime dependency closure starting from:
    * out/extension.js
    * out/sttm-runtime.js
    * required out/vendor/**
4. Account for static imports, dynamic imports, runtime file reads, and packaged resources/copilot/**.
5. Verify that the current narrow .vscodeignore allowlist includes every required runtime file.

If any required runtime or product asset is missing, stop without modifying files and report every exact missing path:

LOCAL_VSIX_BUILD_BLOCKED_PACKAGE_CONTENT_INCOMPLETE

If the candidate is complete, classify the .vscodeignore assertion as a stale broad-pattern test and record a local-release waiver.

LOCAL PACKAGE GATE

Continue only if:

* compile passed;
* lint passed;
* all six failures are either safely waived with evidence or proven irrelevant to the local product;
* the VSIX candidate contains the complete runtime and product asset set.

Then:

1. Build exactly one VSIX without publishing or installing it.
2. Inspect the actual VSIX archive.
3. Require:
    * extension/package.json;
    * compiled entrypoint and complete runtime closure;
    * required resources/copilot/**;
    * no .env, credentials, Git metadata, test files, evaluation output, logs, diagnostic evidence, or temporary build files.
4. Compute SHA-256.
5. Copy it without overwriting anything into:
    C:\repos\etl-extension\etl_fw2\local-release-artifacts
6. Provide the exact non-force manual VS Code installation command.
7. Clearly list all local-release waivers and state that CI was not used as a release gate.

Do not modify any source file merely to make a test green. Do not modify the main repository, stage, commit, push, edit the PR, or touch CI.

Finish with exactly one:

LOCAL_VSIX_PACKAGE_READY_WITH_DOCUMENTED_WAIVERS

or

LOCAL_VSIX_BUILD_BLOCKED_<EXACT_REASON>
