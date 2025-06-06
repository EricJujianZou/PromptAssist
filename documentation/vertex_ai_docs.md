This document summarizes key information for using the `google-generativeai` Python SDK to interact with Google's generative AI models like Gemini.

**Official Documentation:** [https://googleapis.github.io/python-genai/](https://googleapis.github.io/python-genai/)

## 1. Installation

Install the library using pip:

```bash
pip install google-generativeai
```

## 2. Authentication

To use the API, you need an API key.

1.  **Get an API Key:** Obtain an API key from Google AI Studio (formerly MakerSuite).
2.  **Set API Key:**
    *   **Environment Variable (Recommended):** Set the `GOOGLE_API_KEY` environment variable. The library will automatically pick it up.
        ```bash
        export GOOGLE_API_KEY="YOUR_API_KEY"
        ```
    *   **In Code (Less Recommended for Production):** Pass the API key when configuring the client.
        ```python
        import google.generativeai as genai

        genai.configure(api_key="YOUR_API_KEY")
        ```

## 3. Quickstart: Generating Text

Here's a basic example of generating text from a prompt:

```python
import google.generativeai as genai

# Configure with your API key (if not using environment variable)
# genai.configure(api_key="YOUR_API_KEY")

# Choose a model
# List available models:
# for m in genai.list_models():
#   if 'generateContent' in m.supported_generation_methods:
#     print(m.name)
# Example: models/gemini-1.0-pro, models/gemini-1.5-flash-latest

model = genai.GenerativeModel('gemini-1.5-flash-latest') # Or your preferred model

# Provide a prompt
prompt = "What is the meaning of life?"

# Generate content
response = model.generate_content(prompt)

# Print the response
print(response.text)

# Access other parts of the response if needed
# print(response.prompt_feedback)
# print(response.candidates)
```

## 4. Core Concepts

### 4.1. Models

*   **Listing Models:** You can list available models and their capabilities.
    ```python
    import google.generativeai as genai

    for m in genai.list_models():
      print(f"Model Name: {m.name}")
      print(f"  Supported Methods: {m.supported_generation_methods}")
      # print(f"  Description: {m.description}")
      print("-" * 20)
    ```
*   **Choosing a Model:** Select a model appropriate for your task (e.g., text generation, chat, vision). Common models include `gemini-1.0-pro`, `gemini-1.5-pro-latest`, `gemini-1.5-flash-latest`.

### 4.2. `GenerativeModel` Class

This is the main class for interacting with a specific model.

```python
model = genai.GenerativeModel('model-name')
```

### 4.3. Generating Content (`generate_content`)

*   **Simple Text Prompt:**
    ```python
    response = model.generate_content("Tell me a joke.")
    print(response.text)
    ```
*   **Multi-turn Conversations (Chat):** Use `model.start_chat()` for conversational interactions.
    ```python
    chat = model.start_chat(history=[]) # Optional: provide initial history

    response = chat.send_message("Hello! Can you tell me about Large Language Models?")
    print(response.text)

    response = chat.send_message("How do they work?")
    print(response.text)

    # Access chat history
    # for message in chat.history:
    #   print(f'{message.role}: {message.parts[0].text}')
    ```
*   **Streaming Responses:** For long generations, you can stream the response as it's generated.
    ```python
    response = model.generate_content("Write a long story about a space explorer.", stream=True)
    for chunk in response:
      print(chunk.text, end='')
    ```
*   **Providing Images (Multimodal Input with Vision Models):**
    Models like `gemini-pro-vision` or `gemini-1.5-flash-latest` can process images.
    ```python
    import PIL.Image

    img = PIL.Image.open('path/to/your/image.jpg')
    # For models that support multimodal input
    # model = genai.GenerativeModel('gemini-1.5-flash-latest') # or gemini-pro-vision
    # response = model.generate_content(["Describe this image:", img])
    # print(response.text)
    ```
    You can also pass image data directly (e.g., bytes).

### 4.4. Content Structure (Parts and Roles)

*   Content is structured into `parts` (e.g., text, image data) and associated with a `role` (e.g., `user`, `model`).
*   For `generate_content`, you can pass a list of parts or strings.
    ```python
    # Example of structured content (more relevant for chat history or complex inputs)
    # from google.generativeai.types import HarmCategory, HarmBlockThreshold
    # contents = [
    #     {'role':'user',
    #      'parts': ["Briefly explain how a computer works."]},
    #     {'role':'model',
    #      'parts': ["A computer takes input, processes it using a CPU and memory, and then produces output."]}
    # ]
    # response = model.generate_content(contents)
    ```

### 4.5. Generation Configuration (`GenerationConfig`)

Control generation parameters like temperature, max output tokens, top_p, top_k, and stop sequences.

```python
from google.generativeai.types import GenerationConfig

response = model.generate_content(
    "Write a poem about the sea.",
    generation_config=GenerationConfig(
        candidate_count=1, # Number of generated responses to return
        stop_sequences=['\n\n\n'], # Sequences where the API will stop generating
        max_output_tokens=200,
        temperature=0.7, # Controls randomness. Lower is more deterministic.
        top_p=0.9,
        top_k=40
    )
)
print(response.text)
```

### 4.6. Safety Settings (`SafetySetting`)

Configure safety thresholds for different harm categories (e.g., harassment, hate speech).

```python
from google.generativeai.types import HarmCategory, HarmBlockThreshold

response = model.generate_content(
    "A potentially sensitive prompt...", # Be mindful of your prompts
    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        # ... other categories
    }
)

if response.prompt_feedback.block_reason:
    print(f"Prompt blocked: {response.prompt_feedback.block_reason}")
else:
    print(response.text)
```
*   **Block Reasons:** If content is blocked, `response.prompt_feedback.block_reason` will indicate why.
*   **Safety Ratings:** `response.candidates[0].safety_ratings` provides detailed safety scores.

### 4.7. Embeddings

Generate embeddings (vector representations) for text.

```python
# Use an embedding model, e.g., 'models/embedding-001'
result = genai.embed_content(
    model="models/embedding-001", # Or other embedding models
    content="What is the meaning of life?",
    task_type="RETRIEVAL_DOCUMENT", # or "SEMANTIC_SIMILARITY", "CLASSIFICATION", etc.
    # title="Optional title for RETRIEVAL_DOCUMENT"
)

print(result['embedding']) # The embedding vector
```

### 4.8. Error Handling

API calls can raise exceptions. Wrap calls in `try...except` blocks.

*   `google.api_core.exceptions.GoogleAPIError`: Base class for API errors.
*   Specific errors like `InvalidArgument`, `PermissionDenied`, `ResourceExhausted`, etc.
*   `StopCandidateException`: If a candidate was stopped (e.g., by safety settings or stop sequence) but no other valid candidate could be returned.
*   `BlockedPromptException`: If the prompt itself was blocked.

```python
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from google.generativeai import types as genai_types

# genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-1.5-flash-latest')

try:
    response = model.generate_content("A test prompt.")
    print(response.text)
except google_exceptions.InvalidArgument as e:
    print(f"Invalid argument: {e}")
except google_exceptions.PermissionDenied as e:
    print(f"Permission denied (check API key and model access): {e}")
except google_exceptions.ResourceExhausted as e:
    print(f"Resource exhausted (rate limits, quota): {e}")
except genai_types.BlockedPromptException as e:
    print(f"Prompt was blocked: {e}")
    # Access response object if available: e.response
except genai_types.StopCandidateException as e:
    print(f"Generation stopped for candidate: {e}")
    # Access response object if available: e.response
except Exception as e:
    print(f"An unexpected error occurred: {e}")
```

## 5. Advanced Topics (Brief Overview)

*   **Function Calling (Tool Use):** Define tools (functions) that the model can invoke to get external information or perform actions. The model can then request to call these functions, and you provide the results back to the model to continue generation.
*   **Vertex AI Integration:** The library can also be used with Vertex AI Gemini models. This often involves different authentication (e.g., service accounts, Application Default Credentials) and client initialization.
    ```python
    # Example for Vertex AI (from your llm_prompt_handler.py snippet)
    # from google import genai as google_vertex_ai # Alias to avoid confusion
    # from google.generativeai import types as google_vertex_types

    # client = google_vertex_ai.GenerativeModel(
    #     model_name='gemini-1.5-flash-001', # Vertex AI model name
    #     project='your-gcp-project',
    #     location='your-gcp-location',
    #     # system_instruction="...", # Can be set here or in generate_content
    # )
    # response = client.generate_content(...)
    ```
    *Note: The `google.genai.Client` you used in `llm_prompt_handler.py` is more aligned with the Vertex AI SDK's `GenerativeModel` initialization when `vertexai=True` is set. The standalone `google-generativeai` library (focused on Google AI Studio keys) uses `genai.GenerativeModel()` more directly.*

*   **File API:** Upload files (images, audio, video, PDFs) to be used with models that support file input.