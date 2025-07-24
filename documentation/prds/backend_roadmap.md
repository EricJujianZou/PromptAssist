# FastAPI Backend Development Roadmap for Expandr

**Overall Goal:** To create a secure, scalable, and reliable FastAPI backend proxy that handles requests from the Expandr client application, interacts with Google Vertex AI for dynamic prompt generation, and returns the augmented prompts. This backend is crucial for managing API key security and enabling wider, safer use of the AI features.

## Phase 1: MVP Backend - Core Functionality & Local Deployment (Immediate Steps)

**Objective:** Build and test a functional backend locally that can receive requests, call Vertex AI, and return responses. Securely manage API keys from the outset.

### Week 1-2: Setup & Basic Endpoint

1.  **Project Setup & Structure:**
    *   **Action:** Create a new directory for the backend (e.g., `backend_service/` or `api/` at the root of your project).
    *   **Design:** This separates backend code from the client-side PySide6 application, promoting modularity.
    *   **Concepts:**
        *   **Project Structure:** Organizing code into logical directories for maintainability.
        *   **Modularity:** Breaking the system into independent components (client and server).
    *   **Best Practice:** Clear separation of concerns.

2.  **FastAPI & Uvicorn Installation:**
    *   **Action:** Add `fastapi` and `uvicorn[standard]` to a new `requirements_backend.txt` (or similar) in the backend directory. Set up a virtual environment for the backend if you haven't already for the main project, or ensure these are added to the existing one.
    *   **Design:** FastAPI is chosen for its modern features, speed, and `async` support. Uvicorn is a high-performance ASGI server.
    *   **Concepts:**
        *   **Virtual Environments:** Isolating project dependencies.
        *   **Dependency Management:** Using `requirements.txt` to list necessary packages.
        *   **ASGI Server (Uvicorn):** The server that runs your FastAPI application.
    *   **Best Practice:** Isolate dependencies; use a standard ASGI server.

3.  **Basic "Hello World" Endpoint:**
    *   **Action:** Create a `main.py` in the backend directory. Implement a simple `/` or `/health` GET endpoint that returns a JSON response (e.g., `{"status": "ok"}`).
    *   **Design:** Verifies that FastAPI and Uvicorn are set up correctly and the server can run.
    *   **Concepts:**
        *   **FastAPI Application Instance:** `app = FastAPI()`
        *   **Path Operation Decorator:** `@app.get("/")` to define an endpoint.
        *   **Path Operation Function:** An `async def` function that handles the request.
        *   **JSON Response:** Returning data in a standard web format.
    *   **Best Practice:** Start with the simplest possible working example.

