# NEXT_SESSION.md

## Objective: Deployment Validation Day
**Target:** Get Tutra running in a real-world environment and learn from reality.

## Tomorrow's P0 Execution Checklist

### 1. Backend Portability Audit
- [ ] Final verification that the backend boots cleanly in a production environment.
- [ ] Confirm no exceptions thrown during startup when relying solely on environment variables.

### 2. Environment Variable Verification
- [ ] Ensure all required secrets (`JWT_SECRET`, `DATABASE_URL`) are populated.
- [ ] Ensure `ALLOWED_ORIGINS` is set to the intended Vercel domain.
- [ ] Ensure `GOOGLE_CLIENT_ID` is set correctly on both frontend and backend.
- [ ] Ensure `NEXT_PUBLIC_API_URL` correctly points to the public tunnel URL.

### 3. Cloudflare Connectivity
- [ ] Launch local backend on port 8000.
- [ ] Establish Cloudflare tunnel (`cloudflared tunnel --url http://localhost:8000`).
- [ ] Verify the temporary public HTTPS URL routes correctly to the local FastAPI health checks.

### 4. Vercel Deployment
- [ ] Import `tutra` repository into Vercel.
- [ ] Configure the Root Directory to `frontend`.
- [ ] Inject `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_GOOGLE_CLIENT_ID`.
- [ ] Deploy and verify the build succeeds.

### 5. End-to-End Production Testing
Walk through the entire journey using a brand new Google account (acting exactly like a parent):
- [ ] Landing Page
- [ ] Google Login (Must succeed across origins)
- [ ] Discovery Flow
- [ ] Parent Dashboard
- [ ] Academic Scan
- [ ] Lesson 1
- [ ] Pricing
*Rule: No shortcuts. No database edits. No developer tools.*

### 6. Production Bug Fixing (Only if required)
- [ ] If issues occur, log them first in `PRODUCTION_BUGS.md`.
- [ ] Rank them (P0, P1, P2).
- [ ] Fix blocking (P0) issues systematically.

## Strict Rules for Tomorrow
* **NO new features.**
* **NO scope expansion.**
* **NO architecture discussions** (unless deployment exposes a fundamental flaw).
* **Treat infrastructure as configuration.**
* **Treat the application as portable.**
