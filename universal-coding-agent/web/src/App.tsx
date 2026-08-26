import { useEffect, useMemo, useState } from "react";

import { api } from "./api";
import type {
  CancellationReport,
  ContextDocument,
  ProgramExecutionSnapshot,
  ProgramSnapshot,
  RemoteOperationSnapshot,
  RequirementResult,
  SearchHit,
  TaskSnapshot,
} from "./types";
import {
  activeProgramExecutionBinding,
  canApproveScope,
  canContinueProgramExecution,
  canReconcileRemoteOperation,
  canStartProgramExecution,
  cancellationEvidencePresentation,
  phaseProgress,
  remoteOperationPresentation,
  statusTone,
  unresolvedClarifications,
} from "./viewModels";

type ProgramState = {
  program: ProgramSnapshot;
  execution: ProgramExecutionSnapshot;
};

type View = "overview" | "task" | "requirements" | "program" | "documents" | "search";

const navItems: Array<{ id: View; label: string; eyebrow: string }> = [
  { id: "overview", label: "Overview", eyebrow: "Control center" },
  { id: "task", label: "New task", eyebrow: "Safe execution" },
  { id: "requirements", label: "Requirements", eyebrow: "Clarify & freeze" },
  { id: "program", label: "Program", eyebrow: "Phase delivery" },
  { id: "documents", label: "Documents", eyebrow: "Text context" },
  { id: "search", label: "Search", eyebrow: "Code & evidence" },
];

const defaultPolicy = JSON.stringify(
  {
    policy_version: "1",
    profiles: [
      {
        profile_id: "focused-tests",
        argv: ["python", "-m", "pytest", "-q"],
        cwd: ".",
        timeout_seconds: 300,
        output_limit: 20000,
      },
    ],
  },
  null,
  2,
);