4.  **Configuration Management (`.env` for Backend):**
    *   **Action:**
        *   Create a `.env` file *within the backend directory*.
        *   Add Vertex AI credentials (`VERTEX_AI_PROJECT`, `VERTEX_AI_LOCATION`, `GOOGLE_APPLICATION_CREDENTIALS` if using a service account key file) and model parameters (`LLM_MODEL_NAME`, `MAX_OUTPUT_TOKENS`, `TEMPERATURE`) to this backend `.env` file.
        *   Use `python-dotenv` and a Pydantic `Settings` class (FastAPI's recommended way) to load these configurations.
    *   **Design:** Centralizes backend-specific configuration, keeping secrets out of code and separate from client configuration. Pydantic provides validation.
    *   **Concepts:**
        *   **Environment Variables:** Storing configuration outside the codebase.
        *   **Pydantic `BaseSettings`:** For type-validated settings management in FastAPI.
        *   **Separation of Concerns:** Backend config is distinct from client config.
    *   **Best Practice:** Secure and validated configuration loading. **Ensure this backend `.env` file is in your main `.gitignore` file.**

### Week 2-3: Vertex AI Integration & Prompt Generation Endpoint

5.  **Vertex AI Client Initialization in Backend:**
    *   **Action:** Create a module (e.g., `vertex_ai_client.py`) in the backend to initialize the Vertex AI `GenerativeModel` using the settings loaded in the previous step.
    *   **Design:** Encapsulates Vertex AI interaction logic.
    *   **Concepts:**
        *   **Google Cloud SDK (`vertexai`):** The library for interacting with Vertex AI.
        *   **Service Account Authentication (Recommended for Backend):** If using a service account JSON key, ensure `GOOGLE_APPLICATION_CREDENTIALS` environment variable points to it.
    *   **Best Practice:** Abstract external service interactions.

6.  **`/generate_prompt` Endpoint:**
    *   **Action:**
        *   Define a POST endpoint (e.g., `/api/v1/generate_prompt`).
        *   It should accept a JSON payload containing the `user_query: str`. Use Pydantic models for request body validation.
        *   Call the Vertex AI client to generate the augmented prompt using the `user_query` and the configured meta-prompt/system instruction (which should also be part of the backend's configuration).
        *   Return the augmented prompt as a JSON response (e.g., `{"augmented_prompt": "..."}`).
    *   **Design:** This is the core functional endpoint for the client. Pydantic ensures data integrity.
    *   **Concepts:**
        *   **HTTP POST Method:** Used for sending data to create or update a resource.
        *   **Pydantic Models:** For request and response data validation and serialization.
        *   **API Versioning (e.g., `/v1/`):** Good practice for future API evolution.
    *   **Best Practice:** Clear API contract with validated inputs and outputs.

7.  **Error Handling in Backend:**
    *   **Action:** Implement `try-except` blocks within the `/generate_prompt` endpoint to catch potential errors from Vertex AI (e.g., API errors, timeouts) or internal issues. Return appropriate HTTP error responses (e.g., 500 for server error, 503 for service unavailable).
    *   **Design:** Makes the backend robust and provides meaningful error feedback.
    *   **Concepts:**
        *   **FastAPI `HTTPException`:** For returning standard HTTP error responses.
        *   **Specific Exception Handling:** Catching errors from the `vertexai` library.
    *   **Best Practice:** Graceful error handling is crucial for API reliability.

8.  **Logging in Backend:**
    *   **Action:** Implement structured logging (e.g., using Python's `logging` module, configured in FastAPI) to record requests, responses, errors, and key events.
    *   **Design:** Essential for debugging and monitoring.
    *   **Concepts:**
        *   **Logging Levels:** (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        *   **Log Formatters & Handlers:** Customizing log output and destination.
    *   **Best Practice:** Comprehensive logging.

### Week 4: Client-Side Integration & Local Testing

9.  **Modify Client (`LLMPromptHandler.py`):**
    *   **Action:**
        *   Remove direct Vertex AI API calls and credential handling from [`LLMPromptHandler.py`](src/core/llm_prompt_handler.py).
        *   Add a configuration for `BACKEND_API_URL` in the client's `.env` file (e.g., `http://localhost:8000` for local backend testing).
        *   Use an HTTP client library (e.g., `requests` or `httpx` - `httpx` is good for async compatibility if the client also becomes async) to make POST requests to the backend's `/api/v1/generate_prompt` endpoint.
        *   Handle responses and errors from the backend.
    *   **Design:** Decouples client from direct LLM interaction, delegating to the backend proxy.
    *   **Concepts:**
        *   **HTTP Client Libraries:** Making requests to web services.
        *   **API Consumption:** Client interacting with the backend API.
    *   **Best Practice:** Client should be unaware of the ultimate LLM provider details.

10. **End-to-End Local Testing:**
    *   **Action:** Run both the PySide6 client and the FastAPI backend locally. Trigger the `::Prompt(...)` command in the client and verify:
        *   The request hits the backend.
        *   The backend calls Vertex AI.
        *   The augmented prompt is returned to the client and displayed.
        *   Errors are handled gracefully.
    *   **Design:** Validates the entire workflow.
    *   **Best Practice:** Thorough testing before considering deployment.

## Phase 2: Containerization & Cloud Deployment (MVP Release)

**Objective:** Package the backend into a Docker container and deploy it to Google Cloud Run, making it accessible to users beyond the local machine.

### Week 5-6: Dockerization & GCR/Artifact Registry

11. **Create `Dockerfile` for Backend:**
    *   **Action:** Write a `Dockerfile` in the backend directory to:
        *   Use an official Python base image.
        *   Set up a working directory.
        *   Copy `requirements_backend.txt` and install dependencies.
        *   Copy the backend application code.
        *   Expose the port Uvicorn will run on (e.g., 8000).
        *   Specify the `CMD` to run Uvicorn (e.g., `uvicorn main:app --host 0.0.0.0 --port 8000`).
    *   **Design:** Defines a reproducible environment for the backend. `--host 0.0.0.0` is important for Docker.
    *   **Concepts:**
        *   **Dockerfile Instructions:** (`FROM`, `WORKDIR`, `COPY`, `RUN`, `EXPOSE`, `CMD`).
        *   **Containerization:** Packaging an application and its dependencies.
    *   **Best Practice:** Minimal and efficient Docker image.

12. **Build Docker Image Locally:**
    *   **Action:** Use `docker build` to create the image. Test running the container locally.
    *   **Design:** Verifies the `Dockerfile` and application work correctly within a container.
    *   **Best Practice:** Test locally before pushing to a registry.

13. **Push Image to Google Artifact Registry (or GCR):**
    *   **Action:**
        *   Set up Google Artifact Registry in your GCP project.
        *   Authenticate Docker with Artifact Registry.
        *   Tag your Docker image appropriately (e.g., `us-central1-docker.pkg.dev/YOUR_PROJECT_ID/expandr-repo/expandr-backend:v0.1.0`).
        *   Push the image using `docker push`.
    *   **Design:** Stores the deployable artifact in a secure, managed Google Cloud service.
    *   **Concepts:**
        *   **Container Registry:** A storage system for Docker images.
        *   **Image Tagging:** Versioning images.
    *   **Best Practice:** Use a private registry for your application images.

### Week 6-7: Deployment to Google Cloud Run

14. **Deploy to Google Cloud Run:**
    *   **Action:**
        *   Create a new Cloud Run service.
        *   Configure it to use the image pushed to Artifact Registry.
        *   Set necessary environment variables (Vertex AI credentials, model config) securely within the Cloud Run service configuration (use Secret Manager for sensitive values).
        *   Configure CPU, memory, min/max instances, concurrency.
        *   Allow unauthenticated invocations (if the client doesn't send auth tokens to your proxy) or set up IAM for authentication if needed.
    *   **Design:** Leverages serverless infrastructure for scalability and managed operations.
    *   **Concepts:**
        *   **Serverless Deployment:** Running code without managing underlying servers.
        *   **Cloud Run Configuration:** Setting up environment, resources, and scaling.
        *   **Google Secret Manager:** Securely storing and accessing API keys and other secrets for Cloud Run services.
    *   **Best Practice:** Securely manage secrets in the cloud environment; configure appropriate resources.

15. **Update Client with Cloud Run URL:**
    *   **Action:** Once Cloud Run provides a service URL, update the `BACKEND_API_URL` in the client's configuration (perhaps through a new `.env` setting or a user-configurable setting in the UI for flexibility).
    *   **Design:** Points the client to the live, deployed backend.

16. **Testing Deployed Service:**
    *   **Action:** Thoroughly test the client application interacting with the deployed Cloud Run backend. Monitor logs in Cloud Run.
    *   **Design:** Ensures the deployed system works as expected.

## Phase 3: Enhancements & Future Steps (Post-MVP)

**Objective:** Improve robustness, add features, and optimize the backend.

### Timeline: Ongoing after MVP

17. **Advanced Error Monitoring & Alerting:**
    *   **Action:** Integrate with Google Cloud's operations suite (Logging, Monitoring, Error Reporting) for better insights and alerts on backend issues.
    *   **Best Practice:** Proactive monitoring.

18. **Backend API Authentication/Authorization (If needed):**
    *   **Action:** If the backend needs to be protected beyond just being an internal proxy, implement API key authentication or OAuth2 for client requests to the backend.
    *   **Design:** Secures your backend API itself.
    *   **Concepts:**
        *   **FastAPI Security Utilities:** (`Security`, `HTTPBearer`, etc.).

19. **Caching Strategies:**
    *   **Action:** Consider caching frequent or identical Vertex AI requests/responses (e.g., using Redis or in-memory cache with FastAPI-Cache) to reduce latency and cost, if applicable.
    *   **Design:** Improves performance and efficiency.

20. **Rate Limiting:**
    *   **Action:** Implement rate limiting on API endpoints to prevent abuse and manage costs.
    *   **Design:** Protects your service and downstream APIs.

21. **CI/CD Pipeline:**
    *   **Action:** Set up a Continuous Integration/Continuous Deployment pipeline (e.g., using GitHub Actions, Google Cloud Build) to automate testing, building Docker images, and deploying to Cloud Run on code changes.
    *   **Best Practice:** Automate the deployment process for reliability and speed.

22. **User-Configurable Meta-Prompts via API:**
    *   **Action:** Extend the `/generate_prompt` endpoint or add new ones to allow the client to specify different meta-prompts or system instructions, if this feature is desired (as per [`README.md`](README.md) roadmap).
    *   **Design:** Increases flexibility for the user.

23. **Asynchronous Task Handling for Long Vertex AI Calls (If needed):**
    *   **Action:** If some Vertex AI calls become very long, explore background tasks in FastAPI (e.g., using `BackgroundTasks` or Celery) so the client doesn't have to wait for an immediate HTTP response. The client would then poll for results or receive a callback.
    *   **Design:** Improves client responsiveness for long operations.

---
