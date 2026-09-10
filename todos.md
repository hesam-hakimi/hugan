TASK_ID: ETL-0910-EXISTING-CONSUMER-UPGRADE-INDEPENDENT-REVIEW01
TYPE: Focused independent read-only acceptance review
ENVIRONMENT: Windows development agent; existing ETL evidence and the
retained dedicated test installation and temporary consumer.

LANGUAGE AND NO-VISION
Use English for ALL communication, progress updates, final responses,
code, comments, tests and documents. Do not append Persian summaries.
The vision service is unavailable. Do not capture screenshots, record
video, inspect images, or invoke vision/OCR services.
Use retained DOM/accessibility text, structured UI events, logs, file
contents, inventories and checksums. State any specific visual limitation.

OBJECTIVE
Close the pending acceptance decision for the completed existing-consumer
skill upgrade. Produce a clear verdict and identify the next concrete
step toward correct job/env writes.

START FROM EXISTING WORK
Resolve these records by their contents and identities, not folder recency:
- ETL-0910-INSTALLED-WORKFLOW-EXISTING-CONSUMER-UPGRADE-SMOKE01
- Its RECONCILE record
- ETL-0910-EXACT-VSIX-INSTALL-INITIALIZE-REVIEW01

Check whether this independent review already exists or is in progress.
Reuse a completed review; do not create a duplicate or concurrent review.
The completed Upgrade must not be repeated or artificially recreated
through a downgrade. Reconciliation alone is not independent acceptance.

FOCUSED REVIEW
1. Verify the original evidence inventory and the current target and
   installed identities using actual files. Distinguish extension version
   0.3.147 from managed asset version 1.1.5.

2. Independently verify the expected skill content against the installed
   catalog and the actual rendering/checksum rules. Correlate retained
   records showing that the expectation preceded approval and mutation.
   Do not rely only on report prose or file modification times.

3. Verify the recorded Cancel and approval sequences, pending inventories,
   exact Upgrade Managed Assets selection, and the resulting single-file
   change. Check that Overwrite and Repair were not selected.

4. Confirm delivery of repo.skill.validate-write from 1.1.4 to 1.1.5,
   including Target Root guidance. Verify preservation of the other
   20 assets and .gitignore, and the recorded post-Audit current status.
   Preserve the limitation that non-empty user content outside the
   managed section was not exercised.

5. Assess the existing findings independently, concentrating on their
   effect on this acceptance decision and release readiness:
   missing destination/change disclosure, the sibling Overwrite action,
   and the remaining recorded findings.
   Check launch flags, including --disable-workspace-trust, against the
   actual authorized scope. Do not infer normal trust-path qualification.

Do not repeat unrelated historical investigations. Preserve accepted
Base initialization results and keep historical FIX01 and PARITY01 test
results separate.

EXECUTION BOUNDARIES
Read-only inspection only. No Host launch, model request, ETL operation,
build, test execution, packaging, installation, source/Git change,
consumer mutation, deployment or release.
Reuse existing evidence and helpers. Do not create another JS/PowerShell
framework. Leave original evidence unchanged.

DELIVERY
Write only concise report.md and result.json in the review directory.
Include:
- Verdict and directly supporting evidence.
- Blocking findings, non-blocking findings and retained limitations.
- Acceptance status of this specific consumer skill upgrade.
- Original job/env write correctness: not established by this review.
- Post-upgrade model loading of the skill: not established by this review.
- Release acceptance: not granted.

If accepted, specify one actionable next task for qualifying actual
preview → approval → job/env write behavior in the correct temporary
consumer root, reusing the existing environment and permanent tests.
If blocked, specify the smallest correction needed.

Finish this acceptance decision without introducing another reconciliation
stage or expanding into unrelated cleanup.
