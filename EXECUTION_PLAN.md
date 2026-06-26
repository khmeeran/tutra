# TOMORROW'S SPRINT: VERCEL DEPLOYMENT READINESS

This document is the Senior Technical Lead's execution plan. It is based on a deep, line-by-line review of the current `frontend/src/` and `backend/app/` codebase. 

---

## Things We Will NOT Do Tomorrow
Be brutally strict. If it does not actively prevent a Vercel deployment or crash the end-to-end user journey, it is out of scope.

* ❌ **Curriculum Knowledge Graph** (This is the next major initiative, but we must stabilize the current app first).
* ❌ **Advanced Analytics**
* ❌ **Gamification & Trophies**
* ❌ **Teacher Portal / School Portal**
* ❌ **Voice Tutor / Multimodal AI**
* ❌ **Exam Prediction**
* ❌ **Parent Reports V2**

Tomorrow is exclusively about making the existing code robust enough for external testing.

---

## Phase 1: Build Stability

### Replace Localhost Hardcoding
* **Current Status:** 🔴 Broken (Hardcoded for local dev)
* **Evidence:** `grep` reveals `http://localhost:8000` is hardcoded across 10+ lines in `frontend/src/app/` (e.g., `academic-scan/page.tsx:65`, `discovery/page.tsx:142`, `lesson/page.tsx:36`).
* **Why it matters:** Vercel frontend will not be able to communicate with the production backend.
* **Estimated Time:** 15 mins
* **Acceptance Criteria:** Every hardcoded URL is replaced with `process.env.NEXT_PUBLIC_API_URL`.

### Fix Next.js Build
* **Current Status:** 🟡 Partial
* **Evidence:** We made rapid changes to `layout.tsx` and `ProtectedRoute.tsx`. `npm run build` will likely surface strict TypeScript errors (e.g., implicit `any` in API responses).
* **Why it matters:** Vercel enforces a strict build step. If `next build` fails, deployment halts.
* **Estimated Time:** 30 mins
* **Acceptance Criteria:** `npm run build` exits with code 0.

---

## Phase 2: Authentication Verification

### Migrate `fetch` to Authenticated `api.ts`
* **Current Status:** 🔴 Broken (Security bypass)
* **Evidence:** `lib/api.ts` correctly intercepts and attaches the `Authorization: Bearer <token>` header. However, most `page.tsx` files are still using raw `fetch("http://localhost:8000/api...")`. 
* **Why it matters:** Since we secured the backend with `Depends(get_current_user)`, all raw `fetch` requests will return `401 Unauthorized`.
* **Estimated Time:** 45 mins
* **Acceptance Criteria:** All frontend API calls use the `axios` instance from `lib/api.ts`.

### Secure Unprotected Backend Endpoints
* **Current Status:** 🔴 Broken
* **Evidence:** `backend/app/routers/discovery.py` has no `Depends(get_current_user)` on its `/reflect`, `/report`, or `/math-scan` endpoints.
* **Why it matters:** Anyone with the API URL could spam our AI endpoints without logging in.
* **Estimated Time:** 15 mins
* **Acceptance Criteria:** `discovery.py` endpoints enforce JWT authentication.

---

## Phase 3: Parent Journey (End-to-End)

### Fix Student ID Injection
* **Current Status:** 🟡 Partial
* **Evidence:** The frontend uses `getTempStudentId()` which pulls from `localStorage`. We must ensure the `Discovery` flow properly assigns the created `student_profile_id` to the session upon completion.
* **Why it matters:** If the student ID is missing or undefined, the backend ownership checks will reject the request with `403 Forbidden`.
* **Estimated Time:** 30 mins
* **Acceptance Criteria:** Parent Dashboard and Lesson Engine load the correct student profile without throwing 403 or 404 errors.

---

## Phase 4: Student Learning Record (SLR)

### Verify Append-Only Logging
* **Current Status:** 🟡 Partial
* **Evidence:** `frontend/src/app/lesson/page.tsx:55` fires a raw fetch to `/api/v1/slr/log` but doesn't await or handle errors gracefully. 
* **Why it matters:** If network latency causes a drop, we lose the learning event permanently.
* **Estimated Time:** 30 mins
* **Acceptance Criteria:** Network tab confirms `200 OK` on every `/slr/log` POST during Discovery, Scan, and Lesson completion.

---

## Phase 5: UI Polish

### Fix Broken Alignment & Loading States
* **Current Status:** 🟡 Partial
* **Evidence:** The `ProtectedRoute` component displays a generic `Loading...` div. 
* **Why it matters:** Looks broken to first-time users.
* **Estimated Time:** 30 mins
* **Acceptance Criteria:** Implement a clean, branded loading spinner in `ProtectedRoute.tsx`.

---

## Phase 6: Deployment Readiness

### Document Production Environment Variables
* **Current Status:** 🟡 Partial
* **Why it matters:** Vercel needs `.env` variables injected via the Vercel Dashboard.
* **Estimated Time:** 15 mins
* **Acceptance Criteria:** Create `.env.example` containing `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_GOOGLE_CLIENT_ID`.

---

## Phase 7: Final Go/No-Go Review (End of Sprint Checklist)

Tomorrow night, we will answer this exact checklist. If any item is "NO", we do not deploy.

- [ ] Google Login works.
- [ ] New parent onboarding works.
- [ ] Existing parent login works.
- [ ] Discovery works.
- [ ] Parent Dashboard loads.
- [ ] Academic Scan works.
- [ ] Lesson works.
- [ ] Pricing page works.
- [ ] No `localhost` URLs remain in the frontend.
- [ ] Production build (`npm run build`) succeeds locally.
- [ ] Backend starts without import errors.
- [ ] No critical console errors in Chrome DevTools.
- [ ] Protected routes successfully block unauthorized users.
- [ ] Logout works and clears all state.
- [ ] Environment variables are fully documented for Vercel.

If every checkbox is YES, we deploy to Vercel the following day.
