import { useEffect, useMemo, useState } from "react";

import { api } from "./api";
import type {
  ContextDocument,
  ProgramSnapshot,
  RequirementResult,
  SearchHit,
  TaskSnapshot,
} from "./types";
import { canApproveScope, phaseProgress, statusTone, unresolvedClarifications } from "./viewModels";

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
      api.task(task.task_id).then(setTask).catch(() => undefined);
    }, 1600);
    return () => window.clearInterval(timer);
  }, [task?.task_id, task?.status]);

  const unresolved = useMemo(
    () => unresolvedClarifications(requirement?.contract),
    [requirement],
  );
  const progress = phaseProgress(program);

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

  function createProgram() {
    if (!requirement || requirement.contract.status !== "approved") return;
    void perform(
      () =>
        api.createProgram({
          program_id: programId,
          requirement: requirement.contract,
          requirement_hash: requirement.requirement_hash,
        }),
      setProgram,
      "Program plan created and awaiting approval.",
    );
  }

  function controlProgram(action: "pause" | "resume" | "cancel") {
    if (!program) return;
    void perform(
      () => api.programControl(program.program_id, action, "Operator action from Control Center"),
      setProgram,
      `Program ${action} applied.`,
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
      setTask,
      "Safe task queued. Discovery has no write authority.",
    );
  }

  function controlTask(action: "pause" | "resume" | "cancel") {
    if (!task) return;
    void perform(
      () => api.taskControl(task.task_id, action, "Operator action from Control Center"),
      setTask,
      `Task ${action} requested.`,
    );
  }

  function scopeDecision(approved: boolean) {
    if (!task) return;
    void perform(
      () => api.scopeDecision(task.task_id, approved),
      setTask,
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
                  <li>Pause and cancel are checked at safe boundaries.</li>
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
          <section className="grid2 alignStart">
            <article className="card formCard">
              <span className="kicker">Program orchestration</span>
              <h2>Plan a large change in phases</h2>
              <Field label="Program ID" value={programId} onChange={setProgramId} />
              <p className="muted">Planning is bound to the approved requirement hash. No phase execution is implied by planning.</p>
              {!program && (
                <button
                  className="primary"
                  onClick={createProgram}
                  disabled={busy || requirement?.contract.status !== "approved"}
                >
                  Create phase plan
                </button>
              )}
              {program?.status === "awaiting_approval" && (
                <button
                  className="primary"
                  onClick={() =>
                    void perform(
                      () => api.approveProgram(program.program_id, program.plan_hash),
                      setProgram,
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
                  <button className="secondary" onClick={() => controlProgram("pause")} disabled={busy}>Pause</button>
                  <button className="secondary" onClick={() => controlProgram("resume")} disabled={busy}>Resume</button>
                  <button className="dangerGhost" onClick={() => controlProgram("cancel")} disabled={busy}>Cancel</button>
                </div>
              )}
            </article>
            <article className="card">
              <div className="sectionHeading">
                <div><span className="kicker">Phase map</span><h2>{program?.plan.title ?? "No program yet"}</h2></div>
                <StatusPill status={program?.status} />
              </div>
              {!program && <Empty text="Approve a requirement, then create a program plan." />}
              {program?.phases.map((phase, index) => (
                <div className="phase" key={phase.phase_id}>
                  <div className="phaseIndex">{String(index + 1).padStart(2, "0")}</div>
                  <div className="phaseBody">
                    <div className="phaseTitle"><strong>{phase.title}</strong><StatusPill status={phase.status} /></div>
                    <code>{phase.phase_id}</code>
                    <p>Depends on: {phase.dependencies.join(", ") || "none"}</p>
                  </div>
                </div>
              ))}
              {program && <div className="hashBox">Plan hash: {program.plan_hash}</div>}
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
                    <button className="secondary" onClick={() => controlTask("pause")} disabled={busy}>Pause</button>
                    <button className="secondary" onClick={() => controlTask("resume")} disabled={busy}>Resume</button>
                    <button className="dangerGhost" onClick={() => controlTask("cancel")} disabled={busy}>Stop</button>
                  </div>
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
