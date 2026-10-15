import { useCallback, useEffect, useRef, useState } from "react";
import { api, errorMessage } from "../api";
import type { DocumentSummary, ImportInput, JobView } from "../contracts";
import { ErrorNotice } from "./StatusNotice";
import { JobStatus } from "./JobStatus";
export function DocumentAdmin({
  documents,
  changed,
}: {
  documents: DocumentSummary[];
  changed: () => void;
}) {
  const [selected, setSelected] = useState<DocumentSummary | null>(null);
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState("");
  const [label, setLabel] = useState("v1");
  const [date, setDate] = useState("2026-10-15");
  const [role, setRole] = useState<"" | "reader" | "maintainer">("");
  const [text, setText] = useState("");
  const [job, setJob] = useState("");
  const [pending, setPending] = useState(false);
  const [submitted, setSubmitted] = useState<{
    input: ImportInput;
    target: DocumentSummary | null;
  } | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [deleting, setDeleting] = useState<DocumentSummary | null>(null);
  const dialog = useRef<HTMLDialogElement>(null);
  const opener = useRef<HTMLButtonElement | null>(null);
  const load = useRef<AbortController | null>(null);
  useEffect(() => () => load.current?.abort(), []);
  useEffect(() => {
    if (deleting) dialog.current?.showModal();
    else if (dialog.current?.open) {
      dialog.current.close();
      requestAnimationFrame(() => {
        if (opener.current?.isConnected) opener.current.focus();
        else document.getElementById("admin-heading")?.focus();
      });
    }
  }, [deleting]);
  const settled = useCallback(
    (value: JobView) => {
      setPending(false);
      if (value.status === "succeeded") setSubmitted(null);
      changed();
    },
    [changed],
  );
  function recover() {
    if (!submitted || pending) return;
    load.current?.abort();
    setSelected(submitted.target);
    setTitle(submitted.input.title);
    setLabel(submitted.input.label);
    setDate(submitted.input.effective_date);
    setRole(submitted.input.min_role ?? "reader");
    setText(submitted.input.markdown);
    setEditing(true);
    requestAnimationFrame(() => document.getElementById("doc-title")?.focus());
  }
  function fresh() {
    if (pending) return;
    load.current?.abort();
    setSelected(null);
    setEditing(true);
    setTitle("");
    setLabel("v1");
    setRole("");
    setText("");
    setError("");
  }
  async function edit(doc: DocumentSummary) {
    load.current?.abort();
    const controller = new AbortController();
    load.current = controller;
    setError("");
    setBusy(true);
    try {
      const source = await api.document(doc.id, controller.signal);
      if (controller.signal.aborted) return;
      setSelected(doc);
      setTitle(source.title);
      setLabel("");
      setRole("");
      setText(source.text);
      setEditing(true);
    } catch (e: unknown) {
      if (!controller.signal.aborted) setError(errorMessage(e));
    } finally {
      if (!controller.signal.aborted) setBusy(false);
    }
  }
  async function save() {
    if (role === "" || pending || busy) return;
    setBusy(true);
    setError("");
    const input: ImportInput = {
      title,
      label,
      min_role: role,
      effective_date: date,
      markdown: text,
    };
    try {
      const value = selected
        ? await api.replace(selected.id, {
            ...input,
            expected_revision: selected.revision,
          })
        : await api.import(input);
      setSubmitted({ input, target: selected });
      setPending(true);
      setJob(value.job_id);
      setEditing(false);
      setSelected(null);
    } catch (e: unknown) {
      setError(errorMessage(e));
    } finally {
      setBusy(false);
    }
  }
  async function remove() {
    if (!deleting) return;
    setBusy(true);
    setError("");
    try {
      await api.remove(deleting.id, deleting.revision);
      setDeleting(null);
      if (submitted?.target?.id === deleting.id) {
        setSubmitted(null);
        setJob("");
      }
      setEditing(false);
      setSelected(null);
      changed();
    } catch (e: unknown) {
      setDeleting(null);
      setError(errorMessage(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="admin panel">
      <div className="section-header">
        <div>
          <h2 id="admin-heading" tabIndex={-1}>
            Document maintenance
          </h2>
          <p className="meta">
            Changes publish atomically. Earlier citation links become
            unavailable.
          </p>
        </div>
        <div className="actions">
          <button
            className="secondary"
            disabled={busy || pending}
            onClick={fresh}
          >
            New document
          </button>
          <button
            className="secondary"
            disabled={busy || pending}
            onClick={() => {
              setBusy(true);
              setError("");
              void api
                .rebuild()
                .then((value) => {
                  setSubmitted(null);
                  setPending(true);
                  setJob(value.job_id);
                })
                .catch((e: unknown) => setError(errorMessage(e)))
                .finally(() => setBusy(false));
            }}
          >
            Rebuild index
          </button>
        </div>
      </div>
      {error && <ErrorNotice message={error} />}
      <ul className="document-list">
        {documents.map((doc) => (
          <li key={doc.id}>
            <div>
              <strong>{doc.title}</strong>
              <p className="meta">
                {doc.version_label} / {doc.effective_date}
              </p>
            </div>
            <div className="actions">
              <button
                className="secondary"
                disabled={busy || pending}
                aria-label={"Replace " + doc.title}
                onClick={() => {
                  void edit(doc);
                }}
              >
                Replace
              </button>
              <button
                className="danger secondary"
                disabled={busy || pending}
                aria-label={"Delete " + doc.title}
                onClick={(event) => {
                  opener.current = event.currentTarget;
                  setDeleting(doc);
                }}
              >
                Delete
              </button>
            </div>
          </li>
        ))}
      </ul>
      {editing && (
        <form
          className="version-form"
          onSubmit={(event) => {
            event.preventDefault();
            void save();
          }}
        >
          <h3>
            {selected
              ? "Replace " + selected.title
              : "Import a fictional manual"}
          </h3>
          <label htmlFor="doc-title">Document title</label>
          <input
            id="doc-title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            maxLength={120}
            required
          />
          <div className="form-row">
            <div>
              <label htmlFor="version-label">New version label</label>
              <input
                id="version-label"
                value={label}
                onChange={(e) => setLabel(e.target.value)}
                maxLength={40}
                required
              />
            </div>
            <div>
              <label htmlFor="effective-date">Effective date</label>
              <input
                id="effective-date"
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                required
              />
            </div>
          </div>
          <label htmlFor="visibility">Minimum access role</label>
          <select
            id="visibility"
            value={role}
            onChange={(e) => setRole(e.target.value as typeof role)}
            required
            aria-describedby="visibility-help"
          >
            <option value="">Choose visibility</option>
            <option value="reader">Reader (both identities)</option>
            <option value="maintainer">Maintainer only</option>
          </select>
          <p id="visibility-help" className="meta">
            Choose explicitly for each version. Changing this changes who can
            retrieve the document.
          </p>
          <label htmlFor="markdown">Markdown source</label>
          <textarea
            id="markdown"
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={10}
            required
            maxLength={262144}
            aria-describedby="markdown-help"
          />
          <p id="markdown-help" className="meta">
            Start with a heading. Plain Markdown, maximum 256 KiB. Source is
            displayed as text.
          </p>
          <div className="actions">
            <button disabled={busy || pending}>
              {busy
                ? "Submitting..."
                : selected
                  ? "Queue replacement"
                  : "Queue import"}
            </button>
            <button
              type="button"
              className="secondary"
              disabled={busy || pending}
              onClick={() => setEditing(false)}
            >
              Close editor
            </button>
          </div>
        </form>
      )}
      {job && (
        <JobStatus
          key={job}
          id={job}
          settled={settled}
          retry={submitted ? recover : undefined}
        />
      )}
      {pending && (
        <p className="meta">
          Finish or cancel the indexing job before submitting another change.
          Its status remains available when you return from a citation.
        </p>
      )}
      <dialog
        ref={dialog}
        aria-labelledby="delete-title"
        aria-describedby="delete-description"
        onCancel={(event) => {
          if (busy) event.preventDefault();
          else setDeleting(null);
        }}
      >
        <h2 id="delete-title">Delete {deleting?.title}?</h2>
        <p id="delete-description">
          This removes every stored source version and invalidates its
          citations. It also cancels pending replacement jobs.
        </p>
        <div className="actions">
          <button
            className="secondary"
            disabled={busy || pending}
            onClick={() => setDeleting(null)}
          >
            Keep document
          </button>
          <button
            className="danger"
            disabled={busy || pending}
            onClick={() => {
              void remove();
            }}
          >
            {busy ? "Deleting..." : "Confirm delete"}
          </button>
        </div>
      </dialog>
    </section>
  );
}