export default function App() {
  const [view, setView] = useState<View>("overview");
  const [health, setHealth] = useState("connecting");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const [requirement, setRequirement] = useState<RequirementResult>();
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [alignmentId, setAlignmentId] = useState("customer-export");
  const [requirementTitle, setRequirementTitle] = useState("Customer export");
  const [requirementObjective, setRequirementObjective] = useState("");

  const [program, setProgram] = useState<ProgramSnapshot>();
  const [programExecution, setProgramExecution] = useState<ProgramExecutionSnapshot>();
  const [programId, setProgramId] = useState("program-customer-export");

  const [documents, setDocuments] = useState<ContextDocument[]>([]);
  const [documentId, setDocumentId] = useState("product-order-001");
  const [documentFilename, setDocumentFilename] = useState("product-order.md");
  const [documentContent, setDocumentContent] = useState("");
  const [documentRole, setDocumentRole] = useState("requirement");
  const [documentScope, setDocumentScope] = useState("program");
  const [documentScopeId, setDocumentScopeId] = useState("program-customer-export");

  const [query, setQuery] = useState("");
  const [hits, setHits] = useState<SearchHit[]>([]);

  const [repository, setRepository] = useState("");
  const [ref, setRef] = useState("main");
  const [taskTitle, setTaskTitle] = useState("Safe implementation");
  const [taskObjective, setTaskObjective] = useState("");
  const [testProfiles, setTestProfiles] = useState("focused-tests");
  const [policyText, setPolicyText] = useState(defaultPolicy);
  const [task, setTask] = useState<TaskSnapshot>();
  const [taskLookupId, setTaskLookupId] = useState("");

  useEffect(() => {
    api.health()
      .then((result) => setHealth(result.status))
      .catch(() => setHealth("offline"));
    void refreshDocuments();
  }, []);

  useEffect(() => {
    if (!task?.task_id || ["completed", "failed", "cancelled"].includes(task.status ?? "")) {
      return;
    }
    const timer = window.setInterval(() => {
      api.task(task.task_id).then(applyTaskState).catch(() => undefined);
    }, 1600);
    return () => window.clearInterval(timer);
  }, [task?.task_id, task?.status]);

  useEffect(() => {
    if (!program?.program_id || !programExecution?.runtime.busy) {
      return;
    }
    const loadedProgramId = program.program_id;
    const timer = window.setInterval(() => {
      Promise.all([
        api.program(loadedProgramId),
        api.programExecutions(loadedProgramId),
      ])
        .then(([programSnapshot, executionSnapshot]) => {
          setProgram(programSnapshot);
          setProgramExecution(executionSnapshot);
        })
        .catch(() => undefined);
    }, 1600);
    return () => window.clearInterval(timer);
  }, [program?.program_id, programExecution?.runtime.busy]);

  const unresolved = useMemo(
    () => unresolvedClarifications(requirement?.contract),
    [requirement],
  );
  const progress = phaseProgress(program);
  const activeProgramExecution = activeProgramExecutionBinding(programExecution);
  const programExecutionCanStart = canStartProgramExecution(program, programExecution);
  const programExecutionCanContinue = canContinueProgramExecution(program, programExecution);

  async function perform<T>(action: () => Promise<T>, onSuccess: (value: T) => void, success: string) {
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const value = await action();
      onSuccess(value);
      setMessage(success);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught));
    } finally {
      setBusy(false);
    }
  }

  async function refreshDocuments() {
    try {
      const result = await api.listDocuments();
      setDocuments(result.documents);
    } catch {
      // Health state communicates API availability; document refresh is best effort.
    }
  }

  function analyzeRequirement() {
    void perform(
      () =>
        api.analyzeRequirement({
          alignment_id: alignmentId,
          title: requirementTitle,
          objective: requirementObjective,
          answers,
          previous: requirement?.contract,
        }),
      setRequirement,
      "Requirement analysis updated.",
    );
  }

  function approveRequirement() {
    if (!requirement) return;
    void perform(
      () => api.approveRequirement(requirement.contract),
      setRequirement,
      "Requirement contract approved and frozen.",
    );
  }

  function applyProgramState(state: ProgramState) {
    setProgram(state.program);
    setProgramExecution(state.execution);
    setProgramId(state.program.program_id);
  }

  function applyTaskState(snapshot: TaskSnapshot) {
    setTask(snapshot);
    setTaskLookupId(snapshot.task_id);
  }

  async function readProgramState(id: string): Promise<ProgramState> {
    const loadedProgram = await api.program(id);
    const execution = await api.programExecutions(loadedProgram.program_id);
    return { program: loadedProgram, execution };
  }

  async function attachExecutionState(
    programRequest: Promise<ProgramSnapshot>,
  ): Promise<ProgramState> {
    const updatedProgram = await programRequest;
    const execution = await api.programExecutions(updatedProgram.program_id);
    return { program: updatedProgram, execution };
  }

  async function attachProgramState(
    executionRequest: Promise<ProgramExecutionSnapshot>,
  ): Promise<ProgramState> {
    const execution = await executionRequest;
    const updatedProgram = await api.program(execution.program_id);
    return { program: updatedProgram, execution };
  }

  function loadProgram() {
    const requestedProgramId = programId.trim();
    if (!requestedProgramId) return;
    void perform(
      () => readProgramState(requestedProgramId),
      applyProgramState,
      "Program and persisted execution state loaded.",
    );
  }

  function refreshProgram() {
    if (!program) return;
    void perform(
      () => readProgramState(program.program_id),
      applyProgramState,
      "Program execution status refreshed without starting work.",
    );
  }

  function reconcileProgramRemoteOperation(
    taskId: string,
    action: "observe" | "cancel",
  ) {
    if (!program) return;
    if (
      action === "cancel" &&
      !window.confirm(
        `Request bounded remote cancellation for ${taskId}? The UI will report termination only after the provider confirms a terminal state.`,
      )
    ) {
      return;
    }
    void perform(
      async () => {
        await api.reconcileRemoteOperation(taskId, action);
        return readProgramState(program.program_id);
      },
      applyProgramState,
      action === "observe"
        ? "Remote state observed without resuming Program work."
        : "Remote cancellation requested; the displayed provider state is the bounded outcome.",
    );
  }

  function createProgram() {
    if (!requirement || requirement.contract.status !== "approved") return;
    void perform(
      () =>
        attachExecutionState(
          api.createProgram({
            program_id: programId,
            requirement: requirement.contract,
            requirement_hash: requirement.requirement_hash,
          }),
        ),
      applyProgramState,
      "Program plan created and awaiting approval.",
    );
  }

  function controlProgram(action: "pause" | "resume" | "cancel") {
    if (!program) return;
    void perform(
      () =>
        attachExecutionState(
          api.programControl(
            program.program_id,
            action,
            "Operator action from Control Center",
          ),
        ),
      applyProgramState,
      `Program ${action} applied.`,
    );
  }

  function trustedExecutionInputs(): {
    policy: Record<string, unknown>;
    testProfiles: string[];
  } | undefined {
    let policy: Record<string, unknown>;
    try {
      policy = JSON.parse(policyText) as Record<string, unknown>;
    } catch {
      setError("Trusted policy must be valid JSON.");
      return undefined;
    }
    const profiles = testProfiles
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);
    if (profiles.length === 0) {
      setError("At least one trusted test profile is required.");
      return undefined;
    }
    return { policy, testProfiles: profiles };
  }

  function startProgramExecution() {
    if (
      !program ||
      !programExecutionCanStart ||
      !repository.trim() ||
      !ref.trim()
    ) {
      return;
    }
    const inputs = trustedExecutionInputs();
    if (!inputs) return;
    if (
      !window.confirm(
        "Start exactly one dependency-ready Program unit through Discovered Safe Mode?",
      )
    ) {
      return;
    }
    void perform(
      () =>
        attachProgramState(
          api.startProgramExecution(program.program_id, {
            current_requirement_hash: program.plan.requirement_hash,
            repository: repository.trim(),
            ref: ref.trim(),
            policy: inputs.policy,
            test_profiles: inputs.testProfiles,
          }),
        ),
      applyProgramState,
      "One dependency-ready Program unit was explicitly queued.",
    );
  }

  function continueProgramExecution(approved: boolean) {
    if (!program || !activeProgramExecution || !programExecutionCanContinue) return;
    const decision = approved ? "approve" : "reject";
    if (
      !window.confirm(
        `${decision[0].toUpperCase()}${decision.slice(1)} the pending Safe checkpoint for ${activeProgramExecution.task_id}?`,
      )
    ) {
      return;
    }
    void perform(
      () =>
        attachProgramState(
          api.continueProgramExecution(
            program.program_id,
            activeProgramExecution.task_id,
            program.plan.requirement_hash,
            approved,
          ),
        ),
      applyProgramState,
      approved
        ? "The checkpoint was explicitly approved and queued for continuation."
        : "The checkpoint was explicitly rejected; implementation was not approved.",
    );
  }

  function uploadDocument() {
    void perform(
      () =>
        api.uploadDocument({
          document_id: documentId,
          filename: documentFilename,
          content: documentContent,
          role: documentRole,
          scope: documentScope,
          scope_id: documentScopeId,
        }),
      () => {
        setDocumentContent("");
        void refreshDocuments();
      },
      "Document stored as immutable text context.",
    );
  }

  function runSearch() {
    void perform(
      () => api.search(query, 30),
      (result) => setHits(result.hits),
      "Search completed.",
    );
  }

  function loadTask() {
    const requestedTaskId = taskLookupId.trim();
    if (!requestedTaskId) return;
    void perform(
      () => api.task(requestedTaskId),
      applyTaskState,
      "Task state loaded without starting provider work.",
    );
  }

  function refreshTask() {
    if (!task) return;
    void perform(
      () => api.task(task.task_id),
      applyTaskState,
      "Task state refreshed without starting provider work.",
    );
  }

  function startTask() {
    let policy: Record<string, unknown>;
    try {
      policy = JSON.parse(policyText) as Record<string, unknown>;
    } catch {
      setError("Trusted policy must be valid JSON.");
      return;
    }
    const profiles = testProfiles
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);
    void perform(
      () =>
        api.startSafeTask({
          title: taskTitle,
          objective: taskObjective,
          repository,
          ref,
          policy,
          test_profiles: profiles,
          acceptance_criteria: requirement?.contract.acceptance_criteria.map((item) => item.statement) ?? [],
        }),
      applyTaskState,
      "Safe task queued. Discovery has no write authority.",
    );
  }

  function controlTask(action: "pause" | "resume" | "cancel") {
    if (!task) return;
    void perform(
      () => api.taskControl(task.task_id, action, "Operator action from Control Center"),
      applyTaskState,
      `Task ${action} requested.`,
    );
  }

  function reconcileTaskRemoteOperation(action: "observe" | "cancel") {
    if (!task) return;
    if (
      action === "cancel" &&
      !window.confirm(
        `Request bounded remote cancellation for ${task.task_id}? The UI will report termination only after the provider confirms a terminal state.`,
      )
    ) {
      return;
    }
    const taskId = task.task_id;
    void perform(
      () => api.reconcileRemoteOperation(taskId, action),
      (result) => {
        setTask((current) =>
          current?.task_id === result.task_id
            ? { ...current, remote_operation: result.remote_operation }
            : current,
        );
      },
      action === "observe"
        ? "Remote state observed without resuming task work."
        : "Remote cancellation requested; the displayed provider state is the bounded outcome.",
    );
  }

  function scopeDecision(approved: boolean) {
    if (!task) return;
    void perform(
      () => api.scopeDecision(task.task_id, approved),
      applyTaskState,
      approved ? "Scope approved; Safe Mode may implement." : "Scope rejected; no implementation approved.",
    );
  }

  async function readSelectedFile(file?: File) {
    if (!file) return;
    setDocumentFilename(file.name);
    setDocumentContent(await file.text());
    setDocumentId(`doc-${Date.now()}`);
  }

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brandMark">U</div>
          <div>
            <strong>Universal Coding Agent</strong>
            <span>Governed delivery workspace</span>
          </div>
        </div>
        <nav>
          {navItems.map((item) => (
            <button
              key={item.id}
              className={view === item.id ? "navItem active" : "navItem"}
              onClick={() => setView(item.id)}
            >
              <span>{item.eyebrow}</span>
              {item.label}
            </button>
          ))}
        </nav>
        <div className="sidebarFooter">
          <span className={`dot ${health === "ok" ? "online" : ""}`} />
          API {health}
          <small>Credentials stay on the host</small>
        </div>
      </aside>

      <main>
        <header className="topbar">
          <div>
            <span className="kicker">Product control plane</span>
            <h1>{navItems.find((item) => item.id === view)?.label}</h1>
          </div>
          <div className="topActions">
            {task && (
              <>
                <StatusPill status={task.control?.state ?? task.status} />
                <button className="secondary" onClick={() => controlTask("pause")} disabled={busy}>
                  Pause
                </button>
                <button className="dangerGhost" onClick={() => controlTask("cancel")} disabled={busy}>
                  Stop task
                </button>
              </>
            )}
          </div>
        </header>

        {(message || error) && (
          <div className={error ? "notice error" : "notice success"}>{error || message}</div>
        )}

        {view === "overview" && (
          <section className="stack">
            <div className="heroCard">
              <div>
                <span className="kicker">Delivery status</span>
                <h2>From requirement to reviewed code, with explicit control.</h2>
                <p>
                  Requirements, uploaded evidence, program phases, solution discovery and Safe Mode
                  share one backend state. The browser is a control surface, not the source of truth.
                </p>
              </div>
              <button className="primary" onClick={() => setView("task")}>Start governed task</button>
            </div>
            <div className="metricGrid">
              <Metric label="Requirement" value={requirement?.contract.status ?? "Not started"} />
              <Metric label="Program" value={program?.status ?? "Not created"} />
              <Metric label="Program phases" value={`${progress.completed} / ${progress.total}`} />
              <Metric label="Safe task" value={task?.status ?? "Not running"} />
            </div>
            <div className="grid2">
              <article className="card">
                <h3>Safety model</h3>
                <ul className="checkList">
                  <li>Requirement ambiguity blocks material decisions.</li>
                  <li>Discovery proposes scope without edit authority.</li>
                  <li>Scope approval happens before implementation.</li>
                  <li>
                    Pause prevents new work at the next safe boundary; it does not suspend an
                    active provider or test operation.
                  </li>
                  <li>
                    Cancel prevents new work and requests termination only for registered
                    UCA-owned processes or explicitly owned handles.
                  </li>
                </ul>
              </article>
              <article className="card">
                <h3>Knowledge available</h3>
                <p className="largeNumber">{documents.length}</p>
                <p>Uploaded text documents currently indexed for retrieval.</p>
                <button className="textButton" onClick={() => setView("search")}>Search evidence →</button>
              </article>
            </div>
          </section>
        )}

        {view === "requirements" && (
          <section className="grid2 alignStart">
            <article className="card formCard">
              <div className="sectionHeading">
                <div><span className="kicker">Alignment</span><h2>Clarify the request</h2></div>
                <StatusPill status={requirement?.contract.status} />
              </div>
              <Field label="Alignment ID" value={alignmentId} onChange={setAlignmentId} />
              <Field label="Title" value={requirementTitle} onChange={setRequirementTitle} />
              <TextArea
                label="What should be delivered?"
                value={requirementObjective}
                onChange={setRequirementObjective}
                rows={8}
                placeholder="Describe the feature, problem, constraints and expected outcome."
              />
              <button className="primary" onClick={analyzeRequirement} disabled={busy || !requirementObjective.trim()}>
                {requirement ? "Re-analyze" : "Analyze requirement"}
              </button>
            </article>
            <article className="card">
              <div className="sectionHeading">
                <div><span className="kicker">Contract</span><h2>Decision-changing questions</h2></div>
                {requirement && <span className="mono">v{requirement.contract.version}</span>}
              </div>
              {!requirement && <Empty text="Analyze a request to build a versioned requirement contract." />}
              {requirement && unresolved.length === 0 && (
                <div className="successBlock">No unresolved blocking or material decisions.</div>
              )}
              {unresolved.map((item) => (
                <div className="question" key={item.decision_key}>
                  <div className="questionHeader">
                    <StatusPill status={item.severity} />
                    <code>{item.decision_key}</code>
                  </div>
                  <strong>{item.question}</strong>
                  <p>{item.rationale}</p>
                  {item.options.length > 0 ? (
                    <select
                      value={answers[item.decision_key] ?? ""}
                      onChange={(event) =>
                        setAnswers((current) => ({ ...current, [item.decision_key]: event.target.value }))
                      }
                    >
                      <option value="">Choose an answer…</option>
                      {item.options.map((option) => <option key={option}>{option}</option>)}
                    </select>
                  ) : (
                    <input
                      value={answers[item.decision_key] ?? ""}
                      onChange={(event) =>
                        setAnswers((current) => ({ ...current, [item.decision_key]: event.target.value }))
                      }
                      placeholder="Provide a concrete decision"
                    />
                  )}
                </div>
              ))}
              {requirement?.contract.status === "ready_for_approval" && (
                <button className="primary" onClick={approveRequirement} disabled={busy}>
                  Approve & freeze requirement
                </button>
              )}
              {requirement?.contract.status === "approved" && (
                <>
                  <div className="successBlock">Requirement frozen</div>
                  <div className="hashBox">{requirement.requirement_hash}</div>
                  <button className="secondary" onClick={() => setView("program")}>Create delivery program →</button>
                </>
              )}
            </article>
          </section>
        )}

        {view === "program" && (
          <section className="stack">
            <div className="grid2 alignStart">
              <article className="card formCard">
                <span className="kicker">Program orchestration</span>
                <h2>Plan or recover a large change</h2>
                <Field label="Program ID" value={programId} onChange={setProgramId} />
                <p className="muted">
                  Loading and refreshing are read-only. Planning is bound to an approved
                  requirement hash and never implies phase execution.
                </p>
                <div className="controlRow">
                  <button
                    className="secondary"
                    onClick={loadProgram}
                    disabled={busy || !programId.trim()}
                  >
                    Load existing program
                  </button>
                  {!program && (
                    <button
                      className="primary"
                      onClick={createProgram}
                      disabled={busy || requirement?.contract.status !== "approved"}
                    >
                      Create phase plan
                    </button>
                  )}
                </div>
                {program?.status === "awaiting_approval" && (
                  <button
                    className="primary"
                    onClick={() =>
                      void perform(
                        () =>
                          attachExecutionState(
                            api.approveProgram(program.program_id, program.plan_hash),
                          ),
                        applyProgramState,
                        "Program approved.",
                      )
                    }
                    disabled={busy}
                  >
                    Approve program plan
                  </button>
                )}
                {program && (
                  <div className="controlRow">
                    <button
                      className="secondary"
                      onClick={() => controlProgram("pause")}
                      disabled={busy}
                    >
                      Pause
                    </button>
                    <button
                      className="secondary"
                      onClick={() => controlProgram("resume")}
                      disabled={busy}
                    >
                      Resume
                    </button>
                    <button
                      className="dangerGhost"
                      onClick={() => controlProgram("cancel")}
                      disabled={busy}
                    >
                      Cancel
                    </button>
                  </div>
                )}
              </article>
              <article className="card">
                <div className="sectionHeading">
                  <div>
                    <span className="kicker">Phase map</span>
                    <h2>{program?.plan.title ?? "No program yet"}</h2>
                  </div>
                  <StatusPill status={program?.status} />
                </div>
                {!program && (
                  <Empty text="Approve a requirement and create a plan, or load an existing Program ID." />
                )}
                {program?.phases.map((phase, index) => (
                  <div className="phase" key={phase.phase_id}>
                    <div className="phaseIndex">
                      {String(index + 1).padStart(2, "0")}
                    </div>
                    <div className="phaseBody">
                      <div className="phaseTitle">
                        <strong>{phase.title}</strong>
                        <StatusPill status={phase.status} />
                      </div>
                      <code>{phase.phase_id}</code>
                      <p>Depends on: {phase.dependencies.join(", ") || "none"}</p>
                    </div>
                  </div>
                ))}
                {program && <div className="hashBox">Plan hash: {program.plan_hash}</div>}
              </article>
            </div>

            <article className="card executionPanel">
              <div className="sectionHeading">
                <div>
                  <span className="kicker">Discovered Safe execution</span>
                  <h2>Explicit Program checkpoints</h2>
                </div>
                <StatusPill
                  status={
                    programExecution?.runtime.busy
                      ? programExecution.runtime.status
                      : programExecution?.program_status
                  }
                />
              </div>
              {!program && (
                <Empty text="Load or create a program before inspecting execution state." />
              )}
              {program && !programExecution && (
                <Empty text="Load the program to read its persisted execution bindings." />
              )}
              {programExecution && (
                <>
                  <div className="executionFacts">
                    <div>
                      <span>Loaded program</span>
                      <strong>{programExecution.program_id}</strong>
                    </div>
                    <div>
                      <span>Runtime action</span>
                      <strong>{programExecution.runtime.action || "none"}</strong>
                    </div>
                    <div>
                      <span>Runtime status</span>
                      <strong>{programExecution.runtime.status}</strong>
                    </div>
                    <div>
                      <span>Persisted bindings</span>
                      <strong>{programExecution.bindings.length}</strong>
                    </div>
                  </div>

                  {programExecution.runtime.recovered_pending && (
                    <div className="approvalBox">
                      <strong>Recovered pending execution</strong>
                      <p>
                        The API recovered a durable binding after restart. No provider work was
                        started automatically. Review the binding and make an explicit decision.
                      </p>
                    </div>
                  )}

                  {programExecution.runtime.error && (
                    <div className="notice error">
                      {programExecution.runtime.error_type}: {programExecution.runtime.error}
                    </div>
                  )}

                  <div className="grid2 executionInputs">
                    <Field
                      label="Repository URL or approved local path"
                      value={repository}
                      onChange={setRepository}
                    />
                    <Field label="Branch / ref" value={ref} onChange={setRef} />
                    <Field
                      label="Trusted test profiles (comma separated)"
                      value={testProfiles}
                      onChange={setTestProfiles}
                    />
                    <div className="executionActions">
                      <button
                        className="secondary"
                        onClick={refreshProgram}
                        disabled={busy}
                      >
                        Refresh status
                      </button>
                      <button
                        className="primary"
                        onClick={startProgramExecution}
                        disabled={
                          busy ||
                          !programExecutionCanStart ||
                          !repository.trim() ||
                          !ref.trim() ||
                          !testProfiles.trim()
                        }
                      >
                        Start next unit
                      </button>
                    </div>
                  </div>
                  <details>
                    <summary>Trusted execution policy</summary>
                    <TextArea
                      label="Trusted policy JSON"
                      value={policyText}
                      onChange={setPolicyText}
                      rows={10}
                      mono
                    />
                  </details>

                  {activeProgramExecution && programExecutionCanContinue && (
                    <div className="approvalBox">
                      <strong>Explicit Safe checkpoint decision required</strong>
                      <p>
                        Task <code>{activeProgramExecution.task_id}</code> is bound to phase{" "}
                        <code>{activeProgramExecution.phase_id}</code>
                        {activeProgramExecution.slice_id
                          ? ` / slice ${activeProgramExecution.slice_id}`
                          : ""}
                        . Approve or reject this exact checkpoint; refresh never continues it.
                      </p>
                      <div className="controlRow">
                        <button
                          className="primary"
                          onClick={() => continueProgramExecution(true)}
                          disabled={busy}
                        >
                          Approve & continue
                        </button>
                        <button
                          className="dangerGhost"
                          onClick={() => continueProgramExecution(false)}
                          disabled={busy}
                        >
                          Reject checkpoint
                        </button>
                      </div>
                    </div>
                  )}

                  {programExecution.runtime.requires_explicit_action &&
                    activeProgramExecution &&
                    !programExecutionCanContinue && (
                      <div className="notice error">
                        This binding requires explicit action, but the Program or task control
                        state currently prevents continuation. Resume or refresh the Program
                        before deciding.
                      </div>
                    )}

                  <div className="executionList">
                    {programExecution.bindings.length === 0 && (
                      <Empty text="No Program execution unit has been started." />
                    )}
                    {programExecution.bindings.map((binding) => (
                      <div className="executionRow" key={binding.task_id}>
                        <div className="executionHeading">
                          <div>
                            <strong>{binding.phase_id}</strong>
                            <span>
                              {binding.slice_id ? `Slice ${binding.slice_id}` : "Phase unit"}
                            </span>
                          </div>
                          <StatusPill status={binding.status} />
                        </div>
                        <div className="executionMeta">
                          <code>{binding.task_id}</code>
                          <span>Safe: {binding.safe_status || "not reported"}</span>
                          <span>Control: {binding.control?.state ?? "not reported"}</span>
                        </div>
                        {binding.control?.reason && (
                          <p className="muted">Control reason: {binding.control.reason}</p>
                        )}
                        {binding.cancellation_report && (
                          <CancellationReportPanel report={binding.cancellation_report} />
                        )}
                        {binding.remote_operation && (
                          <RemoteOperationPanel
                            operation={binding.remote_operation}
                            blocked={busy || programExecution.runtime.busy}
                            onObserve={() =>
                              reconcileProgramRemoteOperation(binding.task_id, "observe")
                            }
                            onCancel={() =>
                              reconcileProgramRemoteOperation(binding.task_id, "cancel")
                            }
                          />
                        )}
                        {binding.phase_report_ref && (
                          <div className="artifactRef">
                            Phase report: <code>{binding.phase_report_ref}</code>
                          </div>
                        )}
                        {binding.accepted_evidence_ref && (
                          <div className="artifactRef">
                            Accepted prior-phase evidence: {" "}
                            <code>{binding.accepted_evidence_ref}</code>
                            <br />
                            Evidence SHA256: <code>{binding.accepted_evidence_hash}</code>
                            <br />
                            Immutable Base SHA: <code>{binding.expected_base_sha}</code>
                          </div>
                        )}
                        {binding.error_ref && (
                          <div className="artifactRef errorText">
                            Error evidence: <code>{binding.error_ref}</code>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>

                  <details>
                    <summary>Technical execution state</summary>
                    <pre className="jsonPreview">
                      {JSON.stringify(programExecution, null, 2)}
                    </pre>
                  </details>
                </>
              )}
            </article>
          </section>
        )}

        {view === "documents" && (
          <section className="grid2 alignStart">
            <article className="card formCard">
              <span className="kicker">Context documents</span>
              <h2>Attach text evidence</h2>
              <label className="fileDrop">
                <input
                  type="file"
                  accept=".txt,.md,.log,.json,.yaml,.yml,.xml,.csv,.sql,.py,.ts,.tsx,.js,.jsx,.java,.cs,.sh,.ps1,.tf,.properties,.ini,.conf"
                  onChange={(event) => void readSelectedFile(event.target.files?.[0])}
                />
                <strong>Choose a text file</strong>
                <span>Requirement, architecture, contract, log, config or reference.</span>
              </label>
              <Field label="Document ID" value={documentId} onChange={setDocumentId} />
              <Field label="Filename" value={documentFilename} onChange={setDocumentFilename} />
              <div className="fieldRow">
                <SelectField label="Role" value={documentRole} onChange={setDocumentRole} options={[
                  "requirement", "architecture", "technical_contract", "error_log", "config_sample", "reference", "user_instruction",
                ]} />
                <SelectField label="Scope" value={documentScope} onChange={setDocumentScope} options={["program", "phase", "task"]} />
              </div>
              <Field label="Scope ID" value={documentScopeId} onChange={setDocumentScopeId} />
              <TextArea label="Text content" value={documentContent} onChange={setDocumentContent} rows={7} />
              <button className="primary" onClick={uploadDocument} disabled={busy || !documentContent}>Upload text context</button>
              <p className="muted">Files are validated as UTF-8 text, scanned for credential material and stored immutably. They are never executed.</p>
            </article>
            <article className="card">
              <div className="sectionHeading"><div><span className="kicker">Indexed context</span><h2>Documents</h2></div><span>{documents.length}</span></div>
              {documents.length === 0 && <Empty text="No documents uploaded yet." />}
              {documents.map((document) => (
                <div className="documentRow" key={document.document_id}>
                  <div><strong>{document.filename}</strong><span>{document.role} · {document.scope}:{document.scope_id}</span></div>
                  <code>{document.sha256.slice(0, 12)}</code>
                </div>
              ))}
            </article>
          </section>
        )}

        {view === "search" && (
          <section className="stack">
            <article className="card searchBar">
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                onKeyDown={(event) => event.key === "Enter" && runSearch()}
                placeholder="Search code, uploaded documents, decisions and phase reports…"
              />
              <button className="primary" onClick={runSearch} disabled={busy || !query.trim()}>Search</button>
            </article>
            <div className="searchResults">
              {hits.length === 0 && <Empty text="Search returns ranked code and project evidence from the shared backend index." />}
              {hits.map((hit) => (
                <article className="card resultCard" key={hit.record_id}>
                  <div className="resultMeta"><StatusPill status={hit.source_type} /><code>{hit.path}</code><span>{hit.score.toFixed(1)}</span></div>
                  <pre>{hit.excerpt}</pre>
                </article>
              ))}
            </div>
          </section>
        )}

        {view === "task" && (
          <section className="grid2 alignStart">
            <article className="card formCard">
              <span className="kicker">Solution-level Safe Mode</span>
              <h2>Discover the right components first</h2>
              <div className="recoveryLoad">
                <Field
                  label="Existing task ID"
                  value={taskLookupId}
                  onChange={setTaskLookupId}
                />
                <button
                  className="secondary"
                  onClick={loadTask}
                  disabled={busy || !taskLookupId.trim()}
                >
                  Load existing task
                </button>
              </div>
              <p className="muted">
                Loading an existing task is read-only and never reconciles a remote operation.
              </p>
              <Field label="Repository URL or approved local path" value={repository} onChange={setRepository} />
              <Field label="Branch / ref" value={ref} onChange={setRef} />
              <Field label="Task title" value={taskTitle} onChange={setTaskTitle} />
              <TextArea label="Objective" value={taskObjective} onChange={setTaskObjective} rows={7} />
              <Field label="Trusted test profiles (comma separated)" value={testProfiles} onChange={setTestProfiles} />
              <TextArea label="Trusted policy JSON" value={policyText} onChange={setPolicyText} rows={10} mono />
              <button className="primary" onClick={startTask} disabled={busy || !repository || !taskObjective}>
                Analyze project & propose scope
              </button>
            </article>
            <article className="card">
              <div className="sectionHeading">
                <div><span className="kicker">Execution</span><h2>{task?.title ?? "No active task"}</h2></div>
                <StatusPill status={task?.control?.state ?? task?.status} />
              </div>
              {!task && <Empty text="Start a task. Discovery runs read-only before any scope approval." />}
              {task && (
                <>
                  <div className="taskFacts">
                    <div><span>Task</span><strong>{task.task_id}</strong></div>
                    <div><span>Agent status</span><strong>{task.status}</strong></div>
                    <div><span>Control state</span><strong>{task.control?.state ?? "pending"}</strong></div>
                  </div>
                  <div className="controlRow">
                    <button className="secondary" onClick={refreshTask} disabled={busy}>Refresh status</button>
                    <button className="secondary" onClick={() => controlTask("pause")} disabled={busy}>Pause</button>
                    <button className="secondary" onClick={() => controlTask("resume")} disabled={busy}>Resume</button>
                    <button className="dangerGhost" onClick={() => controlTask("cancel")} disabled={busy}>Stop</button>
                  </div>
                  {task.cancellation_report && (
                    <CancellationReportPanel report={task.cancellation_report} />
                  )}
                  {task.remote_operation && (
                    <RemoteOperationPanel
                      operation={task.remote_operation}
                      blocked={busy || Boolean(task.busy)}
                      onObserve={() => reconcileTaskRemoteOperation("observe")}
                      onCancel={() => reconcileTaskRemoteOperation("cancel")}
                    />
                  )}
                  {canApproveScope(task) && (
                    <div className="approvalBox">
                      <strong>Scope approval required</strong>
                      <p>Implementation has not been authorized. Review discovery evidence before continuing.</p>
                      <div className="controlRow">
                        <button className="primary" onClick={() => scopeDecision(true)} disabled={busy}>Approve scope</button>
                        <button className="dangerGhost" onClick={() => scopeDecision(false)} disabled={busy}>Reject</button>
                      </div>
                    </div>
                  )}
                  {task.error && <div className="notice error">{task.error_type}: {task.error}</div>}
                  <details>
                    <summary>Technical task state</summary>
                    <pre className="jsonPreview">{JSON.stringify(task.result ?? task, null, 2)}</pre>
                  </details>
                </>
              )}
            </article>
          </section>
        )}
      </main>
    </div>
  );
}

function CancellationReportPanel({ report }: { report: CancellationReport }) {
  const evidence = cancellationEvidencePresentation(report);
  const operationKinds = report.active_operation_kinds.join(", ") || "none";

  return (
    <section className="cancellationEvidence">
      <div className="cancellationEvidenceHeader">
        <div>
          <span className="kicker">Durable cancellation evidence</span>
          <h3>{evidence.label}</h3>
        </div>
        <span className={`status ${evidence.tone}`}>recorded</span>
      </div>
      <p className="cancellationSummary">{evidence.summary}</p>
      <div className="cancellationMeta">
        <span>Task: <code>{report.task_id}</code></span>
        <span>Active kinds: <code>{operationKinds}</code></span>
      </div>
      <p className="cancellationReason">
        <strong>Reason:</strong> {report.reason || "Not provided"}
      </p>
      <div className="cancellationMetrics">
        <EvidenceMetric label="Owned processes observed" value={report.owned_processes_observed} />
        <EvidenceMetric
          label="Owned handles observed"
          value={report.owned_cancellable_operations_observed}
        />
        <EvidenceMetric label="Terminate requests" value={report.terminate_requests} />
        <EvidenceMetric
          label="Handle cancel requests"
          value={report.cancellable_operation_cancel_requests}
        />
        <EvidenceMetric label="Kill requests" value={report.kill_requests} />
        <EvidenceMetric label="Processes still active" value={report.processes_still_active} />
        <EvidenceMetric
          label="Handles still active"
          value={report.cancellable_operations_still_active}
        />
        <EvidenceMetric
          label="Cooperative fallback"
          value={report.cooperative_fallback ? "yes" : "no"}
        />
      </div>
      <p className="cancellationBoundaryNote">
        Pause is safe-boundary only. Cancel prevents new work and requests active termination only
        for registered UCA-owned processes and explicitly owned handles; this report records the
        observed bounded outcome.
      </p>
    </section>
  );
}

function RemoteOperationPanel({
  operation,
  blocked,
  onObserve,
  onCancel,
}: {
  operation: RemoteOperationSnapshot;
  blocked: boolean;
  onObserve: () => void;
  onCancel: () => void;
}) {
  const presentation = remoteOperationPresentation(operation);
  const canReconcile = canReconcileRemoteOperation(operation, blocked);

  return (
    <section className="remoteOperationEvidence">
      <div className="cancellationEvidenceHeader">
        <div>
          <span className="kicker">Redacted remote-operation evidence</span>
          <h3>{presentation.label}</h3>
        </div>
        <span className={`status ${presentation.tone}`}>{operation.state}</span>
      </div>
      <p className="cancellationSummary">{presentation.summary}</p>
      <div className="remoteOperationMeta">
        <span>Task: <code>{operation.task_id}</code></span>
        <span>Transport: <code>{operation.transport}</code></span>
        <span>Provider status: <code>{operation.last_status}</code></span>
        <span>Last action: <code>{operation.last_action ?? "none"}</code></span>
        <span>Updated: <code>{operation.updated_at}</code></span>
        {operation.base_sha && <span>Immutable Base SHA: <code>{operation.base_sha}</code></span>}
      </div>
      <div className="remoteOperationRefs">
        <span>Endpoint scope hash</span>
        <code>{operation.transport_scope}</code>
        <span>Operation reference hash</span>
        <code>{operation.operation_ref}</code>
      </div>
      <div className="cancellationMetrics">
        <EvidenceMetric label="Revision" value={operation.revision} />
        <EvidenceMetric
          label="Reconciliation attempts"
          value={operation.reconciliation_attempts}
        />
        <EvidenceMetric label="Cancel requests" value={operation.cancel_requests} />
        <EvidenceMetric
          label="Cancellation intent"
          value={operation.cancellation_requested ? "recorded" : "not recorded"}
        />
      </div>
      <div className="controlRow remoteOperationActions">
        <button className="secondary" onClick={onObserve} disabled={!canReconcile}>
          Observe remote operation
        </button>
        <button className="dangerGhost" onClick={onCancel} disabled={!canReconcile}>
          Request remote cancellation
        </button>
      </div>
      {operation.state === "active" && !operation.requires_explicit_action && (
        <p className="remoteOperationBlocked">
          Explicit reconciliation is unavailable while the local task worker is active.
        </p>
      )}
      <p className="cancellationBoundaryNote">
        Loading, refresh, and polling are read-only. Observe makes one bounded provider status
        request. Cancel records durable intent before requesting remote cancellation. Neither
        action resumes the graph, consumes output, or advances a Program phase.
      </p>
    </section>
  );
}

function EvidenceMetric({ label, value }: { label: string; value: number | string }) {
  return <div><span>{label}</span><strong>{value}</strong></div>;
}

function StatusPill({ status }: { status?: string }) {
  return <span className={`status ${statusTone(status)}`}>{status?.replaceAll("_", " ") ?? "not started"}</span>;
}

function Metric({ label, value }: { label: string; value: string }) {
  return <article className="metric"><span>{label}</span><strong>{value.replaceAll("_", " ")}</strong></article>;
}

function Empty({ text }: { text: string }) {
  return <div className="empty">{text}</div>;
}

function Field({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return <label className="field"><span>{label}</span><input value={value} onChange={(event) => onChange(event.target.value)} /></label>;
}

function SelectField({ label, value, onChange, options }: { label: string; value: string; onChange: (value: string) => void; options: string[] }) {
  return <label className="field"><span>{label}</span><select value={value} onChange={(event) => onChange(event.target.value)}>{options.map((option) => <option key={option}>{option}</option>)}</select></label>;
}

function TextArea({ label, value, onChange, rows, placeholder, mono = false }: { label: string; value: string; onChange: (value: string) => void; rows: number; placeholder?: string; mono?: boolean }) {
  return <label className="field"><span>{label}</span><textarea className={mono ? "monoInput" : ""} value={value} rows={rows} placeholder={placeholder} onChange={(event) => onChange(event.target.value)} /></label>;
}
