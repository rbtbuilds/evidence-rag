import { useCallback, useEffect, useRef, useState } from "react";
import { api, errorMessage } from "../api";
import type { JobView } from "../contracts";
import { ErrorNotice } from "./StatusNotice";
export function JobStatus({
  id,
  settled,
  retry,
}: {
  id: string;
  settled: (job: JobView) => void;
  retry?: (() => void) | undefined;
}) {
  const [job, setJob] = useState<JobView | null>(null);
  const [error, setError] = useState("");
  const [refresh, setRefresh] = useState(0);
  const completed = useRef("");
  const receive = useCallback(
    (value: JobView) => {
      setJob(value);
      if (
        !["queued", "running"].includes(value.status) &&
        completed.current !== id
      ) {
        completed.current = id;
        settled(value);
      }
    },
    [id, settled],
  );
  useEffect(() => {
    const controller = new AbortController();
    let timer: ReturnType<typeof setTimeout> | undefined;
    let reads = 0;
    async function poll() {
      try {
        const value = await api.job(id, controller.signal);
        if (controller.signal.aborted) return;
        receive(value);
        setError("");
        if (["queued", "running"].includes(value.status)) {
          if (++reads < 600)
            timer = setTimeout(() => {
              void poll();
            }, 1000);
        }
      } catch (e: unknown) {
        if (!controller.signal.aborted) setError(errorMessage(e));
      }
    }
    void poll();
    return () => {
      controller.abort();
      clearTimeout(timer);
    };
  }, [id, refresh, receive]);
  return (
    <section className="job-status" aria-label="Indexing job">
      <h3>Indexing job</h3>
      <p role="status">
        {job
          ? `Job ${job.status}${job.error_code ? " / " + job.error_code : ""}`
          : "Checking job..."}
      </p>
      {error && <ErrorNotice message={error} />}
      <div className="actions">
        <button className="secondary" onClick={() => setRefresh((n) => n + 1)}>
          Refresh job
        </button>
        {job && ["queued", "running"].includes(job.status) && (
          <button
            className="secondary"
            onClick={() => {
              void api
                .cancelJob(id)
                .then(receive)
                .catch((e: unknown) => setError(errorMessage(e)));
            }}
          >
            Cancel job
          </button>
        )}
        {job &&
          ["failed", "cancelled", "interrupted"].includes(job.status) &&
          retry && (
            <button className="secondary" onClick={retry}>
              Edit/retry draft
            </button>
          )}
      </div>
      <p className="meta">
        Refresh checks stop after ten minutes. A cancelled or failed job keeps
        the previous active edition.
      </p>
    </section>
  );
}
