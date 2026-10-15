import type { Answer } from "../contracts";
export function AnswerPanel({
  answer,
  open,
}: {
  answer: Answer | null;
  open: (id: string) => void;
}) {
  if (!answer)
    return (
      <section className="answer-grid">
        <div className="empty">
          <h2>Start with a question</h2>
          <p>Your answer and its current source passages will appear here.</p>
        </div>
        <aside className="evidence">
          <h2>Evidence</h2>
          <p>No passages selected yet.</p>
        </aside>
      </section>
    );
  return (
    <section className="answer-grid">
      <div data-testid="answer" aria-live="polite">
        <h2>{answer.abstained ? "Insufficient evidence" : "Answer"}</h2>
        <p className="meta">
          {answer.generation_mode === "extractive"
            ? "Exact source quotations"
            : "Local generated answer"}{" "}
          / {answer.retrieval_mode.replaceAll("_", " ")}
        </p>
        <div className="answer-text">
          {answer.abstained
            ? answer.reason === "invalid_generation"
              ? "The local model returned an invalid answer format or citation. No generated claim was accepted."
              : "The accessible current sources do not provide enough matching evidence. Try a more specific question."
            : answer.answer}
        </div>
        <p className="meta">
          Citation links verify the current version. They do not certify every
          claim.
        </p>
      </div>
      <aside className="evidence">
        <h2>Evidence</h2>
        {answer.citations.length === 0 ? (
          <p>No supporting passages.</p>
        ) : (
          <ol>
            {answer.citations.map((c) => (
              <li key={c.chunk_id}>
                <a
                  id={"cite-" + c.chunk_id}
                  href={"/citations/" + encodeURIComponent(c.chunk_id)}
                  onClick={(event) => {
                    event.preventDefault();
                    open(c.chunk_id);
                  }}
                >
                  {c.title} - {c.version_label} - {c.effective_date}
                </a>
                <p className="meta">{c.section_id}</p>
              </li>
            ))}
          </ol>
        )}
      </aside>
    </section>
  );
}
