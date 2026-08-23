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
});
