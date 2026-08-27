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
  requires_explicit_disposition: boolean;
};

export type RemoteOperationReconciliationResult = {
  task_id: string;
  action: "observe" | "cancel";
  remote_operation: RemoteOperationSnapshot;
};

export type RemoteOperationDisposition = {
  schema_version: "1";
  audit_ref: string;
  task_id: string;
  outcome: "cancelled" | "failed";
  reason: string;
  recorded_at: string;
  program_id: string;
  phase_id: string;
  slice_id: string;
  transport: string;
  transport_scope: string;
  operation_ref: string;
  base_sha: string;
  remote_state: "terminal" | "unavailable";
  remote_status: string;
  remote_revision: number;
  remote_updated_at: string;
  provider_confirmed_cancelled: boolean;
  confirmed_by_operator: boolean;
  provider_calls_made: 0;
  output_consumed: false;
  graph_resumed: false;
  program_phase_advanced: false;
};

export type RemoteOperationDispositionResult = {
  task_id: string;
  outcome: "cancelled" | "failed";
  program_id: string;
  remote_operation_disposition: RemoteOperationDisposition;
};

export type RemoteOperationLeaseRetirement = {
  schema_version: "1";
  retirement_ref: string;
  task_id: string;
  disposition_audit_ref: string;
  disposition_outcome: "cancelled" | "failed";
  program_id: string;
  phase_id: string;
  slice_id: string;
  reason: string;
  retired_at: string;
  transport: string;
  transport_scope: string;
  operation_ref: string;
  base_sha: string;
  remote_state: "terminal" | "unavailable";
  remote_status: string;
  remote_revision: number;
  remote_updated_at: string;
  confirmed_by_operator: true;
  private_lease_rows_retired: 1;
  private_identifier_retained_in_active_store: false;
  provider_calls_made: 0;
  output_consumed: false;
  graph_resumed: false;
  task_outcome_changes_made: 0;
  program_outcome_changes_made: 0;
  program_phase_advanced: false;
};

export type RemoteOperationLeaseRetirementResult = {
  task_id: string;
  outcome: "cancelled" | "failed";
  program_id: string;
  remote_operation_disposition: RemoteOperationDisposition;
  remote_operation_lease_retirement: RemoteOperationLeaseRetirement;
};

export type RemoteOperationLeaseRetirementEligibilityCode =
  | "lifecycle_action_active"
  | "local_worker_active"
  | "active_private_lease"
  | "disposition_audit_invalid"
  | "lease_disposition_mismatch"
  | "task_control_missing"
  | "task_control_state_mismatch"
  | "retirement_receipt_conflict"
  | "retirement_receipt_invalid"
  | "program_binding_missing"
  | "program_binding_mismatch"
  | "program_evidence_oversized"
  | "program_evidence_incomplete";

export type RemoteOperationLeaseRetirementEligibilityReason = {
  code: RemoteOperationLeaseRetirementEligibilityCode;
  message: string;
};

export type RetainedRemoteOperationLeaseInventoryItem = {
  schema_version: "1";
  task_id: string;
  program_id: string;
  phase_id: string;
  slice_id: string;
  transport: string;
  remote_state: "active" | "terminal" | "unavailable";
  remote_status: string;
  remote_revision: number;
  remote_updated_at: string;
  disposition_audit_ref: string;
  disposition_outcome: "cancelled" | "failed";
  disposition_recorded_at: string;
  retained_private_lease: true;
  eligible_for_retirement: boolean;
  eligibility_reasons: RemoteOperationLeaseRetirementEligibilityReason[];
  preview_is_advisory: true;
  action_revalidation_required: true;
};

export type RetainedRemoteOperationLeaseInventory = {
  schema_version: "1";
  generated_at: string;
  items: RetainedRemoteOperationLeaseInventoryItem[];
  returned_count: number;
  scanned_count: number;
  has_more: boolean;
  next_after_task_id: string;
  read_only: true;
  provider_calls_made: 0;
  mutations_made: false;
  opaque_provider_identifiers_exposed: false;
};

export type LifecycleRecoveryCandidate = {
  schema_version: "1";
  target_type: "reservation" | "worker_ownership";
  target_kind:
    | "remote_operation"
    | "program_control"
    | "standalone_task"
    | "program_execution";
  scope_id: string;
  task_id: string;
  program_id: string;
  created_at: string;
  recovery_ref: string;
  same_runtime_active: boolean;
  eligible_for_recovery: boolean;
  eligibility_is_advisory: true;
  requires_operator_process_verification: true;
};

export type LifecycleRecoveryReceipt = {
  schema_version: "1";
  target_type: LifecycleRecoveryCandidate["target_type"];
  target_kind: LifecycleRecoveryCandidate["target_kind"];
  scope_id: string;
  task_id: string;
  program_id: string;
  created_at: string;
  recovery_ref: string;
  reason: string;
  recovered_at: string;
  audit_ref: string;
  confirmed_by_operator: true;
  rows_recovered: 1;
  provider_calls_made: 0;
  automatic_cleanup: false;
};

export type LifecycleRecoverySnapshot = {
  schema_version: "1";
  candidates: LifecycleRecoveryCandidate[];
  recoveries: LifecycleRecoveryReceipt[];
  ttl_enabled: false;
  automatic_cleanup_enabled: false;
  provider_calls_made: 0;
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
  remote_disposition_ref: string;
  control?: ControlSnapshot;
  cancellation_report?: CancellationReport;
  remote_operation?: RemoteOperationSnapshot;
  remote_operation_disposition?: RemoteOperationDisposition;
  remote_operation_lease_retirement?: RemoteOperationLeaseRetirement;
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
  remote_operation_disposition?: RemoteOperationDisposition;
  remote_operation_lease_retirement?: RemoteOperationLeaseRetirement;
  result?: Record<string, unknown>;
};
