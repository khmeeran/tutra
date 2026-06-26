# NEXT_SESSION.md

## Objective: Vercel Deployment Readiness
**Target:** The day after tomorrow, we deploy Tutra to Vercel and test it as first-time users outside a development machine.
**Rule:** No new features tomorrow. No scope expansion. Fix only what blocks deployment.

## Tomorrow's P0 Execution Checklist

### 1. Build Stability
- [ ] Verify frontend builds without warnings/errors (`npm run build`).
- [ ] Verify backend starts cleanly without import errors.
- [ ] Remove obvious debug code and stray `console.log` statements.
- [ ] Confirm `launch.bat` starts the project successfully.

### 2. Authentication Verification
- [ ] Complete end-to-end Google Authentication testing.
- [ ] Verify refresh persistence, logout destruction, protected routes, and role-based routing middleware.
- [ ] Remove any remaining temporary auth shortcuts or mocked IDs.

### 3. Parent Flow Testing
- [ ] Test the complete journey end-to-end: Landing → Google Login → Discovery → Parent Dashboard → Academic Scan → Lesson → Pricing.
- [ ] Fix any blockers in this sequence immediately.

### 4. Student Learning Record Validation
- [ ] Verify every critical event is successfully written to the database.
- [ ] Ensure logs trigger for: Discovery, Scan, Lesson, Mastery, and Dashboard interactions.
- [ ] Confirm no missing events.

### 5. UI Polish
- [ ] Fix high-impact issues only (Alignment, Spacing, Typography).
- [ ] Polish Loading states, Error messages, and Empty states.
- [ ] **STRICT NO:** No redesigns.

### 6. Deployment Readiness
- [ ] Document all required environment variables (`.env` and `.env.local`).
- [ ] Ensure production build succeeds locally.
- [ ] Ensure API URLs are configurable via environment variables (replace `http://localhost:8000`).
- [ ] Remove all localhost hardcoding and development-only credentials from source code.

### 7. Documentation
- [ ] Update `TECHNICAL_DEBT.md` to mark exactly what remains before final deployment.
- [ ] Keep this `NEXT_SESSION.md` updated as items are checked off.

## Success Metric
"Are we confident enough to let someone outside our development machine try Tutra?"
If yes, we deploy. If not, we fix only what blocks deployment.
