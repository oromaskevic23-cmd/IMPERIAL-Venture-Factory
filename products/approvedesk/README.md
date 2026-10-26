# ApproveDesk VF-01 — local working software slice

**Status: IMPLEMENTED LOCAL MVP / NOT PRODUCTION READY.** Sprint 007. No confirmed customers or revenue.

This is real local code: Python 3 standard library, SQLite, accessible HTML/CSS/JS and real Chromium browser E2E. No cloud secrets, paid APIs, AI model or external customer data.

## Run and test
From repository root:

    python3 products/approvedesk/app.py

Open http://127.0.0.1:8787 . Create an owner and a separate reviewer account, each with a 12+ character password. Owner creates a project and adds the previously registered reviewer. Owner adds a safe small .txt revision. Reviewer comments and approves. Owner can read journal and export JSON.

Run API and authorization suite:

    python3 -m unittest discover -s products/approvedesk/tests -v

GitHub Actions also runs the UI with actual Chromium using two separate browser contexts and persistent SQLite.

## Implemented
- Registration and password-based login with salted PBKDF2-SHA256; HttpOnly SameSite Strict session cookie.
- CSRF checks for all authenticated mutations; tenant project authorization.
- Versioned UTF-8 text, max 24 KiB, strict .txt filename whitelist, no arbitrary binary upload.
- Separate owner and reviewer accounts, comments, once-only approve/reject and JSON export.
- SQLite-backed actions with an append-only application-level SHA256 hash-chain audit prototype.
- Loopback binding only to avoid unapproved production exposure.

## Critical limits
- Not for actual customer data or Internet-facing deployment. No rate limits, email verification, hardened TLS/HTTPS, session expiry, full role revocation, legal-signature acceptance or external pen test.
- Secure cookies must be enabled behind verified HTTPS using APPROVEDESK_SECURE_COOKIE=1.
- Application-level audit data are editable by DB administrators. This is NOT canonical IMPERIAL Core Audit Ledger, ProofGraph or signed Approval Gateway.
- Only .txt mock files, not PDF/document uploads or malware scanning.
- Browser tests are real user sessions, NOT evidence that AI NCA agents wrote the code.
- Independent human QA, full security acceptance, sandbox isolation, production backups and VELION ⚡️ model inference remain blocked/unverified.

Strategic IMPERIAL Core intellectual property is not part of venture asset sales without separately authorized written agreements.
