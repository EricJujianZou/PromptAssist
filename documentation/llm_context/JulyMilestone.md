# State of the Project: Expandr

**Document Version:** 2.0
**Date:** 2025-07-24

## 1. Project Vision & Core Functionality

**Expandr** is a system-wide productivity tool designed to enhance user workflow by integrating text expansion and AI-powered prompt augmentation into any application's text field.

The core value proposition rests on two primary features:

1.  **Static Snippets:** A classic text expansion feature where a user-defined abbreviation (e.g., `::email`) is automatically replaced with pre-defined content (e.g., `my.email@example.com`).
2.  **Dynamic Prompt Augmentation:** An innovative feature allowing users to leverage a Large Language Model (LLM) directly in their workflow via a secure backend proxy.

The architectural vision of a **secure backend proxy** has been realized, decoupling the client from direct LLM API interaction, centralizing API key management, and enabling future scalability.

## 2. Current State of the Application

The project is now a **complete client-server application**. The backend has been developed and deployed to Google Cloud Run, and the client application is ready for its final configuration to communicate with the live service.

### Client Application (PySide6)

*   **UI Framework:** PySide6 for a cross-platform desktop application.
*   **Main Interface:** A modern, frameless dashboard window with a custom-styled dark theme, structured as a scalable two-pane layout.
*   **Core Components:**
    *   `Application`: The central orchestrator class.
    *   `KeystrokeListener`: A global keyboard hook that monitors user input.
    *   `SnippetUI`: The main dashboard widget.
    *   `LLMHandler`: Slated for final modification to call the deployed backend proxy.
    *   `Storage Classes`: For snippets, settings, and history.
*   **Implemented Features:** Full CRUD for snippets, a feature-rich settings page, and a history log for dynamic prompts.

### Backend Application (FastAPI)

*   **Framework:** FastAPI, providing a robust and modern API.
*   **Deployment:** The backend is containerized using **Docker** and deployed as a serverless application on **Google Cloud Run**.
*   **Core Components:**
    *   `main.py`: Defines the API endpoints, including `/api/v1/generate-prompt`.
    *   `vertex_ai_client.py`: A dedicated class that encapsulates all interaction with the Google GenAI SDK, keeping LLM logic separate.
    *   `settings.py`: Uses Pydantic to manage configuration and securely load secrets (like the Vertex AI project details) from environment variables, which are managed by Google Secret Manager in the cloud deployment.
    *   `pydantic_models.py`: Provides strict data validation for API requests and responses, ensuring data integrity.

## 3. Key Architectural Decisions & Past Solutions

*   **Backend Proxy Architecture:**
    *   **Problem:** The initial client-only design exposed the LLM API key, posing a significant security risk.
    *   **Solution:** A FastAPI backend was developed to act as a secure proxy. It encapsulates the API key and all LLM interaction logic. This resolves the security flaw and centralizes control for future enhancements like caching or rate limiting.

*   **UI Redesign (From Dialog to Dashboard):**
    *   **Problem:** The initial UI was not scalable.
    *   **Solution:** Refactored into a two-pane dashboard, allowing for easy addition of new feature pages like "Settings" and "History."

*   **LLM Command Orchestration & UI Feedback:**
    *   **Problem:** The UI would freeze during API calls, providing a poor user experience.
    *   **Solution:** Re-architected the signal/slot flow to provide immediate visual feedback ("Generating...") before initiating the time-consuming backend call.

*   **Concurrent Request Handling:**
    *   **Problem:** Rapid commands could corrupt the UI state.
    *   **Solution:** Implemented a state flag (`is_request_in_flight`) to lock the application, preventing new requests while one is in progress.

## 4. Outstanding Issues & Known Bugs

*   **Primary Unvalidated Area:** The connection between the client application and the newly deployed Google Cloud Run backend has **not been tested end-to-end**. It is unknown if the client can successfully communicate with the live service or if there are any CORS, authentication, or network-related issues.
*   **Usability Gap:** The `::Prompt(...)` command does not properly support pasting large blocks of text from the clipboard into the command itself. The `KeystrokeListener`'s buffer is designed for typed input and may trim or mishandle large pasted content.

## 5. Immediate Next Steps & Future Roadmap

The project has successfully completed the development and deployment phases of the backend. The immediate and critical priority is now validation and testing.

### Immediate Next Step

*   **End-to-End Testing of Deployed Service:**
    1.  **Update Client Configuration:** Modify the client application's configuration to point to the live Google Cloud Run service URL.
    2.  **Thorough Testing:** Conduct comprehensive testing of the dynamic prompt feature to ensure the client can successfully send requests to the deployed backend and receive responses.
    3.  **Monitor Cloud Logs:** Closely monitor the logs in Google Cloud Run during testing to identify and diagnose any errors in the deployed environment.

### Future Roadmap

With the MVP backend now deployed, the focus shifts to production-grade enhancements as outlined in **Phase 3** of the backend roadmap.

*   **Phase 3 - Enhancements:**
    *   **Advanced Error Monitoring & Alerting:** Integrate with Google Cloud's operations suite for proactive monitoring.
    *   **CI/CD Pipeline:** Set up a GitHub Actions workflow to automate testing, Docker image builds, and deployments to Cloud Run on code changes.
    *   **Caching Strategies:** Implement caching (e.g., Redis) to reduce latency and cost for repeated queries.
    *   **Rate Limiting:** Add rate limiting to the API endpoints to prevent abuse.