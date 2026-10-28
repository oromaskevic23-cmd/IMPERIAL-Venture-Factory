// Strict commercial source verification. No database, secrets, or customer content here.
// This module is shared by the private Supabase Edge Function and offline tests.
export const REPO = "oromaskevic23-cmd/IMPERIAL-Venture-Factory";
export const API = "https://api.github.com/repos/" + REPO;
const MARKERS = [
  "What should be assessed?",
  "Public, non-confidential description of the problem",
  "Expected first deliverable",
  "Public issue privacy and scope confirmation",
];
const CONSENT = [
  "- [x] I understand this issue is public and contains no secrets, personal data, payment details, or confidential material.",
  "- [x] I understand any price, delivery and live system access require separate human agreement and explicit approval.",
];
const SENSITIVE = [
  /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/i,
  /-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/i,
  /\b(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9_]{12,})\b/i,
  /(?:authorization|api[_ -]?key|client[_ -]?secret)\s*[:=]\s*(?:bearer\s+)?[A-Za-z0-9_-]{8,}/i,
];
const TEST = /SYSTEM TEST|NO CUSTOMER|\[TEST ONLY\]|SYNTHETIC DEMO/i;
export class SourceRejected extends Error {
  constructor(code) { super(code); this.name = "SourceRejected"; }
}
export function validateIssue(issue, number) {
  if (!Number.isSafeInteger(number) || number < 1 || number > 9999999999999) {
    throw new SourceRejected("INVALID_ISSUE_NUMBER");
  }
  if (!issue || typeof issue !== "object" || Array.isArray(issue)
    || issue.number !== number || Object.hasOwn(issue, "pull_request")) {
    throw new SourceRejected("NOT_A_PUBLIC_ISSUE");
  }
  if (issue.url !== API + "/issues/" + number
      || issue.html_url !== "https://github.com/" + REPO + "/issues/" + number
      || issue.state !== "open") {
    throw new SourceRejected("SOURCE_MISMATCH");
  }
  if (!issue.user || typeof issue.user.login !== "string" || issue.user.login.length === 0
    || issue.user.login.toLowerCase() === REPO.split("/")[0].toLowerCase()
    || issue.user.type !== "User") {
    throw new SourceRejected("OWNER_TEST_OR_NO_AUTHOR");
  }
  const title = issue.title, body = issue.body;
  if (typeof title !== "string" || title.length > 250
    || !title.startsWith("[Audit request]")
    || typeof body !== "string" || body.length > 8000) {
    throw new SourceRejected("FORM_NOT_ELIGIBLE");
  }
  if (TEST.test(title + "\n" + body) || SENSITIVE.some(r => r.test(title + "\n" + body))) {
    throw new SourceRejected("TEST_OR_PRIVACY_HOLD");
  }
  if (!MARKERS.every(v => body.includes(v)) || !CONSENT.every(v => body.includes(v))) {
    throw new SourceRejected("SCOPE_OR_CONSENT_MISSING");
  }
  if (!Array.isArray(issue.labels)) throw new SourceRejected("LABELS_REQUIRED");
  if (issue.labels.some(x => typeof x?.name === "string"
    && /privacy-review-required|commercial-scope-review|test|spam/i.test(x.name))) {
    throw new SourceRejected("SOURCE_ON_HOLD");
  }
  return {number, source_ref: "github:" + REPO + "#" + number};
}
export async function receiptSha256(number) {
  if (!Number.isSafeInteger(number) || number < 1 || number > 9999999999999)
    throw new SourceRejected("INVALID_ISSUE_NUMBER");
  const canonical = JSON.stringify({
    issue: String(number), offer: "IC-OFFER-001", repo: REPO,
  });
  const bytes = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(canonical));
  return Array.from(new Uint8Array(bytes), x => x.toString(16).padStart(2, "0")).join("");
}
