"""Actual first-driver lifetimes and unqualified continuation outcomes over HTTP."""

import json

import pytest
from test_local_product_api import (
    PREFIX,
    action_fields,
    arm,
    calls,
    fixture,
    free_port,
    journey,
    post,
    request_payload,
    server,
    sql,
)


@pytest.mark.parametrize("kind", ["operation", "process", "cancellable", "pausable", "paused"])
def test_h03_actual_retained_registration_sets_block_the_returned_first_seal(tmp_path, kind):
    port = free_port()
    config = fixture(tmp_path, port)
    with server(tmp_path, port) as client:
        saved = journey(client, config, until="initialize-42")
        payload = request_payload(
            client,
            "start_first_phase",
            "retained-first",
            **action_fields("start_first_phase", saved, config),
        )
        arm(tmp_path, "start_first_phase", "first_outer_returned", mode="retain_" + kind)
        result = post(client, payload)
        assert result.status_code == 409, result.text
        actual = json.loads((tmp_path / "retained-registrations.json").read_text())
        expected = (
            "_paused_pausables"
            if kind == "paused"
            else {
                "operation": "_operations",
                "process": "_processes",
                "cancellable": "_cancellables",
                "pausable": "_pausables",
            }[kind]
        )
        assert actual[expected] == 1
        assert sql(tmp_path, "SELECT status FROM program_executions") == [
            ("awaiting_scope_approval",)
        ]
        before = calls(tmp_path)
        assert post(client, payload).status_code == 202
        assert calls(tmp_path) == before
        assert sql(tmp_path, "SELECT generation FROM program_source_heads") == [(0,)]
    with server(tmp_path, port, number=2) as client:
        assert post(client, payload).status_code == 202
        assert (
            post(client, {**payload, "request_id": "cannot-reconstruct-driver"}).status_code == 409
        )


def test_h03_late_registration_from_the_actual_returned_context_is_denied(tmp_path):
    port = free_port()
    config = fixture(tmp_path, port)
    with server(tmp_path, port) as client:
        saved = journey(client, config, until="initialize-42")
        payload = request_payload(
            client,
            "start_first_phase",
            "late-first",
            **action_fields("start_first_phase", saved, config),
        )
        arm(tmp_path, "start_first_phase", "after_worker_release", mode="late_registration")
        response = post(client, payload)
        assert response.status_code == 200, response.text
        assert (tmp_path / "late-registration-denied").read_text() == "revoked"


@pytest.mark.parametrize(
    "failure,approved",
    [("", False), ("second_review", True), ("second_conditional", True), ("second_tests", True)],
)
def test_h06_actual_unqualified_second_phase_cannot_preview_or_accept(tmp_path, failure, approved):
    port = free_port()
    config = fixture(tmp_path, port, failure=failure)
    if failure == "second_tests":
        config["policy"]["profiles"][0]["argv"][-1] += (
            "; assert answer()!=44, 'negative second test'"
        )
        (tmp_path / "binding.json").write_text(json.dumps(config))
    with server(tmp_path, port) as client:
        saved = journey(client, config, until="scope-44", second_approved=approved)
        terminal = saved["scope-44"]["response"]
        assert terminal["outcome"] in {"rejected", "failed"}, terminal
        payload = request_payload(
            client,
            "preview_final_source",
            "negative-final-preview",
            **action_fields("preview_final_source", saved, config),
        )
        before = calls(tmp_path)
        assert post(client, payload).status_code == 409
        assert calls(tmp_path) == before
        assert client.get(PREFIX).json()["accepted"]["generation"] == 1
        assert sql(tmp_path, "SELECT COUNT(*) FROM program_source_acceptances") == [(1,)]
