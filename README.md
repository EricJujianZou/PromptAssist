# PromptAssist 🚀

**Your Personal AI-Powered Prompt Manager**
[![Quick Demo](https://img.youtube.com/vi/oFcH-L0bwaI/maxresdefault.jpg)](https://youtu.be/oFcH-L0bwaI)
---

Installation: https://github.com/EricJujianZou/PromptAssist/releases/tag/v1.0.0

## What is PromptAssist?

PromptAssist is a lightweight Windows utility that runs in your system tray and gives you two powerful abilities in any application:

-   **⚡ Snippet Expansion:** Type a short command (like `::email`) and have it instantly replaced with a longer piece of text. Perfect for code boilerplate, common replies, or anything you type frequently. Edit, create, and delete text snippets by accessing the UI in your system tray.
-   **🧠 LLM Augmentation:** Use a special prefix (::Prompt([your-prompt-here) to transform your prompt with more accuracy and context.

## Key Features

-   **System-Wide:** Works in your code editor, browser, notepad, and more.
-   **Lightweight:** Runs quietly in the system tray with minimal resource usage.
-   **Customizable:** Easily add, edit, and manage your snippets through a simple dashboard.
-   **Secure:** Connects to your own self-hosted API backend for LLM prompts.
-   **No Installation:** Just download and run the `.exe` file to use my Google Cloud backend.

## Getting Started - Use The App

1.  Go to the latest [release page](https://github.com/EricJujianZou/PromptAssist/releases/tag/v1.0.0)
2.  Download the `PromptAssist.exe` file or follow the instructions to clone for yourself.
3.  Run it! The PromptAssist icon will appear in your system tray.

## How to Use

-   **Double-click** the tray icon to open the Dashboard and manage your snippets.
-   **Type a snippet command** (e.g., `::sig`) in any text field to expand it.
-   **Type an LLM command** (e.g., `::Prompt(explain Bayes' Theroem to me)`) to transform your prompt to follow prompt engineering practices.

## For Developers: Running from Source

This guide provides step-by-step instructions to set up and run the entire application on your local machine. The project consists of two main parts that run separately:

1.  **The Backend:** A Python server using FastAPI that connects to the language model.
2.  **The Client:** A Python GUI application using PySide6 that runs in your system tray.

### Prerequisites

Before you begin, ensure you have the following installed on your system:

-   [**Python 3.9+**](https://www.python.org/downloads/)
-   [**Git**](https://git-scm.com/downloads/)
-   [**Docker Desktop**](https://www.docker.com/products/docker-desktop/) (for running a local Redis database)

### Step 1: Clone the Repository

First, get the source code onto your machine. Open your terminal, navigate to where you store your projects, and run:

```shell
[git clone https://github.com/](https://github.com/EricJujianZou/PromptAssist.git)

```

### Step 2: Set Up the Local Redis Database

The backend uses Redis for rate limiting to prevent abuse and control costs. We will run Redis locally using Docker.

1.  Make sure Docker Desktop is running on your machine.
2.  In your terminal, run the following command to start a Redis container:

    ```shell
    docker run -d -p 6379:6379 --name prompt-redis redis
    ```

    This command downloads the official Redis image, starts it as a background process (`-d`), and makes it available on the standard Redis port (`6379`). It will automatically restart whenever you start Docker.

### Step 3: Set Up the Backend API

Now, let's get the "brain" of the application running.

1.  **Navigate to the backend directory:**

    ```shell
    cd backend_api
    ```

2.  **Create and activate a virtual environment:**

    ```shell
    # Create the virtual environment folder named 'venv'
    python -m venv venv

    # Activate it (the command is different for Windows vs. macOS/Linux)
    # On Windows:
    .\venv\Scripts\activate
    #using Conda:
    conda activate venv
    ```
    Your terminal prompt should now change to show `(venv)`, indicating the virtual environment is active.

3.  **Install dependencies:**

    ```shell
    pip install -r requirements_backend.txt
    ```

4.  **Configure environment variables:**
    -   In the `backend_api` folder, create a new file named `.env`.
    -   Copy the entire contents of `backend_api/.env.example` and paste them into your new `.env` file.
    -   Fill in the placeholder values in your `.env` file:
        -   `VERTEX_AI_PROJECT`: Your Google Cloud Project ID.
        -   `VERTEX_AI_LOCATION`: The region for your Vertex AI resources (e.g., `us-central1`).
        -   `BACKEND_API_KEY`: **Create a long, random, secret key.** This is like a password that your client will use to talk to this backend.
        -   `REDIS_URL`: Leave this as `redis://localhost` to connect to the local Docker container you started.

5.  **Authenticate with Google Cloud:**
    For the backend to use your Google account for AI services, you need to log in via the terminal.
    ```shell
    gcloud auth application-default login
    ```
    This will open a browser window for you to log in to your Google account.

6.  **Run the backend server:**

    ```shell
    uvicorn main:app --reload
    ```
    You should see output indicating the server is running on `http://127.0.0.1:8000`. **Leave this terminal running.**

### Step 4: Set Up the Client GUI

With the backend running, open a **new, separate terminal** to set up the user-facing application.

1.  **Navigate to the project root directory** (the parent of `backend_api`).

2.  **Create and activate a separate virtual environment:**

    ```shell
    python -m venv venv_client
    # On Windows:
    .\venv_client\Scripts\activate
    ```
    Your new terminal prompt should now show `(venv_client)`.

3.  **Install dependencies:**
    *(Note: The client's requirements file is in the `documentation` folder).*

    ```shell
    pip install -r documentation/requirements.txt
    ```

4.  **Configure environment variables:**
    -   In the `src` folder, create a new file named `.env`.
    -   Copy the contents of `src/.env.example` and paste them into your new `src/.env` file.
    -   Fill in the placeholder values:
        -   `BACKEND_API_URL`: Set this to `http://127.0.0.1:8000`.
        -   `BACKEND_API_KEY`: **This is critical.** Paste the exact same secret key you created for the backend's `.env` file in Step 3.

5.  **Run the client application:**

    ```shell
    python run.py
    ```

The application icon should now appear in your system tray. It is fully connected to your local backend, which is connected to your local Redis database. You now have the complete system running for development and testing!

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
