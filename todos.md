These owner decisions were made outside this execution chat. Record them verbatim. Do not ask, present, split, reinterpret, or seek confirmation for any further owner decision.

DECISION D2/D3 — RATIFY, principle only.

CREATE layout selection may select only an already-ratified profile from a versioned recognized-profile registry. Evidence must be restricted to the explicitly selected workspace root, scoped by (artifactFamily, evidenceScope), accompanied by an explicit discovery-completeness attestation, and validated jointly for cross-family include topology.

Evidence may select a ratified profile; it must never synthesize a path grammar, filename sanitizer, extension, alias table, environment identifier, fallback, naming rule, or registry entry.

Incomplete discovery, ambiguous or inconsistent evidence, no ratified matching profile, an unknown registry version, or a cross-family include-topology failure must produce one typed fail-closed outcome with a cause chain and no artifact path.

This is a Maintainer/Product policy ratification, not a claim that this registry exists today and not a Framework normative contract. It does not ratify registry ownership, registry content, versioning mechanism, initial profiles, any Job/Environment grammar, R1–R3, R11, R15, or implementation. Until those details are separately ratified, affected CREATE operations remain fail-closed.

DECISION D4 — RATIFY the breaking-change characterization only.

A policy that prohibits creation of new standalone .sql transformation artifacts would be an intentional breaking product narrowing because the current Extension creates standalone .sql artifacts. This ratification does not enact that prohibition, does not remove or modify current .sql behavior, and does not resolve R11.

Any future prohibition requires a separate explicit Maintainer/Product decision plus characterization coverage of the current .sql producers and compatibility impact. Framework-owned .sql evidence remains fixture/example-grade and must not be promoted into a product contract.

Attribute both decisions to the Maintainer/Product Owner, even though the respondent is recorded as “Both authorities.”

After recording these decisions:

1. Mark D1, D2/D3, and D4 as principle-ratified with their exact scope limitations.
2. Keep every R1–R20 detail decision unresolved unless it was explicitly decided above.
3. Do not begin another interactive question or owner interview.
4. Do not infer any answer from current code, prevalence, producer count, silence, or absence of a producer.
5. Output only:
    * the updated D1/D2-D3/D4 decision ledger;
    * the still-open Maintainer/Product decision IDs;
    * the still-open CD/Platform decision IDs;
    * the exact fail-closed lifecycle stages;
    * an immutability receipt.

Do not write an ADR or any file. Do not modify code, Git, worktrees, review cards, Keep/Undo state, baselines, VSIX, consumer workspaces, or external systems. Do not authorize or start Slice 2.
