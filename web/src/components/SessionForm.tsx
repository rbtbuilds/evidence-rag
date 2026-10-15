import { useState } from "react";
export function SessionForm({
  login,
  busy,
  codeInvalid = false,
}: {
  login: (code: string) => void;
  busy: boolean;
  codeInvalid?: boolean;
}) {
  const [code, setCode] = useState("");
  return (
    <section className="sign-in panel">
      <h2>Open a demo session</h2>
      <p>
        Use a reader or maintainer code printed in your local terminal. This
        demonstration contains fictional equipment manuals.
      </p>
      <form
        onSubmit={(event) => {
          event.preventDefault();
          login(code);
          setCode("");
        }}
      >
        <label htmlFor="access-code">Demo access code</label>
        <input
          id="access-code"
          type="password"
          value={code}
          onChange={(event) => setCode(event.target.value)}
          autoComplete="off"
          required
          maxLength={256}
          aria-invalid={codeInvalid}
          aria-describedby={codeInvalid ? "code-help app-error" : "code-help"}
        />
        <p id="code-help" className="meta">
          Launch codes stay in this session. They are never saved in browser
          storage.
        </p>
        <button disabled={busy}>Sign in</button>
        <p role="status">{busy ? "Updating the demo session..." : ""}</p>
      </form>
    </section>
  );
}
