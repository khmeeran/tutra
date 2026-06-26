# Tutra Release Notes

This document chronicles the evolution of Tutra from a technical perspective, summarizing changes, fixes, and readiness at the conclusion of every major phase.

---

## [Phase 3 Completion] - SLR Integrity & State Machine Architecture
**Date:** 2026-06-26

### What Changed
* **P0 Backend Owns Reality:** Removed all client-side logging (`/slr/log`). The backend now atomically writes events directly inside the AI service routers (`/discovery/report`, `/discovery/math-scan`, `/lesson/next-step`).
* **P1 Session Integrity:** Introduced `session_id` to `StudentActivityLog` to bind events together across a single learning session.
* **P2 Event Granularity:** Expanded the event model to explicitly track journeys, introducing `discovery_started`, `academic_scan_started`, `lesson_started`, and `retry_attempted`. 
* **P4 Idempotency:** Added an `idempotency_key` column and verification logic. Network drops and form resubmissions will no longer generate duplicate events.
* **P5 State Machine:** Built a rigid `VALID_TRANSITIONS` state machine (`slr_service.py`). It enforces sequential chronological flow (e.g., rejecting a `lesson_completed` if there was no `lesson_started`).
* **P3 Derived Views:** Altered the dashboard insights engine. It no longer relies on fake static summaries and instead algorithmically derives descriptions directly from the event log and dynamic concepts.

### Bugs Fixed
* Fixed a major structural flaw where the SLR was treated as a generic analytics bucket, vulnerable to untrusted client manipulation.
* Addressed data loss risks where a client connection drop post-AI-generation would orphan the data. Atomic backend writes resolve this.

### Breaking Changes
* The generic `/api/v1/slr/log` endpoint remains for legacy references but should be deprecated. All internal AI routers now require `session_id` and `idempotency_key` in the request body.

### Technical Debt Reduced
* Migrated from a naive analytics approach to a robust event sourcing pattern for the Student Learning Record.

### Known Issues
* The AI doesn't yet categorize subsequent lesson interactions as explicitly `hint_requested` vs `independent_solution`; currently, the router generalizes interactions as `retry_attempted` until an explicit "celebrate" state is triggered by the LLM.

### Current Readiness
* **Static Readiness:** 98%
* **Deployment Readiness:** Pending production verification.

---

## [Phase 2 Completion] - Destructive QA Pass & Deployment Stabilization
**Date:** 2026-06-26

### What Changed
* Engineered strict backend role enforcement via a `require_role` dependency in the JWT pipeline, ensuring token privileges are cryptographically enforced at the endpoint boundary.
* Replaced hardcoded pedagogical fallbacks in AI flows (e.g., Academic Scan, Lesson) with a transparent auto-retry network mechanism.
* Implemented a global Axios response interceptor to intercept `401 Unauthorized` responses and proactively clear stale frontend authentication state.

### Bugs Fixed
* **The Zombie Session Bug:** Handled an edge case where expired JWTs on the backend remained in browser `localStorage`, causing infinite hangs or broken empty states.
* **Fabricated AI Fallbacks:** Prevented the system from injecting hallucinated or hardcoded fallback questions when the LLM service disconnected, protecting the integrity of the Student Learning Record.
* **Fake Latency:** Stripped arbitrary `setTimeout` delays from the authentication flow, mapping UI latency 1:1 with actual API latency.

### Breaking Changes
* Any internal endpoints now strictly asserting `require_role` will reject improperly scoped tokens with a `403 Forbidden` rather than a generic `401 Unauthorized` or silently succeeding.

### Technical Debt Reduced
* Repaired Python syntax errors within the core `verify_token` authorization block.
* Executed a repository-wide footprint audit, eliminating rogue `console.log` statements, development `localhost` fallbacks, and outdated `TODO` comments.

### Known Issues
* The `lesson` and `session` components currently utilize `setTimeout` to simulate memory-decay intervals. While functionally necessary for the current architectural state, this relies on client-side timers which do not persist across hard reloads. 

### Current Readiness
* **Static Readiness:** 98%
* **Deployment Readiness:** Pending production verification.
