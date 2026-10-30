# Automation Failure Audit — evidence preview

Classification: ADVISORY LAB REPORT. Independent QA, customer approval,
delivery and payment are NOT confirmed by this tool.

Workflow: INTEGRATION_DEMO_001
Input SHA-256: 53245e609cc5c7657db0f99921e5b300303c92fe8124557db83a54d079e00e06

## Measurements

- total_events: 5
- distinct_event_ids: 4
- duplicate_event_ids: 1
- http_429: 1
- http_5xx: 1
- timeouts: 1
- slow_over_30s: 1

## Suggested checks

- Verify idempotency keys and duplicate-event suppression.
- Test bounded backoff and Retry-After handling for HTTP 429.
- Review retries, circuit breaker, timeout and dead-letter handling.
- Measure latency budget and add SLA alerting.

No live connectivity or production remediation was performed.
