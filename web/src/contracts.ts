import { z } from "zod";
import type { components } from "./generated/api";
export type SessionView = components["schemas"]["SessionView"];
export type Answer = components["schemas"]["Answer"];
export type CitationView = components["schemas"]["CitationView"];
export type Citation = components["schemas"]["Citation"];
export type DocumentSummary = components["schemas"]["DocumentSummary"];
export type DocumentView = components["schemas"]["DocumentView"];
export type QuestionRequest = components["schemas"]["QuestionRequest"];
export type ReplaceInput = components["schemas"]["ReplaceInput"];
export type ImportInput = components["schemas"]["ImportInput"];
export type JobView = components["schemas"]["JobView"];
export type Profile = "fixture" | "local";
export const sessionSchema: z.ZodType<SessionView> = z.strictObject({
  user_id: z.string(),
  role: z.enum(["reader", "maintainer"]),
  csrf_token: z.string(),
});
const citationFields = {
  chunk_id: z.string(),
  document_id: z.string(),
  version_id: z.string(),
  title: z.string(),
  version_label: z.string(),
  effective_date: z.string(),
  section_id: z.string(),
  start_char: z.number().int().nonnegative(),
  end_char: z.number().int().nonnegative(),
  quote: z.string(),
};
export const citationSchema: z.ZodType<Citation> =
  z.strictObject(citationFields);
export const citationViewSchema: z.ZodType<CitationView> = z.strictObject({
  ...citationFields,
  section_text: z.string(),
  section_start_char: z.number().int().nonnegative(),
  highlight_start: z.number().int().nonnegative(),
  highlight_end: z.number().int().nonnegative(),
});
const documentFields = {
  id: z.string(),
  title: z.string(),
  version_id: z.string(),
  version_label: z.string(),
  effective_date: z.string(),
  revision: z.number().int(),
};
export const documentSchema: z.ZodType<DocumentSummary> =
  z.strictObject(documentFields);
export const documentViewSchema: z.ZodType<DocumentView> = z.strictObject({
  ...documentFields,
  text: z.string(),
});
export const answerSchema: z.ZodType<Answer> = z.strictObject({
  request_id: z.string(),
  execution_profile: z.enum(["fixture", "local"]),
  retrieval_mode: z.enum(["bm25", "dense", "hybrid", "hybrid_rerank"]),
  generation_mode: z.enum(["extractive", "local"]),
  answer: z.string(),
  abstained: z.boolean(),
  reason: z.string().nullable(),
  citations: z.array(citationSchema),
  timings_ms: z.record(z.string(), z.number()),
});
export const jobSchema: z.ZodType<JobView> = z.strictObject({
  id: z.string(),
  status: z.enum([
    "queued",
    "running",
    "succeeded",
    "failed",
    "cancelled",
    "interrupted",
  ]),
  error_code: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
});
export const acceptedSchema = z.strictObject({ job_id: z.string() });
export const healthSchema = z.strictObject({
  status: z.literal("ok"),
  execution_profile: z.enum(["fixture", "local"]),
});
export const errorSchema = z.strictObject({
  error: z.strictObject({
    code: z.string(),
    message: z.string(),
    request_id: z.string(),
  }),
});
