@etl /workflow

READ-ONLY BLOCKER PROVENANCE CHECK ONLY.

Reuse the STTM parse and preview evidence already produced. Do not regenerate artifacts or repeat runtime validation.

Search only the selected workspace’s existing job, environment, onboarding, SQL, and shared configuration assets, plus approved packaged repository-convention rules, for explicit evidence resolving:

* source dataset location;
* target storage path;
* Delta and CSV write semantics and merge keys;
* job ID and onboarding metadata;
* compatible environment and deployment state;
* canonical failure-status literals for BR_0003 and BR_0007 through BR_0010.

Follow locally available YAML includes recursively. Stop at includes outside the selected workspace.

Do not:

* treat an unrelated job or environment as compatible by analogy;
* invent or select any missing value;
* generate files;
* perform runtime validation;
* use Git, shell, network, CI, or companion providers;
* modify the workspace.

For every item, return exactly one classification:

* EXPLICIT_WORKSPACE_EVIDENCE — cite the exact file and key;
* APPROVED_CONVENTION_EVIDENCE — cite the exact applicable rule;
* CONFLICTING_EVIDENCE;
* MISSING_USER_DECISION;
* EXTERNAL_RUNTIME_VALIDATION_ONLY.

Also determine:

1. Whether the ten blank error descriptions are warnings or blockers under the documented validation contract.
2. Whether the two active mappings referencing inactive target schemas are warnings or blockers.
3. Why the parser reports audit status pass while still reporting those semantic findings.
4. Whether the shared ADLS roots mean only dataset-relative paths are missing, rather than complete source/target locations.

Do not resolve user decisions automatically.

Finish with exactly:

LOCAL_STTM_BLOCKER_PROVENANCE_COMPLETE
