# Contribution Guide

This is a public **architecture-first** repository, not a blanket invitation to obtain internal IMPERIAL Core code or secrets.

## Branch and change controls
1. Open a focused issue explaining the user problem, verification method, risks and expected deliverables.
2. Work in a `feat/`, `fix/` or `docs/` branch. Do not push directly to protected primary release branches when review is available.
3. Add reproducible tests, docs, threat considerations and data-boundary notes.
4. Open a Pull Request with exact files and checks. Avoid fabricated test results.
5. Security-sensitive changes need an independent reviewer, Approval Gateway and Founder-designated authorization.

## Local checks
```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_portfolio.py
```
No network or paid account needed.

## IP terms
No open-source license is granted. Contributions and reuse require explicit rights and agreed terms; do not add copyleft, proprietary dependencies, customer records or personal data without review.
