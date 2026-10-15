import { useState } from "react";
import type { Profile, QuestionRequest } from "../contracts";
export function QuestionForm({
  profile,
  busy,
  ask,
}: {
  profile: Profile | null;
  busy: boolean;
  ask: (input: QuestionRequest) => void;
}) {
  const [question, setQuestion] = useState("");
  const [retrieval, setRetrieval] =
    useState<NonNullable<QuestionRequest["retrieval_mode"]>>("hybrid_rerank");
  const [generation, setGeneration] =
    useState<NonNullable<QuestionRequest["generation_mode"]>>("extractive");
  return (
    <form
      className="question-form"
      onSubmit={(event) => {
        event.preventDefault();
        ask({
          question,
          retrieval_mode: retrieval,
          generation_mode: generation,
        });
      }}
    >
      <label htmlFor="question">Question</label>
      <textarea
        id="question"
        value={question}
        onChange={(event) => setQuestion(event.target.value)}
        required
        maxLength={500}
        rows={3}
        aria-describedby="question-help"
        placeholder="What is the circulation display limit?"
      />
      <p id="question-help" className="meta">
        Ask about the fictional Aster trainer. {question.length}/500 characters.
      </p>
      <div className="form-row">
        <div>
          <label htmlFor="retrieval">Retrieval method</label>
          <select
            id="retrieval"
            value={retrieval}
            onChange={(event) =>
              setRetrieval(event.target.value as typeof retrieval)
            }
          >
            <option value="bm25">BM25 keyword</option>
            <option value="dense">Dense cosine</option>
            <option value="hybrid">Hybrid RRF</option>
            <option value="hybrid_rerank">Hybrid + reranking</option>
          </select>
        </div>
        <div>
          <label htmlFor="generation">Answer mode</label>
          <select
            id="generation"
            value={generation}
            onChange={(event) =>
              setGeneration(event.target.value as typeof generation)
            }
          >
            <option value="extractive">Exact quotations</option>
            <option value="local" disabled={profile !== "local"}>
              Local generation
            </option>
          </select>
        </div>
      </div>
      <button disabled={busy || profile === null}>
        {busy ? "Reading evidence..." : "Ask question"}
      </button>
      <span className="meta" role="status">
        {busy ? "Waiting for a checked answer." : ""}
      </span>
    </form>
  );
}
