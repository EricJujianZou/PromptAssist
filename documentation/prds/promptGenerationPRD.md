# PRD Addendum: Dynamic Inline Prompt Augmentation (MVP)
**Date:** 2025-05-25
**Based on Discussion:** Refining PRD v1.1

This document summarizes key decisions and clarifications for the MVP development of the "Dynamic Inline Prompt Augmentation" feature, acting as an addendum to the existing PRD.

## 1. LLM API & Prompting Strategy

### POC API:
*   **Service:** Google Cloud Vertex AI (utilizing free credits)
*   **Model:** Gemini 2.0 Flash (prioritizing speed for POC)
*   **Authentication:** To be provided by the product lead (e.g., service account key).

### Production API (Post-POC Evaluation):
*   Decision based on POC performance (augmented prompt quality, cost, latency).
*   **Candidates:** More capable Gemini models (e.g., 2.5 Pro), OpenAI GPT-4o-mini, Anthropic Claude 3 Sonnet/Haiku.
*   **Priority:** Balance speed, accuracy, and cost.

### Meta-Prompt Strategy (Iterative):
*   **Core:** Develop a strong initial meta-prompt incorporating:
    *   **Role Prompting:** (e.g., "You are an expert prompt engineer...")
    *   **Clear Task Definition:** (e.g., "Transform the user's request into a highly effective, detailed prompt...")
    *   **Desired Output Characteristics:** Specify qualities for the augmented prompt (e.g., well-structured, elicits comprehensive response).
*   **Enhancement:** Explore "few-shot examples" if zero-shot results need improvement.
*   **Optimization Goal:** Best possible augmented prompt results. Meta-prompt conciseness is secondary for POC but a long-term cost consideration.

### API Parameters (Vertex AI - Gemini 2.0 Flash):
*   **`temperature`:** Low (e.g., 0.2-0.5) for focused, deterministic augmentation.
*   **`max_output_tokens`:** Reasonable limit (e.g., 300-500 tokens initially) to control costs and response time.
*   **(Other parameters like `top_p`, `top_k` as per Gemini best practices).**

### Testing:
*   Iterative testing of meta-prompts and parameters is crucial.
*   Functional testing with representative users will be conducted.

## 2. Focus Changes & User Typing During API Call

### Focus Change Handling (e.g., Alt-Tab):
*   **During API Call:** Attempt to abort the ongoing API call to Vertex AI.
*   **During Text Replacement Simulation:** Immediately terminate keyboard simulation.
*   **Combined (2-Layer Protection):** If API call completes but focus changed before pasting, the augmented prompt will not be inserted.

### User Types Concurrently (After Space trigger, before API response/replacement):
*   User's additionally typed characters will appear *after* the dynamically inserted augmented prompt.
*   **Rationale:** Simpler, predictable, avoids complex text merging. Users implicitly guided to wait.

### User Feedback (Future - PRD vNext):
*   Document for future: "Provide user feedback for focus change events (e.g., API call aborted, text replacement cancelled) via in-app UI (Snippet Manager status) or a system tray notification."

## 3. Error Message Display

### MVP:
*   If API call (including one retry) fails, replace original `::Prompt(...)` text with a concise inline error (e.g., `[Prompt Generation Failed. Try again.]`).

### Future Improvement (for PRD vNext):
*   System tray notification for API errors.
*   Optional detailed error message/log reference in Snippet Manager UI.

## 4. API Timeout Duration

### MVP:
*   Development team to determine an appropriate timeout for Vertex AI API calls.
*   **Guideline:** Start with 2-3 times the typical P95 response time for Gemini 2.0 Flash for this task.
*   PRD's <5s end-to-end target is a guideline, acknowledging external dependencies.

### Factors for Dev Team to Consider (and document findings):
*   Observed typical and P95 API response times.
*   User tolerance for waiting vs. quicker failure/retry.
*   Cost implications of long timeouts.

## 5. API Key / Authentication Security

### MVP Development & Testing Stages:
*   **Initial Local Development (Primary Developer Only):** Direct use of Vertex AI authentication (e.g., service account key file) in a local, non-committed, non-shared environment is permissible for speed. **Strictly for isolated local testing.**
*   **MVP Release (Including any internal/wider testing):** A **backend proxy server must be implemented** to securely manage and use Vertex AI credentials. The client application will call this proxy.

### Backend Proxy Analysis & Justification:
*   **Complexity:** Involves creating a lightweight server application (e.g., Python with Flask/FastAPI) hosted by the development team/organization.
*   **Tech Stack & Hosting:** Google Cloud Project for hosting, Python + FastAPI for the backend.
*   **Best Practice:** Industry-standard and most secure method to protect API credentials for distributed client-side applications.
*   **Decision:** Backend proxy is a **mandatory component** for MVP release.

*(A separate, detailed discussion on backend proxy architecture, hosting, and security will be held if needed).*

## 6. User Feedback During API Call

### MVP:
*   Upon successful trigger (`::Prompt(...)` + Space) and API call initiation, inline text changes for immediate feedback.
*   **Example:** `::Prompt(user query)` changes to `::Prompt(Generating...)`.

### Future Improvement (for PRD vNext):
*   Subtle system tray icon animation.
*   Non-intrusive toast notifications for key state changes.

## Prioritization for MVP (Opinion for Fastest Functional MVP):

1.  **Core Trigger & Parsing:** Detect `::Prompt(...) Space`, extract user input.
2.  **Basic Vertex AI API Integration (Local Dev Only):** Implement API call to Gemini 2.0 Flash with initial meta-prompt, using direct auth locally and temporarily.
3.  **Basic Text Replacement:** Delete original command, insert API response.
4.  **Inline Feedback (`Generating...`):** Implement textual change during API call.
5.  **Inline Error Message:** Basic inline error display on API failure (with one retry).
6.  **Focus Change Handling (Core Logic):**
    *   Terminate typing if focus changes during replacement.
    *   Attempt to abort API call / prevent pasting if focus changes during API call.
7.  **Backend Proxy Implementation:** Design, build, and integrate the secure backend proxy. **Crucial before any distribution.**
8.  **Refine Meta-Prompt & API Parameters:** Based on initial testing through the proxy.
9.  **API Timeout Logic:** Implement robust timeout for API calls.

## Potential Challenges & Technical Complexities:

*   **Vertex AI Authentication & API Nuances:** Correct implementation and adaptation.
*   **Reliable Focus Change Detection & API Call Abortion:** Robust cross-application focus detection and clean HTTP request abortion.
*   **Backend Proxy Development:** Setting up a separate service, managing security, deployment.
*   **State Management:** Lifecycle of a dynamic prompt request.

## Risks and Mitigation/Improvement Strategies:

*   **Risk:** External LLM API (Vertex AI) unreliability/latency.
    *   **Mitigation:** Retry logic, appropriate timeouts, clear user feedback.
*   **Risk:** Suboptimal augmented prompts.
    *   **Mitigation:** Iterative meta-prompt engineering, testing, potential few-shot examples.
*   **Risk:** API credential security if backend proxy is delayed/misconfigured.
    *   **Mitigation:** Prioritize backend proxy as essential for MVP. Strict local-only use of direct credentials during early dev.
*   **Risk:** Meeting <5s performance target consistently.
    *   **Mitigation:** Use fast models, optimize API calls, manage user expectations.