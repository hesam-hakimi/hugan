export type Clarification = {
  question_id: string;
  decision_key: string;
  question: string;
  severity: "blocking" | "material" | "minor";
  rationale: string;
  options: string[];
  recommended_answer: string;
};

export type RequirementContract = {
  alignment_id: string;
  version: number;
  title: string;
  objective: string;
  requirements: Array<{ requirement_id: string; statement: string; category: string }>;
  acceptance_criteria: Array<{
    criterion_id: string;
    statement: string;
    requirement_ids: string[];
  }>;
  constraints: string[];
  exclusions: string[];
  assumptions: string[];
  clarifications: Clarification[];
  answers: Record<string, string>;
  status: "needs_clarification" | "ready_for_approval" | "approved" | "superseded";
};

export type RequirementResult = {
  contract: RequirementContract;
  requirement_hash: string;
  contract_ref: string;
  context_ref: string;
  validation_ref: string;
};

export type ProgramSnapshot = {
  program_id: string;
  status: string;
  plan_hash: string;
  plan: {
    title: string;
    objective: string;
    requirement_hash: string;
    phases: Array<{
      phase_id: string;
      title: string;
      objective: string;
      dependencies: string[];
    }>;
    definition_of_done: string[];
  };
  phases: Array<{
    phase_id: string;
    title: string;
    status: string;
    dependencies: string[];
  }>;
};

export type ControlSnapshot = {
  entity_type?: "task" | "program";
  entity_id?: string;
  state: string;
  reason: string;
  revision: number;
};

export type CancellationReport = {
  task_id: string;
  reason: string;
  active_operation_kinds: string[];
  owned_processes_observed: number;
  owned_cancellable_operations_observed: number;
  terminate_requests: number;
  kill_requests: number;
  cancellable_operation_cancel_requests: number;
  processes_still_active: number;
  cancellable_operations_still_active: number;
  cooperative_fallback: boolean;
};

export type RemoteOperationSnapshot = {
  task_id: string;
  thread_id: string;
  transport: string;
  transport_scope: string;
  operation_ref: string;
  base_sha: string;
  created_at: string;
  updated_at: string;
  last_status: string;
  state: "active" | "terminal" | "unavailable";
  cancellation_requested: boolean;
  revision: number;
  reconciliation_attempts: number;
  cancel_requests: number;
  last_action: "observe" | "cancel" | null;
  recovered_pending: boolean;
  requires_explicit_action: boolean;
};

export type RemoteOperationReconciliationResult = {
  task_id: string;
  action: "observe" | "cancel";
  remote_operation: RemoteOperationSnapshot;
};

export type ProgramExecutionBinding = {
  program_id: string;
  phase_id: string;
  slice_id: string | null;
  task_id: string;
  thread_id: string;
  requirement_hash: string;
  status: "starting" | "awaiting_scope_approval" | "running" | "completed" | "failed" | "cancelled";
  safe_status: string;
  result_ref: string;
  phase_report_ref: string;
  error_ref: string;
  accepted_evidence_ref: string;
  accepted_evidence_hash: string;
  expected_base_sha: string;
  control?: ControlSnapshot;
  cancellation_report?: CancellationReport;
  remote_operation?: RemoteOperationSnapshot;
};

export type ProgramExecutionSnapshot = {
  program_id: string;
  program_status: string;
  runtime: {
    busy: boolean;
    action: string;
    task_id: string;
    status: string;
    recovered_pending: boolean;
    requires_explicit_action: boolean;
    error_type: string;
    error: string;
  };
  bindings: ProgramExecutionBinding[];
};

export type SearchHit = {
  record_id: string;
  source_type: string;
  source_id: string;
  path: string;
  score: number;
  excerpt: string;
  metadata: Record<string, unknown>;
};

export type ContextDocument = {
  document_id: string;
  filename: string;
  role: string;
  scope: string;
  scope_id: string;
  sha256: string;
  size: number;
};

export type TaskSnapshot = {
  task_id: string;
  thread_id?: string;
  title?: string;
  status?: string;
  busy?: boolean;
  error?: string;
  error_type?: string;
  control?: ControlSnapshot;
  cancellation_report?: CancellationReport;
  remote_operation?: RemoteOperationSnapshot;
  result?: Record<string, unknown>;
};
