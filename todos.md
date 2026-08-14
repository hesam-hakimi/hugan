Continue the current S-A task from its recorded BLOCKED state. This message grants only the narrow tooling permission below; all original S-A scope and preservation constraints remain in force.

I authorize exactly one lockfile-driven dependency restore in the confirmed etl_framework_extension repository root:

npm ci --ignore-scripts --no-audit --no-fund

Conditions:

1. Before running it, re-capture Git status and SHA-256 hashes for every pre-existing pending/Keep file, plus package.json and the applicable lockfile.
2. Do not edit package.json, package-lock.json, npm-shrinkwrap.json, testPatterns.ts, or any other pre-existing pending/Keep file.
3. Do not use dependencies or typings from sibling repositories.
4. Do not run npm install, npm update, npm audit fix, lifecycle scripts, package/build/VSIX/install commands, or any Git mutation.
5. If npm ci reports a lockfile mismatch, requires lifecycle scripts, or would modify a protected file, stop immediately and report the exact blocker. Do not repair, regenerate, revert, restore, discard, or clean anything.
6. Treat node_modules as disposable, ignored tooling output only.

After the dependency restore succeeds:

* Inspect the installed @types/vscode surface and ground every WorkspaceConfiguration.inspect() field used by S-A in the actual installed API.
* Before editing production source, prove that a clean, already auto-discovered test location exists without modifying the dirty testPatterns.ts.
* Prefer the existing integration-suite location only if its current runner automatically discovers the new test without registry or pattern edits.
* If no clean test route exists, stop and report that single remaining blocker before editing production source.
* Otherwise implement only the originally authorized S-A read-only settings inventory and provenance reader.
* Do not implement setting writes, context freezing, bootstrap/result envelopes, agent propagation, chat guidance, configuration change observation, task-local overrides, or any later slice.
* Run only the narrow targeted type-check and the smallest relevant tests.
* Keep every user-facing product string in English.
* At completion, report:
    1. files created or edited;
    2. exact commands and results;
    3. the resulting read-only API contract;
    4. any remaining blockers;
    5. end-state Git status and hash proof showing that every pre-existing pending/Keep file and the package/lockfile remain byte-identical.

Do not click Keep, Undo, Revert, Discard, Restore, or Clean. Do not stage, commit, push, or modify another worktree.
