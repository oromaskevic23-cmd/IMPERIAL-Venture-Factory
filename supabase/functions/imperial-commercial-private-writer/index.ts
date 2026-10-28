// IMPERIAL Core private commercial writer: authorized draft-only, source revalidated.
// Requires SUPABASE Auth user JWT, verified by gateway and Auth server.
// Uses only a publishable API key + caller's JWT. No service_role secret.
import {API, validateIssue, receiptSha256} from "./core.mjs";

function respond(status, data) {
  return new Response(JSON.stringify(data), {status, headers: {
    "content-type": "application/json; charset=utf-8",
    "cache-control": "no-store",
    "x-content-type-options": "nosniff",
  }});
}
function publicApiKey() {
  const legacy = Deno.env.get("SUPABASE_ANON_KEY");
  if (legacy) return legacy;
  const singular = Deno.env.get("SUPABASE_PUBLISHABLE_KEY");
  if (singular) return singular;
  try {
    const entry = JSON.parse(Deno.env.get("SUPABASE_PUBLISHABLE_KEYS") || "{}").default;
    if (typeof entry === "string" && entry.length > 10) return Deno.env.get(entry) || entry;
  } catch { /* deny when no configured publishable key */ }
  return "";
}
async function boundedJson(res, maxBytes) {
  const declared = Number(res.headers.get("content-length") || 0);
  if (declared > maxBytes) throw new Error("OVERSIZE");
  const text = await res.text();
  if (new TextEncoder().encode(text).length > maxBytes) throw new Error("OVERSIZE");
  return JSON.parse(text);
}
Deno.serve(async (req) => {
  if (req.method !== "POST") return respond(405, {error:"METHOD_NOT_ALLOWED"});
  const auth = req.headers.get("Authorization") || "";
  if (!/^Bearer [A-Za-z0-9._~-]+$/.test(auth)) return respond(401, {error:"AUTH_REQUIRED"});
  const apiURL = Deno.env.get("SUPABASE_URL") || "";
  const key = publicApiKey();
  if (!apiURL.startsWith("https://") || !key) return respond(503, {error:"BACKEND_NOT_CONFIGURED"});
  const length = Number(req.headers.get("content-length") || 0);
  if (!Number.isFinite(length) || length > 512) return respond(413, {error:"REQUEST_TOO_LARGE"});
  let payload;
  try {
    const raw = await req.text();
    if (raw.length > 512) return respond(413, {error:"REQUEST_TOO_LARGE"});
    payload = JSON.parse(raw);
    if (!payload || Array.isArray(payload) || typeof payload !== "object"
       || Object.keys(payload).some(k => !["issue_number","dry_run"].includes(k))
       || !Number.isSafeInteger(payload.issue_number)
       || payload.issue_number < 1 || payload.issue_number > 9999999999999
       || (payload.dry_run !== undefined && typeof payload.dry_run !== "boolean")) {
      return respond(400, {error:"INVALID_REQUEST"});
    }
  } catch { return respond(400, {error:"INVALID_JSON"}); }

  // Auth server validation avoids trusting an unverified JWT payload.
  let user;
  try {
    const validation = await fetch(apiURL + "/auth/v1/user", {headers: {
      "apikey":key, "Authorization":auth,
    }, signal:AbortSignal.timeout(8000)});
    if (!validation.ok) return respond(401, {error:"AUTH_REQUIRED"});
    user = await boundedJson(validation, 16384);
  } catch { return respond(503, {error:"AUTH_SERVER_UNAVAILABLE"}); }
  if (typeof user?.id !== "string"
      || user?.app_metadata?.imperial_commercial_writer !== "enabled") {
    return respond(403, {error:"WRITER_NOT_APPROVED"});
  }

  // Fetch the exact public GitHub Issue from a fixed host; never trust posted issue bodies.
  let reference;
  try {
    const source = await fetch(API + "/issues/" + payload.issue_number, {redirect:"error", headers: {
      "Accept":"application/vnd.github+json",
      "User-Agent":"imperial-private-crm-writer/1.0",
      "X-GitHub-Api-Version":"2022-11-28",
    }, signal:AbortSignal.timeout(8000)});
    if (!source.ok) return respond(424, {error:"SOURCE_NOT_VERIFIABLE"});
    reference = validateIssue(await boundedJson(source, 65536), payload.issue_number);
  } catch { return respond(424, {error:"SOURCE_NOT_VERIFIABLE"}); }

  // Review-only mode, no write and no customer or personal fields in response.
  if (payload.dry_run === true) {
    return respond(200, {status:"VERIFIED_SOURCE_DRY_RUN",
      source_ref:reference.source_ref, dispatch_allowed:false, payment_confirmed:false});
  }
  const hash = await receiptSha256(payload.issue_number);
  try {
    const db = await fetch(apiURL + "/rest/v1/rpc/imperial_commercial_draft_intake", {
      method:"POST",
      headers:{"apikey":key,"Authorization":auth,"content-type":"application/json"},
      body:JSON.stringify({p_issue_number:payload.issue_number,p_receipt_sha256:hash}),
      signal:AbortSignal.timeout(8000),
    });
    if (db.status === 401 || db.status === 403) return respond(403, {error:"WRITER_NOT_APPROVED"});
    if (!db.ok) return respond(503, {error:"DRAFT_GATE_REJECTED"});
    const result = await boundedJson(db, 4096);
    if (!["DRAFT_INSERTED","DUPLICATE_IGNORED"].includes(result?.status)
      || result.source_ref !== reference.source_ref
      || result.dispatch_allowed !== false) return respond(503, {error:"UNEXPECTED_DRAFT_RESULT"});
    return respond(200, {status:result.status, source_ref:result.source_ref,
      owner_scope_approval_required:true, dispatch_allowed:false, payment_confirmed:false});
  } catch { return respond(503, {error:"DRAFT_GATE_UNAVAILABLE"}); }
});
