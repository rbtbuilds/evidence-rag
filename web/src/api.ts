import { z } from "zod";
import {
  sessionSchema,
  answerSchema,
  citationViewSchema,
  documentSchema,
  documentViewSchema,
  jobSchema,
  acceptedSchema,
  healthSchema,
  errorSchema,
  type SessionView,
  type QuestionRequest,
  type ImportInput,
  type ReplaceInput,
} from "./contracts";
const messages: Record<string, string> = {
  session_required: "Your session ended. Sign in again.",
  invalid_code:
    "That code is invalid. Use a code printed by the local init command.",
  forbidden: "This action requires a maintainer session.",
  not_found:
    "This source is unavailable. It may be restricted, replaced or deleted.",
  csrf_invalid: "Session validation failed. Sign out and sign in again.",
  corpus_changed:
    "The documents changed while answering. Ask the question again.",
  revision_conflict:
    "This document changed. Refresh the document list before replacing or deleting it.",
  model_busy:
    "Another model task owns the machine lease. Try again when it finishes.",
  model_unavailable:
    "Local models or the matching index are unavailable. See the local runbook.",
  model_timeout:
    "Local inference timed out. Try a shorter question or extractive mode.",
  queue_full: "The local work queue is full. Wait for a job to finish.",
  rate_limited: "Too many failed codes. Wait one minute before trying again.",
  mode_unavailable: "Local generation requires the local execution profile.",
  limit_exceeded: "The request exceeds the local size limit.",
  invalid_input: "Check the form values and try again.",
  invalid_response: "The server returned an unexpected response.",
  internal_error: "The request failed. Check the local service and try again.",
};
export class ApiFailure extends Error {
  constructor(
    public code: string,
    public status: number,
  ) {
    super(
      messages[code] ??
        "The request failed. Try again or check the local runbook.",
    );
  }
}
let csrf = "";
async function request<T>(
  path: string,
  schema: z.ZodType<T>,
  method = "GET",
  body?: unknown,
  signal?: AbortSignal,
  headers: Record<string, string> = {},
): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 95000);
  const abort = () => controller.abort();
  signal?.addEventListener("abort", abort, { once: true });
  if (signal?.aborted) controller.abort();
  try {
    const response = await fetch(path, {
      method,
      credentials: "include",
      cache: "no-store",
      signal: controller.signal,
      headers: {
        ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
        ...(method !== "GET" && csrf ? { "X-CSRF-Token": csrf } : {}),
        ...headers,
      },
      ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
    });
    if (!response.ok) {
      const data: unknown = await response.json();
      const error = errorSchema.safeParse(data);
      throw new ApiFailure(
        error.success ? error.data.error.code : "invalid_response",
        response.status,
      );
    }
    const value: unknown =
      response.status === 204 ? null : await response.json();
    const parsed = schema.safeParse(value);
    if (!parsed.success)
      throw new ApiFailure("invalid_response", response.status);
    return parsed.data;
  } finally {
    clearTimeout(timeout);
    signal?.removeEventListener("abort", abort);
  }
}
function remember(session: SessionView): SessionView {
  csrf = session.csrf_token;
  return session;
}
export const api = {
  health: (signal?: AbortSignal) =>
    request("/health", healthSchema, "GET", undefined, signal),
  login: async (code: string) =>
    remember(await request("/api/session", sessionSchema, "POST", { code })),
  session: async (signal?: AbortSignal) =>
    remember(
      await request("/api/session", sessionSchema, "GET", undefined, signal),
    ),
  logout: async () => {
    try {
      await request("/api/session", z.null(), "DELETE");
    } finally {
      csrf = "";
    }
  },
  clearSession: () => {
    csrf = "";
  },
  ask: (input: QuestionRequest, signal?: AbortSignal) =>
    request("/api/questions", answerSchema, "POST", input, signal),
  citation: (id: string, signal?: AbortSignal) =>
    request(
      "/api/citations/" + encodeURIComponent(id),
      citationViewSchema,
      "GET",
      undefined,
      signal,
    ),
  documents: (signal?: AbortSignal) =>
    request(
      "/api/documents",
      z.array(documentSchema),
      "GET",
      undefined,
      signal,
    ),
  document: (id: string, signal?: AbortSignal) =>
    request(
      "/api/documents/" + encodeURIComponent(id),
      documentViewSchema,
      "GET",
      undefined,
      signal,
    ),
  import: (input: ImportInput) =>
    request("/api/admin/documents", acceptedSchema, "POST", input),
  replace: (id: string, input: ReplaceInput) =>
    request(
      "/api/admin/documents/" + encodeURIComponent(id) + "/versions",
      acceptedSchema,
      "POST",
      input,
    ),
  remove: (id: string, revision: number) =>
    request(
      "/api/admin/documents/" + encodeURIComponent(id),
      z.null(),
      "DELETE",
      undefined,
      undefined,
      { "If-Match": String(revision) },
    ),
  rebuild: () => request("/api/admin/rebuild", acceptedSchema, "POST", {}),
  job: (id: string, signal?: AbortSignal) =>
    request(
      "/api/admin/jobs/" + encodeURIComponent(id),
      jobSchema,
      "GET",
      undefined,
      signal,
    ),
  cancelJob: (id: string) =>
    request(
      "/api/admin/jobs/" + encodeURIComponent(id) + "/cancel",
      jobSchema,
      "POST",
      {},
    ),
};
export function errorMessage(error: unknown): string {
  if (error instanceof ApiFailure) return error.message;
  if (error instanceof DOMException && error.name === "AbortError")
    return "The request stopped or timed out. Try again when ready.";
  return "The local service could not be reached. Check that the API is running.";
}
