import type {
  ContextDocument,
  ProgramExecutionSnapshot,
  ProgramSnapshot,
  RemoteOperationDispositionResult,
  RemoteOperationLeaseRetirementResult,
  RemoteOperationReconciliationResult,
  RequirementContract,
  RequirementResult,
  SearchHit,
  TaskSnapshot,
} from "./types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = typeof body?.detail === "string" ? body.detail : `Request failed: ${response.status}`;
    throw new Error(message);
  }
  return body as T;
}

export const api = {
  health: () => request<{ status: string; api: string; browser_credentials: boolean }>("/api/health"),

  search: (query: string, topK = 20) =>
    request<{ hits: SearchHit[] }>("/api/search", {
      method: "POST",
      body: JSON.stringify({ query, top_k: topK }),
    }),

  listDocuments: (scopeId?: string) =>
    request<{ documents: ContextDocument[] }>(
      `/api/documents${scopeId ? `?scope_id=${encodeURIComponent(scopeId)}` : ""}`,
    ),

  uploadDocument: (payload: {
    document_id: string;
    filename: string;
    content: string;
    role: string;
    scope: string;
    scope_id: string;
  }) =>
    request<ContextDocument>("/api/documents", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  analyzeRequirement: (payload: {
    alignment_id: string;
    title: string;
    objective: string;
    answers: Record<string, string>;
    previous?: RequirementContract;
  }) =>
    request<RequirementResult>("/api/requirements/analyze", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  approveRequirement: (contract: RequirementContract) =>
    request<RequirementResult>("/api/requirements/approve", {
      method: "POST",
      body: JSON.stringify({ contract }),
    }),

  createProgram: (payload: {
    program_id: string;
    requirement: RequirementContract;
    requirement_hash: string;
  }) =>
    request<ProgramSnapshot>("/api/programs", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  program: (programId: string) =>
    request<ProgramSnapshot>(`/api/programs/${encodeURIComponent(programId)}`),

  approveProgram: (programId: string, planHash: string) =>
    request<ProgramSnapshot>(`/api/programs/${encodeURIComponent(programId)}/approve`, {
      method: "POST",
      body: JSON.stringify({ plan_hash: planHash }),
    }),

  programControl: (programId: string, action: "pause" | "resume" | "cancel", reason = "") =>
    request<ProgramSnapshot>(`/api/programs/${encodeURIComponent(programId)}/${action}`, {
      method: "POST",
      body: action === "resume" ? undefined : JSON.stringify({ reason }),
    }),

  programExecutions: (programId: string) =>
    request<ProgramExecutionSnapshot>(
      `/api/programs/${encodeURIComponent(programId)}/executions`,
    ),

  startProgramExecution: (
    programId: string,
    payload: {
      current_requirement_hash: string;
      repository: string;
      ref: string;
      policy: Record<string, unknown>;
      test_profiles: string[];
    },
  ) =>
    request<ProgramExecutionSnapshot>(
      `/api/programs/${encodeURIComponent(programId)}/executions/start-next`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
    ),

  continueProgramExecution: (
    programId: string,
    taskId: string,
    currentRequirementHash: string,
    approved: boolean,
  ) =>
    request<ProgramExecutionSnapshot>(
      `/api/programs/${encodeURIComponent(programId)}/executions/${encodeURIComponent(taskId)}/continue`,
      {
        method: "POST",
        body: JSON.stringify({
          current_requirement_hash: currentRequirementHash,
          approved,
        }),
      },
    ),

  startSafeTask: (payload: Record<string, unknown>) =>
    request<TaskSnapshot>("/api/tasks/safe", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  task: (taskId: string) => request<TaskSnapshot>(`/api/tasks/${encodeURIComponent(taskId)}`),

  reconcileRemoteOperation: (taskId: string, action: "observe" | "cancel") =>
    request<RemoteOperationReconciliationResult>(
      `/api/tasks/${encodeURIComponent(taskId)}/remote-operation/reconcile`,
      {
        method: "POST",
        body: JSON.stringify({ action }),
      },
    ),

  disposeRemoteOperation: (
    taskId: string,
    outcome: "cancelled" | "failed",
    reason: string,
  ) =>
    request<RemoteOperationDispositionResult>(
      `/api/tasks/${encodeURIComponent(taskId)}/remote-operation/dispose`,
      {
        method: "POST",
        body: JSON.stringify({ outcome, reason, confirmed: true }),
      },
    ),

  retireRemoteOperationLease: (
    taskId: string,
    dispositionAuditRef: string,
    reason: string,
  ) =>
    request<RemoteOperationLeaseRetirementResult>(
      `/api/tasks/${encodeURIComponent(taskId)}/remote-operation/retire`,
      {
        method: "POST",
        body: JSON.stringify({
          disposition_audit_ref: dispositionAuditRef,
          reason,
          confirmed: true,
        }),
      },
    ),

  taskControl: (taskId: string, action: "pause" | "resume" | "cancel", reason = "") =>
    request<TaskSnapshot>(`/api/tasks/${encodeURIComponent(taskId)}/${action}`, {
      method: "POST",
      body: action === "resume" ? undefined : JSON.stringify({ reason }),
    }),

  scopeDecision: (taskId: string, approved: boolean) =>
    request<TaskSnapshot>(`/api/tasks/${encodeURIComponent(taskId)}/scope-decision`, {
      method: "POST",
      body: JSON.stringify({ approved }),
    }),
};
