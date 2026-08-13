@etl /workflow

READ-ONLY TARGET WORKSPACE IDENTITY CHECK ONLY.

Do not generate, modify, delete, approve, install, stage, commit, push, deploy, or execute anything.

Current evidence:

* Open workspace appears to be: etl-acz0001-aczdg
* STTM file: CD-Renewal_DataMapping_V3.0 1.xlsx
* Logical target: cz_acz0004_retail.cd_renewal
* Sources include: ccaudittrx, ccaudittrxreference, and cd_renewal

Do not assume that the workspace is correct or incorrect based only on its folder name.

Determine whether the currently selected workspace is the intended Consumer ETL repository for creating the CD Renewal job.

Use only explicit repository evidence, including:

* README and repository documentation
* existing repository structure
* job configuration conventions
* environment configuration conventions
* onboarding records
* source-system identifiers
* target database and table identifiers
* shared configuration references
* existing CD Renewal references
* approved repository naming or ownership evidence

Report:

1. Current selected workspace root.
2. Evidence supporting that it is the correct target.
3. Evidence suggesting that it is the wrong target.
4. Whether CD Renewal is expected to be:
    * a new job in this repository,
    * an existing job being modified,
    * or a job belonging to another repository.
5. The exact repository or workspace name, if explicit evidence identifies one.
6. Any missing evidence that requires user confirmation.
7. Confirmation that zero files were changed.

Do not perform the full STTM preview again.

Finish with exactly one:

TARGET_WORKSPACE_CONFIRMED_CORRECT

TARGET_WORKSPACE_CONFIRMED_WRONG_<EXPECTED_WORKSPACE>

or

TARGET_WORKSPACE_IDENTITY_REQUIRES_USER_CONFIRMATION
