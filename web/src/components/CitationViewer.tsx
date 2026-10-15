import { useEffect, useRef, useState } from "react";
import { api, errorMessage } from "../api";
import type { CitationView } from "../contracts";
import { ErrorNotice } from "./StatusNotice";
export function CitationViewer({ id, back }: { id: string; back: () => void }) {
  const [source, setSource] = useState<CitationView | null>(null);
  const [error, setError] = useState("");
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => {
    const controller = new AbortController();
    setSource(null);
    setError("");
    api
      .citation(id, controller.signal)
      .then(setSource)
      .catch((e: unknown) => {
        if (!controller.signal.aborted) setError(errorMessage(e));
      });
    return () => controller.abort();
  }, [id]);
  useEffect(() => {
    if (source) heading.current?.focus();
  }, [source]);
  return (
    <main className="source-page panel">
      <button className="secondary" onClick={back}>
        Back to answer
      </button>
      {error ? (
        <ErrorNotice message={error} />
      ) : source ? (
        <>
          <h2 ref={heading} tabIndex={-1}>
            {source.title}
          </h2>
          <p>
            {source.version_label} / {source.effective_date}
          </p>
          <p className="meta">
            Current source passage. The marked text is the cited quotation.
          </p>
          <pre className="source-text">
            {source.section_text.slice(0, source.highlight_start)}
            <mark aria-label="Cited quotation">
              {source.section_text.slice(
                source.highlight_start,
                source.highlight_end,
              )}
            </mark>
            {source.section_text.slice(source.highlight_end)}
          </pre>
          <p className="meta id">Version {source.version_id}</p>
        </>
      ) : (
        <p role="status">Opening the current passage...</p>
      )}
    </main>
  );
}
