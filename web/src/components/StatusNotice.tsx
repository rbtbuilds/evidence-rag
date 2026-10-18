import { useEffect, useRef } from "react";
import type { Profile } from "../contracts";
export function StatusNotice({ profile }: { profile: Profile | null }) {
  return (
    <aside className="notice" aria-label="Execution profile">
      {profile === "fixture" ? (
        <>
          <strong>Fixture / extractive</strong>
          <p>
            Real keyword search. Dense retrieval and reranking use deterministic
            test doubles. Answers quote the fictional manuals.
          </p>
        </>
      ) : profile === "local" ? (
        <>
          <strong>Local models</strong>
          <p>
            Pinned local snapshots. Exact quotations are the default.
            Experimental local generation failed its quality gate; generated
            claims can be unsupported.
          </p>
        </>
      ) : (
        <p>Checking the local execution profile...</p>
      )}
    </aside>
  );
}
export function ErrorNotice({ message, id }: { message: string; id?: string }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => ref.current?.focus(), [message]);
  return (
    <div id={id} ref={ref} className="error notice" role="alert" tabIndex={-1}>
      {message}
    </div>
  );
}
