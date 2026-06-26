# 3. Operations Bible

This document governs everything outside the codebase. Software alone does not build a company; operational excellence ensures the software can thrive.

---

## 1. Support & Customer Success
* **Tone:** Empathetic, extremely fast, human. Never robotic.
* **Channels:** WhatsApp (Primary for India), Email (Secondary).
* **SLA:** First response under 15 minutes during working hours.
* **Escalation:** If a parent is frustrated because a concept scan graded their child incorrectly, the engineering team is pinged immediately. Product bugs disguised as "bad AI" are P0.

## 2. Marketing & Brand
* **Core Message:** Tutra builds confidence. We sell the emotional transformation of the child, not the AI technology.
* **Content:** Success stories (PTM moments), free learning resources for parents, guides on handling academic anxiety.
* **Channels:** Instagram (visual storytelling), SEO (parenting queries), Word-of-mouth (referral loops).

## 3. Pricing & Subscriptions
* **Philosophy:** Premium but accessible. Worth every rupee.
* **Trial:** 7-day risk-free trial. Requires Google Auth, but no credit card upfront to maximize top-of-funnel entry.
* **Plans:** Monthly (flexible), Yearly (discounted, commitment to the 95% journey).
* **Refunds:** No-questions-asked refund policy within the first 14 days of a paid plan. We want parents who *want* to be here.

## 4. B2B & Schools (Future Phase)
* **Strategy:** Tutra as a teacher's assistant, not a replacement.
* **Value Prop:** We give teachers super-powers to identify exactly which students are falling behind in which concepts, saving them hours of manual grading.
* **Onboarding:** Bulk student upload via CSV. Admin dashboards for Principals.

## 5. Legal & Compliance
* **Data Privacy:** Extremely strict. We are handling children's data. Zero third-party data selling.
* **Terms:** Clear, plain English terms of service.
* **Tax/GST:** Automated invoicing with proper HSN codes and GST integration (Razorpay/Stripe).

## 6. Communication (Emails & WhatsApp)
* **Lifecycle Marketing:**
  * **Day 1:** Welcome + How to do the first scan.
  * **Day 3:** Checking in on the child's reaction.
  * **Day 7 (Trial End):** The value of consistency. Upgrade prompt.
  * **Weekly:** "Your child's brain this week" report.
* **Tone:** Encouraging, data-driven, celebratory.

## 7. AI Operations & Cost Tracking
* **LLM Spend:** Track Ollama/OpenAI API costs per student per month. 
* **Unit Economics:** Ensure the monthly subscription price comfortably covers the compute cost of an active student (assuming daily usage).
* **Model Updates:** Regularly evaluate prompt drift. If the AI becomes repetitive or hallucinates, update prompts safely using shadow testing.

## 8. Renewals & Retention
* **Churn Prevention:** If a student goes idle for 4 days, trigger a low-friction re-engagement mission (e.g., a fun 2-minute visual puzzle) to bring them back.
* **Renewal Communication:** Notify parents 7 days before annual billing. Highlight the year's progress graph. 
