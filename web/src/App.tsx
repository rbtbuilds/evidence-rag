import { useCallback, useEffect, useRef, useState } from "react";
import { api, ApiFailure, errorMessage } from "./api";
import type {
  Answer,
  DocumentSummary,
  Profile,
  QuestionRequest,
  SessionView,
} from "./contracts";
import { StatusNotice, ErrorNotice } from "./components/StatusNotice";
import { SessionForm } from "./components/SessionForm";
import { QuestionForm } from "./components/QuestionForm";
import { AnswerPanel } from "./components/AnswerPanel";
import { CitationViewer } from "./components/CitationViewer";
import { DocumentAdmin } from "./components/DocumentAdmin";
import "./styles.css";
function Workbench({
  session,
  profile,
  expired,
  path,
  navigate,
}: {
  session: SessionView;
  profile: Profile | null;
  expired: () => void;
  path: string;
  navigate: (path: string) => void;
}) {
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [answer, setAnswer] = useState<Answer | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const active = useRef<AbortController | null>(null);
  const documentsRequest = useRef<AbortController | null>(null);
  const lastCitation = useRef("");
  const refresh = useCallback(() => {
    active.current?.abort();
    setAnswer(null);
    setBusy(false);
    documentsRequest.current?.abort();
    const controller = new AbortController();
    documentsRequest.current = controller;
    void api
      .documents(controller.signal)
      .then(setDocuments)
      .catch((e: unknown) => {
        if (!controller.signal.aborted) {
          if (e instanceof ApiFailure && e.status === 401) expired();
          else setError(errorMessage(e));
        }
      });
  }, [expired]);
  useEffect(() => {
    refresh();
    return () => {
      active.current?.abort();
      documentsRequest.current?.abort();
    };
  }, [refresh]);
  useEffect(() => {
    active.current?.abort();
    setBusy(false);
    if (path === "/" && lastCitation.current)
      document.getElementById("cite-" + lastCitation.current)?.focus();
  }, [path]);
  async function ask(input: QuestionRequest) {
    active.current?.abort();
    const controller = new AbortController();
    active.current = controller;
    setBusy(true);
    setError("");
    setAnswer(null);
    try {
      const value = await api.ask(input, controller.signal);
      if (!controller.signal.aborted) setAnswer(value);
    } catch (e: unknown) {
      if (!controller.signal.aborted) {
        if (e instanceof ApiFailure && e.status === 401) expired();
        else setError(errorMessage(e));
      }
    } finally {
      if (!controller.signal.aborted) setBusy(false);
    }
  }
  const match = /^\/citations\/([^/]+)$/.exec(path);
  if (match?.[1])
    return (
      <CitationViewer
        id={decodeURIComponent(match[1])}
        back={() => navigate("/")}
      />
    );
  return (
    <main>
      {error && <ErrorNotice message={error} />}
      <section className="panel">
        <h2>Ask the current manuals</h2>
        <QuestionForm
          profile={profile}
          busy={busy}
          ask={(input) => {
            void ask(input);
          }}
        />
        <AnswerPanel
          answer={answer}
          open={(id) => {
            lastCitation.current = id;
            navigate("/citations/" + encodeURIComponent(id));
          }}
        />
      </section>
      <section className="corpus-summary">
        <h2>Available manuals</h2>
        <p>
          {documents.length
            ? documents.map((doc) => doc.title).join(", ")
            : "No active manuals are available to this session."}
        </p>
        <p className="meta">
          Only sources available to your identity are listed.
        </p>
      </section>
      {session.role === "maintainer" && (
        <DocumentAdmin documents={documents} changed={refresh} />
      )}
    </main>
  );
}
export default function App() {
  const [session, setSession] = useState<SessionView | null>(null);
  const [codeInvalid, setCodeInvalid] = useState(false);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [ready, setReady] = useState(false);
  const [path, setPath] = useState(window.location.pathname);
  const [theme, setTheme] = useState(() => {
    try {
      return localStorage.getItem("theme") ?? "system";
    } catch {
      return "system";
    }
  });
  const expired = useCallback(() => {
    api.clearSession();
    setSession(null);
    setError("Your session ended. Sign in again.");
  }, []);
  useEffect(() => {
    const controller = new AbortController();
    void api
      .health(controller.signal)
      .then((value) => setProfile(value.execution_profile))
      .catch((e: unknown) => {
        if (!controller.signal.aborted) setError(errorMessage(e));
      });
    void api
      .session(controller.signal)
      .then(setSession)
      .catch((e: unknown) => {
        if (
          !controller.signal.aborted &&
          !(e instanceof ApiFailure && e.status === 401)
        )
          setError(errorMessage(e));
      })
      .finally(() => {
        if (!controller.signal.aborted) setReady(true);
      });
    return () => controller.abort();
  }, []);
  useEffect(() => {
    const media = window.matchMedia?.("(prefers-color-scheme: dark)");
    const apply = () => {
      document.documentElement.dataset.theme =
        theme === "system" ? (media?.matches ? "dark" : "light") : theme;
    };
    apply();
    media?.addEventListener("change", apply);
    try {
      localStorage.setItem("theme", theme);
    } catch {
      /* Theme persistence is optional in restricted browser contexts. */
    }
    return () => media?.removeEventListener("change", apply);
  }, [theme]);
  useEffect(() => {
    const pop = () => setPath(window.location.pathname);
    window.addEventListener("popstate", pop);
    return () => window.removeEventListener("popstate", pop);
  }, []);
  function navigate(next: string) {
    window.history.pushState({}, "", next);
    setPath(next);
  }
  async function login(code: string) {
    setBusy(true);
    setError("");
    setCodeInvalid(false);
    setSession(null);
    try {
      setSession(await api.login(code));
    } catch (e: unknown) {
      setCodeInvalid(e instanceof ApiFailure && e.code === "invalid_code");
      setError(errorMessage(e));
    } finally {
      setBusy(false);
    }
  }
  async function logout() {
    setSession(null);
    setError("");
    navigate("/");
    try {
      await api.logout();
    } catch (e: unknown) {
      setError(errorMessage(e));
    }
  }
  return (
    <>
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      <header className="topbar">
        <div>
          <h1>Evidence RAG</h1>
          <p>Ask a question. Inspect its evidence.</p>
        </div>
        <div className="identity">
          <label htmlFor="theme">Theme</label>
          <select
            id="theme"
            value={theme}
            onChange={(e) => setTheme(e.target.value)}
          >
            <option value="system">System</option>
            <option value="light">Light</option>
            <option value="dark">Dark</option>
          </select>
          {session && (
            <>
              <strong data-testid="identity">
                {session.user_id} / {session.role}
              </strong>
              <button
                className="secondary"
                onClick={() => {
                  void logout();
                }}
              >
                Sign out
              </button>
            </>
          )}
        </div>
      </header>
      <div className="workspace" id="main-content" tabIndex={-1}>
        <StatusNotice profile={profile} />
        {error && <ErrorNotice id="app-error" message={error} />}
        <>
          {!ready ? (
            <p role="status">Checking session...</p>
          ) : session ? (
            <Workbench
              key={session.csrf_token}
              session={session}
              profile={profile}
              expired={expired}
              path={path}
              navigate={navigate}
            />
          ) : (
            <main>
              <SessionForm
                login={(code) => {
                  void login(code);
                }}
                busy={busy}
                codeInvalid={codeInvalid}
              />
            </main>
          )}
        </>
      </div>
      <footer>
        Owned fictional Aster manuals. Loopback demonstration authentication.
      </footer>
    </>
  );
}
