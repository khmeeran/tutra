# Tutra Technical Debt Register

This document is brutally honest. It tracks every shortcut, mock, hardcoded value, and temporary implementation. We burn this down gradually.

## 1. Authentication & State
*   **Hardcoded Student ID:** The UUID `00000000-0000-0000-0000-000000000000` is used as a bypass for the `student_profile_id` across the frontend (`src/lib/auth.ts`) and backend routers (`quizzes.py`).
    *   *TODO:* Implement proper Parent-Student DB mapping and inject the actual authenticated student ID via JWTs.
*   **LocalStorage Demographics:** The child's basic profile form data (Name, Class, Board, Location) from the Discovery flow is stored in `localStorage` (`discovery_state_fast`) instead of the database.
    *   *TODO:* POST this data to `StudentProfile` upon Discovery completion.

## 2. Dynamic Lesson Engine
*   **Ollama Fallbacks:** `ai_service.py` uses hardcoded fallback strings/JSON if Ollama fails or times out.
    *   *TODO:* Implement proper error handling, retries, or graceful degradation UI instead of hiding the failure in the fallback.
*   **Scan to Lesson Handoff:** The `concept` (e.g., "Percentages") passed to the Lesson Engine is currently a hardcoded string in the frontend (`/lesson/page.tsx`) instead of dynamically pulling the exact identified gap from the SLR.
    *   *TODO:* Fetch the identified gap from the `/slr/insights/` endpoint and inject it into the Lesson Engine context.

## 3. Database & Models
*   **String FKs in SLR:** The `StudentActivityLog` (SLR) currently stores `subject` and `concept` as strings for flexibility.
    *   *TODO:* Migrate these to strict Foreign Keys (`subject_id`, `concept_id`) once the Curriculum Engine is fully populated.
*   **Missing Curriculum IDs:** `quizzes.py` uses a generated `uuid4()` for `subject_id` instead of mapping it from the `Topic` hierarchy.

## 4. UI & Dashboard
*   **Student Dashboard Missing Routes:** `/student/dashboard` points to `/student/tutor` and `/student/quiz` which do not exist.
    *   *TODO:* Build the actual student-facing views.
*   **Paywall Modal:** The transition out of the Lesson Engine forces a hardcoded Paywall Modal.
    *   *TODO:* Hook this up to the actual `subscriptions` table and Stripe/Razorpay integration.

## 5. Security
*   **Open Endpoints:** `learning_record.py` and `discovery.py` do not enforce `Depends(get_current_user)`.
    *   *TODO:* Secure all `/api/v1/` routes behind the HTTPBearer token verification.
