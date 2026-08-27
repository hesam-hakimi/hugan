import { afterEach, describe, expect, it, vi } from "vitest";

import { api } from "./api";

function successfulJson(body: Record<string, unknown> = {}) {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("Program execution API client", () => {
  it("loads Program and execution state with read-only requests", async () => {
    const fetchMock = vi.fn(async () => successfulJson());
    vi.stubGlobal("fetch", fetchMock);

    await Promise.all([
      api.program("program with spaces"),
      api.programExecutions("program with spaces"),
    ]);

    const programRequest = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    const executionRequest = fetchMock.mock.calls[1] as unknown as [string, RequestInit];
    expect(programRequest[0]).toBe("/api/programs/program%20with%20spaces");
    expect(executionRequest[0]).toBe(
      "/api/programs/program%20with%20spaces/executions",
    );
    expect(programRequest[1].method).toBeUndefined();
    expect(executionRequest[1].method).toBeUndefined();
    expect(programRequest[1].body).toBeUndefined();
    expect(executionRequest[1].body).toBeUndefined();
  });

  it("loads task state with a read-only request", async () => {
    const fetchMock = vi.fn(async () => successfulJson());
    vi.stubGlobal("fetch", fetchMock);

    await api.task("task/with spaces");

    const request = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(request[0]).toBe("/api/tasks/task%2Fwith%20spaces");
    expect(request[1].method).toBeUndefined();
    expect(request[1].body).toBeUndefined();
  });

  it("loads the first bounded retained-lease page with a read-only request", async () => {
    const fetchMock = vi.fn(async () => successfulJson());
    vi.stubGlobal("fetch", fetchMock);

    await api.retainedRemoteOperationLeases();

    const request = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(request[0]).toBe("/api/remote-operations/retained-leases?limit=25");
    expect(request[1].method).toBeUndefined();
    expect(request[1].body).toBeUndefined();
  });

  it("loads one keyset continuation without widening the bounded page", async () => {
    const fetchMock = vi.fn(async () => successfulJson());
    vi.stubGlobal("fetch", fetchMock);

    await api.retainedRemoteOperationLeases("task.page-25");

    const request = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(request[0]).toBe(
      "/api/remote-operations/retained-leases?limit=25&after_task_id=task.page-25",
    );
    expect(request[1].method).toBeUndefined();
    expect(request[1].body).toBeUndefined();
  });

  it("loads lifecycle recovery candidates with a read-only request", async () => {
    const fetchMock = vi.fn(async () => successfulJson());
    vi.stubGlobal("fetch", fetchMock);

    await api.lifecycleRecovery();

    const request = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(request[0]).toBe(
      "/api/admin/lifecycle-recovery?candidate_limit=25&receipt_limit=25",
    );
    expect(request[1].method).toBeUndefined();
    expect(request[1].body).toBeUndefined();
  });

  it("loads independent lifecycle recovery continuations without widening either page", async () => {
    const fetchMock = vi.fn(async () => successfulJson());
    vi.stubGlobal("fetch", fetchMock);

    await api.lifecycleRecovery({
      candidateAfter: "candidate_cursor",
      candidateLimit: 25,
      receiptLimit: 0,
    });
    await api.lifecycleRecovery({
      receiptAfter: "receipt_cursor",
      candidateLimit: 0,
      receiptLimit: 25,
    });

    const candidateRequest = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    const receiptRequest = fetchMock.mock.calls[1] as unknown as [string, RequestInit];
    expect(candidateRequest[0]).toBe(
      "/api/admin/lifecycle-recovery?candidate_limit=25&receipt_limit=0&candidate_after=candidate_cursor",
    );
    expect(receiptRequest[0]).toBe(
      "/api/admin/lifecycle-recovery?candidate_limit=0&receipt_limit=25&receipt_after=receipt_cursor",
    );
    expect(candidateRequest[1].method).toBeUndefined();
    expect(candidateRequest[1].body).toBeUndefined();
    expect(receiptRequest[1].method).toBeUndefined();
    expect(receiptRequest[1].body).toBeUndefined();
  });

  it("recovers exactly one lifecycle target only through a confirmed POST", async () => {
    const fetchMock = vi.fn(async () => successfulJson());
    vi.stubGlobal("fetch", fetchMock);
    const candidate = {
      schema_version: "1" as const,
      target_type: "worker_ownership" as const,
      target_kind: "program_execution" as const,
      scope_id: "program-1",
      task_id: "",
      program_id: "program-1",
      created_at: "2026-08-27T00:00:00+00:00",
      recovery_ref: `sha256:${"e".repeat(64)}`,
      same_runtime_active: false,
      eligible_for_recovery: true,
      eligibility_is_advisory: true as const,
      requires_operator_process_verification: true as const,
    };

    await api.recoverLifecycleTarget(candidate, "Verified stopped.");

    const request = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(request[0]).toBe("/api/admin/lifecycle-recovery");
    expect(request[1].method).toBe("POST");
    expect(JSON.parse(String(request[1].body))).toEqual({
      target_type: "worker_ownership",
      target_kind: "program_execution",
      scope_id: "program-1",
      recovery_ref: candidate.recovery_ref,
      reason: "Verified stopped.",
      confirmed: true,
    });
  });

  it("starts the next execution unit only through an explicit POST", async () => {
    const fetchMock = vi.fn(async () => successfulJson());
    vi.stubGlobal("fetch", fetchMock);
    const payload = {
      current_requirement_hash: "a".repeat(64),
      repository: "https://example.test/repository.git",
      ref: "main",
      policy: { policy_version: "1", profiles: [] },
      test_profiles: ["focused-tests"],
    };

    await api.startProgramExecution("program-1", payload);

    const request = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(request[0]).toBe("/api/programs/program-1/executions/start-next");
    expect(request[1].method).toBe("POST");
    expect(JSON.parse(String(request[1].body))).toEqual(payload);
  });

  it("continues one bound task with the explicit approval decision", async () => {
    const fetchMock = vi.fn(async () => successfulJson());
    vi.stubGlobal("fetch", fetchMock);

    await api.continueProgramExecution(
      "program-1",
      "task/1",
      "b".repeat(64),
      false,
    );

    const request = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(request[0]).toBe(
      "/api/programs/program-1/executions/task%2F1/continue",
    );
    expect(request[1].method).toBe("POST");
    expect(JSON.parse(String(request[1].body))).toEqual({
      current_requirement_hash: "b".repeat(64),
      approved: false,
    });
  });

  it.each(["observe", "cancel"] as const)(
    "reconciles a remote operation only through an explicit %s POST",
    async (action) => {
      const fetchMock = vi.fn(async () => successfulJson());
      vi.stubGlobal("fetch", fetchMock);

      await api.reconcileRemoteOperation("task/1", action);

      const request = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
      expect(request[0]).toBe(
        "/api/tasks/task%2F1/remote-operation/reconcile",
      );
      expect(request[1].method).toBe("POST");
      expect(JSON.parse(String(request[1].body))).toEqual({ action });
    },
  );

  it.each(["cancelled", "failed"] as const)(
    "disposes remote task state only through an explicit confirmed %s POST",
    async (outcome) => {
      const fetchMock = vi.fn(async () => successfulJson());
      vi.stubGlobal("fetch", fetchMock);

      await api.disposeRemoteOperation(
        "task/1",
        outcome,
        "Operator-confirmed orphan disposition.",
      );

      const request = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
      expect(request[0]).toBe(
        "/api/tasks/task%2F1/remote-operation/dispose",
      );
      expect(request[1].method).toBe("POST");
      expect(JSON.parse(String(request[1].body))).toEqual({
        outcome,
        reason: "Operator-confirmed orphan disposition.",
        confirmed: true,
      });
    },
  );

  it("retires a private lease only through an explicit disposition-bound POST", async () => {
    const fetchMock = vi.fn(async () => successfulJson());
    vi.stubGlobal("fetch", fetchMock);
    const auditRef = `sha256:${"d".repeat(64)}`;

    await api.retireRemoteOperationLease(
      "task/1",
      auditRef,
      "Operator approved local private lease retirement.",
    );

    const request = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(request[0]).toBe(
      "/api/tasks/task%2F1/remote-operation/retire",
    );
    expect(request[1].method).toBe("POST");
    expect(JSON.parse(String(request[1].body))).toEqual({
      disposition_audit_ref: auditRef,
      reason: "Operator approved local private lease retirement.",
      confirmed: true,
    });
  });
});
