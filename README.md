# 🚀 Expandr: Your AI Prompt Assistant

[![Demo Screenshot](documentation/demo%20ss.png)](documentation/demo%20ss.png)

**Expandr** elevates your productivity by combining lightning-fast text expansion for your common phrases with cutting-edge AI to dynamically generate optimized prompts for Large Language Models (LLMs), all seamlessly integrated into your workflow.

Stop retyping the same text and struggling to craft the perfect LLM query. Start working smarter, faster, and get better results from your AI interactions!

---

## 🌟 Key Features

### ✨ Smart Snippet Expansion
*   **⌨️ Instant Command-Based Snippets:** Type a short command (e.g., `::email`) and watch it instantly transform into your predefined text, in any application.
*   **📂 Intuitive Snippet Management:** Easily add, edit, and delete your static snippets through a clean and user-friendly graphical interface (GUI) with dark/light theme support.
*   **🔒 Local & Private Storage:** All your static snippets are stored locally in a `config.json` file (`%APPDATA%\snippet_app\config.json`), ensuring your data remains private and under your control. No cloud dependency for core snippet functionality.

### 🤖 AI-Powered Dynamic Prompts (New!)
*   **⚡ Dynamic Prompt Generation:** Type `::Prompt(your natural language query for an LLM)` followed by the `Space` key. Expandr sends your query to a powerful AI (Google Vertex AI's Gemini models) to transform it into a highly effective, detailed, and well-structured prompt.
*   **🎯 Optimized LLM Interactions:** Get better, more relevant responses from your favorite LLMs by starting with a superior, AI-augmented prompt. Ideal for both novice users wanting better results and expert users seeking efficiency for unique tasks.
*   **💬 Inline Feedback & Notifications:**
    *   See `Generating prompt...` appear immediately after triggering the command.
    *   The augmented prompt is automatically typed out for you.
    *   The generated prompt is also **copied to your clipboard**, and a system sound notifies you, so you can paste it anywhere, anytime.
    *   Receive an inline error message (e.g., `[Prompt Generation Failed. Try Again]`) if the AI call doesn't succeed.
*   **⏱️ Fast Turnaround:** Designed to meet a sub-5-second target from command trigger to augmented prompt appearance (network and API latency dependent).

### 🎯 Seamless Workflow & User Experience
*   **🛠️ System Tray Integration:** Runs quietly in the background and is always accessible via a system tray icon.
*   **🌐 Universal Compatibility:** Works across most applications where you can type text.
*   **⚡ Low Latency:** Near-instant replacement for static snippets and optimized performance for dynamic prompt generation.
*   **🎨 Customizable UI:** Modify UI styles via `src/style.qss`.
*   **🛡️ Privacy-Focused:** No telemetry or unnecessary data collection.

---

## 🤔 Why Expandr?

*   **Boost Your Productivity:** Drastically reduce time spent on repetitive typing and crafting complex LLM queries.
*   **Elevate Your LLM Interactions:** Transform simple ideas into powerful prompts that unlock the full potential of AI models.
*   **Simplify Your Workflow:** Access both static text snippets and dynamic AI assistance without leaving your current application.
*   **Empower Everyone:** Whether you're new to prompt engineering or a seasoned pro, Expandr helps you achieve better results with less effort.

---

## ⚙️ Installation

### Prerequisites
*   Python 3.10+
*   Windows 10/11 (macOS/Linux support is planned)
*   An active internet connection (for AI Dynamic Prompt Generation)
*   Google Cloud Vertex AI setup for the dynamic prompt feature (see [PRD Addendum](documentation/promptGenerationPRD.md) for details on API and authentication).

### Steps
1.  **Clone the repository:**
    ```sh
    git clone https://github.com/your-username/your-repository-name.git
    cd your-repository-name
    ```
2.  **Set up a virtual environment (recommended):**
    ```sh
    python -m venv venv
    venv\Scripts\activate  # On Windows
    # source venv/bin/activate  # On macOS/Linux
    ```
3.  **Install dependencies:**
    ```sh
    pip install -r documentation/requirements.txt 
    # For development, also consider requirements-dev.txt
    ```
4.  **Configure Environment Variables (for AI Dynamic Prompts):**
    Create a `.env` file in the project root directory and add your Google Cloud Vertex AI credentials. Refer to `llm_prompt_handler.py` and the [Vertex AI documentation](documentation/vertex_ai_docs.md) for required variables (e.g., `VERTEX_AI_PROJECT`, `VERTEX_AI_LOCATION`, `LLM_MODEL_NAME`).
    Example `.env` content:
    ```env
    VERTEX_AI_PROJECT="your-gcp-project-id"
    VERTEX_AI_LOCATION="your-gcp-region"
    LLM_MODEL_NAME="gemini-1.5-flash-001" 
    # Or other compatible Gemini model
    MAX_OUTPUT_TOKENS=500
    TEMPERATURE=0.3
    API_RETRY_COUNT=2
    ```
5.  **Run the application:**
    ```sh
    python src/main.py
    ```

---

## 🚦 Usage

### Managing & Using Static Snippets
1.  **Open Snippet Manager:** Right-click the system tray icon and select "Open Snippet Manager".
2.  **Add a New Snippet:**
    *   Click "New".
    *   Enter a **Command** (e.g., `::greet`). Commands must start with `::` and should not contain spaces.
    *   Enter the **Text** you want the command to expand to.
    *   Click "Save".
3.  **Using a Snippet:** Type your command (e.g., `::greet`) in any text field, followed by a `Space` (or `Enter`, `Tab` depending on trigger configuration). The command will be automatically deleted and replaced with your snippet text.
4.  **Edit/Delete Snippets:** Select a snippet in the manager to modify or delete it.

### Generating Dynamic AI Prompts
1.  **Trigger the Command:** In any text field where you want to generate an LLM prompt, type:
    `::Prompt(your natural language request for an LLM)`
    For example: `::Prompt(draft a polite follow-up email to a client who missed our last demo)`
2.  **Press Space:** After typing your request within the parentheses and closing it, press the `Space` key.
3.  **AI Augmentation:**
    *   The original command `::Prompt(...) ` will be replaced with `Generating prompt...`.
    *   Expandr will then call the Vertex AI API.
    *   Once the AI generates the augmented prompt, `Generating prompt...` will be deleted and replaced by the new, optimized prompt.
    *   Simultaneously, the augmented prompt is **copied to your clipboard**, and a system sound will play. You can then paste this prompt into your LLM interface or any other application.
4.  **Error Handling:** If the API call fails after retries, an error message like `[Prompt Generation Failed. Try Again]` will be displayed inline.

---

## 🛠️ Configuration

*   **Snippet Storage:** Static snippets are stored in `%APPDATA%\snippet_app\config.json`. You can manually back up this file.
*   **UI Styling:** Customize the application's appearance by modifying `src/style.qss`.
*   **AI Prompt Behavior:** Parameters like `MAX_OUTPUT_TOKENS`, `TEMPERATURE`, and `API_RETRY_COUNT` for the AI prompt generation can be configured in your `.env` file (see `src/core/llm_prompt_handler.py` for details).

---

## 💻 Technology Stack

*   **Python 3.10+**
*   **PySide6:** For the modern, native Graphical User Interface (GUI).
*   **Google Cloud Vertex AI (Gemini Models):** Powers the dynamic AI prompt augmentation.
*   **Keyboard:** For global keyboard hooking and input simulation.
*   **Pyperclip:** For clipboard operations.
*   **python-dotenv:** For managing environment variables.

---

## 🗺️ Roadmap & Planned Features

*   🔒 **Backend Proxy Server:** Implement a secure backend proxy for managing Vertex AI API credentials, enhancing security for wider distribution (Mandatory for MVP release as per [PRD Addendum](documentation/promptGenerationPRD.md)).
*   🔄 **Focus Change Handling:** More robust abortion of API calls and typing simulation if application focus changes.
*   🌐 **Cloud Sync:** Optional synchronization of static snippets via services like Google Drive or Dropbox.
*   📝 **Snippet Variables:** Support for dynamic variables within static snippets (e.g., `{{date}}`, `{{clipboard}}`).
*   🍎🐧 **Cross-Platform Support:** Expanded support for macOS and Linux.
*   ⚙️ **User-Configurable Meta-Prompts:** Allow users to define or select different meta-prompts/personas for the AI.
*   🔔 **Enhanced Notifications:** More detailed system tray notifications for API states and errors.

---

## 🤝 Contributing

Contributions are welcome! If you have ideas for improvements or want to fix a bug, please follow these steps:

1.  **Fork the repository.**
2.  **Create a feature branch:**
    ```sh
    git checkout -b feature/your-amazing-feature
    ```
3.  **Commit your changes:**
    ```sh
    git commit -m "Add: Your amazing feature"
    ```
4.  **Push to the branch:**
    ```sh
    git push origin feature/your-amazing-feature
    ```
5.  **Open a Pull Request.**

Please ensure your code adheres to project standards and includes relevant documentation or tests.

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` file for more information.

---

## 🙏 Acknowledgments

*   Icons by [Feather Icons](https://feathericons.com/)
*   Built with [PySide6](https://www.qt.io/qt-for-python)
*   AI Prompt Generation powered by [Google Cloud Vertex AI](https://cloud.google.com/vertex-ai)

---

## 📬 Contact

*   **Eric Zou**
*   **Email:** e2zou@uwaterloo.ca
*   **GitHub:** [@EricJujianZou](https://github.com/EricJujianZou)
```
This README aims to be comprehensive, covering the project's enhanced value proposition, features, setup, and usage for both static snippets and the new dynamic AI prompt generation. Remember to replace placeholder URLs like `https://github.com/your-username/your-repository-name.git` with your actual repository details.# 🚀 Expandr: Your Intelligent Text Expansion & AI Prompt Assistant

[![Demo Screenshot](documentation/demo%20ss.png)](documentation/demo%20ss.png)

**Expandr** elevates your productivity by combining lightning-fast text expansion for your common phrases with cutting-edge AI to dynamically generate optimized prompts for Large Language Models (LLMs), all seamlessly integrated into your workflow.

Stop retyping the same text and struggling to craft the perfect LLM query. Start working smarter, faster, and get better results from your AI interactions!

---

## 🌟 Key Features

### ✨ Smart Snippet Expansion
*   **⌨️ Instant Command-Based Snippets:** Type a short command (e.g., `::email`) and watch it instantly transform into your predefined text, in any application.
*   **📂 Intuitive Snippet Management:** Easily add, edit, and delete your static snippets through a clean and user-friendly graphical interface (GUI) with dark/light theme support.
*   **🔒 Local & Private Storage:** All your static snippets are stored locally in a `config.json` file (`%APPDATA%\snippet_app\config.json`), ensuring your data remains private and under your control. No cloud dependency for core snippet functionality.

### 🤖 AI-Powered Dynamic Prompts (New!)
*   **⚡ Dynamic Prompt Generation:** Type `::Prompt(your natural language query for an LLM)` followed by the `Space` key. Expandr sends your query to a powerful AI (Google Vertex AI's Gemini models) to transform it into a highly effective, detailed, and well-structured prompt.
*   **🎯 Optimized LLM Interactions:** Get better, more relevant responses from your favorite LLMs by starting with a superior, AI-augmented prompt. Ideal for both novice users wanting better results and expert users seeking efficiency for unique tasks.
*   **💬 Inline Feedback & Notifications:**
    *   See `Generating prompt...` appear immediately after triggering the command.
    *   The augmented prompt is automatically typed out for you.
    *   The generated prompt is also **copied to your clipboard**, and a system sound notifies you, so you can paste it anywhere, anytime.
    *   Receive an inline error message (e.g., `[Prompt Generation Failed. Try Again]`) if the AI call doesn't succeed.
*   **⏱️ Fast Turnaround:** Designed to meet a sub-5-second target from command trigger to augmented prompt appearance (network and API latency dependent).

### 🎯 Seamless Workflow & User Experience
*   **🛠️ System Tray Integration:** Runs quietly in the background and is always accessible via a system tray icon.
*   **🌐 Universal Compatibility:** Works across most applications where you can type text.
*   **⚡ Low Latency:** Near-instant replacement for static snippets and optimized performance for dynamic prompt generation.
*   **🎨 Customizable UI:** Modify UI styles via `src/style.qss`.
*   **🛡️ Privacy-Focused:** No telemetry or unnecessary data collection.

---

## 🤔 Why Expandr?

*   **Boost Your Productivity:** Drastically reduce time spent on repetitive typing and crafting complex LLM queries.
*   **Elevate Your LLM Interactions:** Transform simple ideas into powerful prompts that unlock the full potential of AI models.
*   **Simplify Your Workflow:** Access both static text snippets and dynamic AI assistance without leaving your current application.
*   **Empower Everyone:** Whether you're new to prompt engineering or a seasoned pro, Expandr helps you achieve better results with less effort.

---

## ⚙️ Installation

### Prerequisites
*   Python 3.10+
*   Windows 10/11 (macOS/Linux support is planned)
*   An active internet connection (for AI Dynamic Prompt Generation)
*   Google Cloud Vertex AI setup for the dynamic prompt feature (see [PRD Addendum](documentation/promptGenerationPRD.md) for details on API and authentication).

### Steps
1.  **Clone the repository:**
    ```sh
    git clone https://github.com/your-username/your-repository-name.git
    cd your-repository-name
    ```
2.  **Set up a virtual environment (recommended):**
    ```sh
    python -m venv venv
    venv\Scripts\activate  # On Windows
    # source venv/bin/activate  # On macOS/Linux
    ```
3.  **Install dependencies:**
    ```sh
    pip install -r documentation/requirements.txt 
    # For development, also consider requirements-dev.txt
    ```
4.  **Configure Environment Variables (for AI Dynamic Prompts):**
    Create a `.env` file in the project root directory and add your Google Cloud Vertex AI credentials. Refer to `llm_prompt_handler.py` and the [Vertex AI documentation](documentation/vertex_ai_docs.md) for required variables (e.g., `VERTEX_AI_PROJECT`, `VERTEX_AI_LOCATION`, `LLM_MODEL_NAME`).
    Example `.env` content:
    ```env
    VERTEX_AI_PROJECT="your-gcp-project-id"
    VERTEX_AI_LOCATION="your-gcp-region"
    LLM_MODEL_NAME="gemini-1.5-flash-001" 
    # Or other compatible Gemini model
    MAX_OUTPUT_TOKENS=500
    TEMPERATURE=0.3
    API_RETRY_COUNT=2
    ```
5.  **Run the application:**
    ```sh
    python src/main.py
    ```

---

## 🚦 Usage

### Managing & Using Static Snippets
1.  **Open Snippet Manager:** Right-click the system tray icon and select "Open Snippet Manager".
2.  **Add a New Snippet:**
    *   Click "New".
    *   Enter a **Command** (e.g., `::greet`). Commands must start with `::` and should not contain spaces.
    *   Enter the **Text** you want the command to expand to.
    *   Click "Save".
3.  **Using a Snippet:** Type your command (e.g., `::greet`) in any text field, followed by a `Space` (or `Enter`, `Tab` depending on trigger configuration). The command will be automatically deleted and replaced with your snippet text.
4.  **Edit/Delete Snippets:** Select a snippet in the manager to modify or delete it.

### Generating Dynamic AI Prompts
1.  **Trigger the Command:** In any text field where you want to generate an LLM prompt, type:
    `::Prompt(your natural language request for an LLM)`
    For example: `::Prompt(draft a polite follow-up email to a client who missed our last demo)`
2.  **Press Space:** After typing your request within the parentheses and closing it, press the `Space` key.
3.  **AI Augmentation:**
    *   The original command `::Prompt(...) ` will be replaced with `Generating prompt...`.
    *   Expandr will then call the Vertex AI API.
    *   Once the AI generates the augmented prompt, `Generating prompt...` will be deleted and replaced by the new, optimized prompt.
    *   Simultaneously, the augmented prompt is **copied to your clipboard**, and a system sound will play. You can then paste this prompt into your LLM interface or any other application.
4.  **Error Handling:** If the API call fails after retries, an error message like `[Prompt Generation Failed. Try Again]` will be displayed inline.

---

## 🛠️ Configuration

*   **Snippet Storage:** Static snippets are stored in `%APPDATA%\snippet_app\config.json`. You can manually back up this file.
*   **UI Styling:** Customize the application's appearance by modifying `src/style.qss`.
*   **AI Prompt Behavior:** Parameters like `MAX_OUTPUT_TOKENS`, `TEMPERATURE`, and `API_RETRY_COUNT` for the AI prompt generation can be configured in your `.env` file (see `src/core/llm_prompt_handler.py` for details).

---

## 💻 Technology Stack

*   **Python 3.10+**
*   **PySide6:** For the modern, native Graphical User Interface (GUI).
*   **Google Cloud Vertex AI (Gemini Models):** Powers the dynamic AI prompt augmentation.
*   **Keyboard:** For global keyboard hooking and input simulation.
*   **Pyperclip:** For clipboard operations.
*   **python-dotenv:** For managing environment variables.

---

## 🗺️ Roadmap & Planned Features

*   🔒 **Backend Proxy Server:** Implement a secure backend proxy for managing Vertex AI API credentials, enhancing security for wider distribution (Mandatory for MVP release as per [PRD Addendum](documentation/promptGenerationPRD.md)).
*   🔄 **Focus Change Handling:** More robust abortion of API calls and typing simulation if application focus changes.
*   🌐 **Cloud Sync:** Optional synchronization of static snippets via services like Google Drive or Dropbox.
*   📝 **Snippet Variables:** Support for dynamic variables within static snippets (e.g., `{{date}}`, `{{clipboard}}`).
*   🍎🐧 **Cross-Platform Support:** Expanded support for macOS and Linux.
*   ⚙️ **User-Configurable Meta-Prompts:** Allow users to define or select different meta-prompts/personas for the AI.
*   🔔 **Enhanced Notifications:** More detailed system tray notifications for API states and errors.

---

## 🤝 Contributing

Contributions are welcome! If you have ideas for improvements or want to fix a bug, please follow these steps:

1.  **Fork the repository.**
2.  **Create a feature branch:**
    ```sh
    git checkout -b feature/your-amazing-feature
    ```
3.  **Commit your changes:**
    ```sh
    git commit -m "Add: Your amazing feature"
    ```
4.  **Push to the branch:**
    ```sh
    git push origin feature/your-amazing-feature
    ```
5.  **Open a Pull Request.**

Please ensure your code adheres to project standards and includes relevant documentation or tests.

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` file for more information.

---

## 🙏 Acknowledgments

*   Icons by [Feather Icons](https://feathericons.com/)
*   Built with [PySide6](https://www.qt.io/qt-for-python)
*   AI Prompt Generation powered by [Google Cloud Vertex AI](https://cloud.google.com/vertex-ai)

---

## 📬 Contact

*   **Eric Zou**
*   **Email:** e2zou@uwaterloo.ca
*   **GitHub:** [@EricJujianZou](https://github.com/EricJujianZou)
```
