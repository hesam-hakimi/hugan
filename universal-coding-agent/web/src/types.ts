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
  control?: {
    state: string;
    reason: string;
    revision: number;
  };
  result?: Record<string, unknown>;
};
