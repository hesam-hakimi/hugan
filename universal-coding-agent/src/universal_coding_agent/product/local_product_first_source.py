"""Durable first-source quotes without changing any v1 authority comparison."""

from __future__ import annotations

import base64
from dataclasses import asdict
from pathlib import Path

from universal_coding_agent.product.local_product_binding import check
from universal_coding_agent.product.local_product_command_store import QUOTES
from universal_coding_agent.product.program_continuation_execution_store import canonical, sha
from universal_coding_agent.product.program_source_capture_budget import CaptureBudget
from universal_coding_agent.product.program_source_evidence import strict_json


class LocalFirstSource:
    def __init__(self, host):
        self.host, self.source = host, host.source
        self.core = self.candidate = self.quote = self.inventories = None
        self.inventory_values = None
        self.evidence_links = None

    def capture(self, part):
        payload, source = part.payload, self.source
        candidate = source.prepare(
            part.key[0],
            payload["task_id"],
            owner_token=part.owner_token,
            expected_source_sha256=payload["before_sha256"],
            expected_generation=0,
        )
        candidate_raw = source._get(candidate["candidate_sha256"])
        check(
            strict_json(candidate_raw)
            == {k: v for k, v in candidate.items() if k != "candidate_sha256"},
            "recorded_evidence_invalid",
        )
        before = source.source.load_snapshot(
            source._get(payload["before_sha256"]), expected_sha256=payload["before_sha256"]
        )
        binding, checkpoint, evidence = source._capture(
            before, payload["task_id"], part.owner_token
        )
        check(
            binding == candidate["binding"]
            and sha(checkpoint) == candidate["checkpoint_sha256"]
            and sha(evidence.payload) == candidate["evidence_sha256"],
            "proposal_changed",
        )
        execution = binding["execution"]
        budget = part.capture_budget
        result = budget.read_artifact(
            source.programs.artifacts.root,
            Path(execution["result_ref"].removeprefix("artifact://")),
            8_000_000,
        )
        report = budget.read_artifact(
            source.programs.artifacts.root,
            Path(execution["phase_report_ref"].removeprefix("artifact://")),
            2_000_000,
        )
        state = strict_json(result)
        state = state.get("state", state)
        execution_root = Path(state["sandbox_path"])
        check(
            execution_root == self.host.safe_root / "sandboxes" / payload["task_id"] / "repo",
            "binding_changed",
        )
        roots = (source.attestor.root, execution_root)
        inventories, identities, inventory_values = [], [], []
        for root in roots:
            inventory_values.append(budget.inventory(root))
            entries, pins = [], []
            for path, observation in sorted(budget.files.items()):
                relative = Path(path).relative_to(root) if Path(path).is_relative_to(root) else None
                if relative is not None:
                    info = observation["file"]
                    entries.append(
                        {
                            "path": str(relative),
                            "type": "file",
                            "mode": info[2],
                            "sha256": observation["sha256"],
                        }
                    )
                    pins.append(
                        {"path": str(relative), "chain": observation["chain"], "file": info}
                    )
            for path, observation in sorted(inventory_values[-1].items()):
                if type(observation) is list:
                    entries.append(
                        {"path": path, "type": "directory", "mode": observation[2], "sha256": None}
                    )
                    pins.append({"path": path, "directory": observation})
            entries.sort(key=lambda item: item["path"])
            pins.sort(key=lambda item: item["path"])
            inventories.append(entries)
            identities.append(pins)
        self.inventories = roots
        self.inventory_values = inventory_values
        with part.store.transaction(participant=part):
            # Copy the producer-verified evidence leaves into an explicit small
            # journal manifest. Recorded reads hash these bytes without decoding
            # the embedded source/checkpoint evidence again.
            leaves = strict_json(evidence.payload)["safe"]["artifacts"]
            check(type(leaves) is list and 0 < len(leaves) <= 32, "recorded_evidence_invalid")
            artifacts = []
            for leaf in leaves:
                raw = base64.b64decode(leaf["content_base64"], validate=True)
                check(sha(raw) == leaf["sha256"], "recorded_evidence_invalid")
                artifacts.append(part.store.put(raw))
            self.evidence_links = {
                "schema": "uca-local-first-evidence-1",
                "program_id": part.key[0],
                "task_id": payload["task_id"],
                "evidence_sha256": candidate["evidence_sha256"],
                "artifacts": artifacts,
            }
            semantic = self.host.semantic(part.key[0], payload["task_id"])
            first_receipt = self.host.first_result(part.key[0], terminal=True)
            check(
                first_receipt["task_id"] == payload["task_id"]
                and first_receipt["result_sha256"] == sha(result),
                "recorded_evidence_invalid",
            )
            first_sha = part.store.put(first_receipt)
            core = {
                "schema": "uca-local-first-source-core-1",
                "project_id": payload["project_id"],
                "program_id": part.key[0],
                "task_id": payload["task_id"],
                "thread_id": execution["thread_id"],
                "phase_id": execution["phase_id"],
                "host_sha256": source.host_sha256,
                "binding_sha256": self.host.binding_sha256,
                "generation": 0,
                **{
                    key: candidate[key]
                    for key in (
                        "before_sha256",
                        "after_sha256",
                        "transition_sha256",
                        "evidence_sha256",
                        "checkpoint_sha256",
                    )
                },
                "initialization_receipt_sha256": semantic["source"]["initial_receipt_sha256"],
                "result_sha256": part.store.put(result),
                "phase_report_sha256": part.store.put(report),
                **{
                    name + "_row_sha256": sha(canonical(binding[name]))
                    for name in ("program", "phase", "execution", "program_control", "task_control")
                },
                "plan_sha256": payload["plan_sha256"],
                "requirement_sha256": payload["requirement_sha256"],
                "recovery_history_sha256": semantic["recovery_history_sha256"],
                "source_policy_sha256": sha(canonical(asdict(source.source.policy))),
                "git_policy_sha256": source.attestor.policy_sha256,
                "test_policy_sha256": sha(canonical(self.host.policy.model_dump(mode="json"))),
                "origin_inventory_sha256": part.store.put(inventories[0]),
                "execution_inventory_sha256": part.store.put(inventories[1]),
                "filesystem_identity_sha256": part.store.put(identities),
                "first_result_receipt_sha256": first_sha,
            }
            part.store.put(core)
            self.host.quiet(part.key[0])
        return candidate, core, state

    def run(self, part):
        part.capture_budget = CaptureBudget()
        with part.capture_budget.activate():
            candidate, core, state = self.capture(part)
            # A second independently assembled core must match even at preview.
            repeated_candidate, repeated_core, _ = self.capture(part)
            check(repeated_candidate == candidate and repeated_core == core, "proposal_changed")
            self.candidate, self.core = candidate, core
            with part.store.transaction(participant=part):
                part.link("first_evidence", self.evidence_links)
            if part.payload["action"] == "preview_first_source":
                with part.store.transaction(participant=part):
                    view_sha = self.host.evidence_view(
                        state,
                        "source",
                        core_sha256=sha(canonical(core)),
                        source_evidence_sha256=candidate["evidence_sha256"],
                    )
                    quote = {
                        "schema": "uca-local-first-source-quote-1",
                        "project_id": part.payload["project_id"],
                        "program_id": part.key[0],
                        "task_id": part.payload["task_id"],
                        "quote_revision": 1,
                        "core_sha256": sha(canonical(core)),
                        "preview_candidate_sha256": candidate["candidate_sha256"],
                        "preview_request_sha256": sha(canonical(part.payload)),
                        "evidence_view_sha256": view_sha,
                    }
                    quote_sha = part.store.put(quote)
                    part.store.connection.execute(
                        f"INSERT INTO {QUOTES} VALUES (?,?,?,?)",
                        (part.key[0], part.payload["task_id"], quote_sha, part.key[1]),
                    )
                    part.link("first_source_quote", quote)
                    self.quote = quote
                    part.final_source = self
                    part.finish(
                        "source_preview_recorded",
                        {
                            "task_id": part.payload["task_id"],
                            "quote_sha256": quote_sha,
                            "quote_revision": 1,
                            "core_sha256": quote["core_sha256"],
                            **{
                                key: core[key]
                                for key in (
                                    "transition_sha256",
                                    "before_sha256",
                                    "after_sha256",
                                    "generation",
                                )
                            },
                            "predecessor_receipt_sha256": core["initialization_receipt_sha256"],
                            "evidence_view_sha256": view_sha,
                        },
                    )
            else:
                reviewed, reviewed_core = self.host.reviewed_first_quote(part.payload)
                check(core == reviewed_core, "proposal_changed")
                old = strict_json(self.source._get(reviewed["preview_candidate_sha256"]))
                check(
                    candidate["candidate_sha256"] != reviewed["preview_candidate_sha256"]
                    and candidate["binding"]["owner_binding_sha256"]
                    != old["binding"]["owner_binding_sha256"],
                    "recovery_required",
                )
                self.quote, part.final_source = reviewed, self
                if part.payload["approved"]:
                    self.source.accept(
                        candidate["candidate_sha256"],
                        approved_transition_sha256=part.payload["transition_sha256"],
                        approval_id=part.payload["approval_id"],
                        owner_token=part.owner_token,
                        participation=part,
                    )
                else:
                    with part.store.transaction(participant=part):
                        self.accepted(part, None)
        return part.response

    def recheck(self, part):
        self.host.quiet(part.key[0])
        check(
            self.host.semantic(part.key[0], part.payload["task_id"])["recovery_history_sha256"]
            == self.core["recovery_history_sha256"],
            "proposal_changed",
        )
        for root, inventory in zip(self.inventories, self.inventory_values, strict=True):
            # Inventory checks additions/removals as well as the captured files.
            check(part.capture_budget.inventory(root) == inventory, "proposal_changed")
        part.capture_budget.recheck_files()

    def accepted(self, part, receipt):
        check(part.payload["action"] == "decide_first_source", "recovery_required")
        self.recheck(part)
        source_sha = receipt["source_sha256"] if receipt else self.core["before_sha256"]
        part.link(
            "first_source_decision",
            {
                "schema": "uca-local-first-source-decision-1",
                "program_id": part.key[0],
                "task_id": part.payload["task_id"],
                "quote_sha256": part.payload["quote_sha256"],
                "preview_candidate_sha256": self.quote["preview_candidate_sha256"],
                "decision_candidate_sha256": self.candidate["candidate_sha256"],
                "core_sha256": sha(canonical(self.core)),
                "approval_id": part.payload["approval_id"],
                "approved": part.payload["approved"],
                "source_receipt_sha256": part.store.put(receipt) if receipt else None,
            },
        )
        return part.finish(
            "source_accepted" if receipt else "rejected",
            {
                "task_id": part.payload["task_id"],
                "quote_sha256": part.payload["quote_sha256"],
                "approved": part.payload["approved"],
                "source_receipt_sha256": part.store.put(receipt) if receipt else None,
                "generation": 1 if receipt else 0,
                "source_sha256": source_sha,
            },
            lower=receipt,
        )
