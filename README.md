# 🚀 Snippet Manager - Text Expansion for Productivity

A lightweight, cross-platform desktop application that lets you insert frequently used text snippets instantly using customizable commands (e.g., `::email`). Built with Python and PySide6.

![image](https://github.com/user-attachments/assets/ca54d804-f624-4a03-b8ba-a5048660ecc4)


---

## 🌟 Features

### ✨ Core Functionality
- **⌨️ Command-Based Snippets**  
  Type `::command` to auto-replace with predefined text (e.g., `::email` → email template).
- **📂 Snippet Management**  
  Add/edit/delete snippets via a clean GUI with dark/light themes.
- **📁 Local Storage**  
  Snippets stored in `%APPDATA%/snippet_app/config.json` (no cloud dependency).
- **📁 LLM Command Generation**
  Automated prompt generation for LLMs with just a command (e.g., ::PromptEmailTemplate)

### 🎨 User Experience
- **🎯 System Tray Integration**  
  Background operation with quick access via system tray icon.
- **⚡ Low Latency**  
  Near-instant text replacement (<100ms).
- **🔒 Privacy-First**  
  No telemetry, ads, or data collection.

### 🛠️ Technical Highlights
- **🐍 Python 3.10+**  
- **📦 PySide6** for modern, native GUI.
- **🔧 JSON Configuration**  
  Easy backup/restore via human-readable files.

---

## ⚙️ Installation

### Prerequisites
- Python 3.10+
- Windows 10/11 (macOS/Linux support planned)

# 🚦 Usage  

## Adding a Snippet  
1. Right-click the system tray icon → Open Snippet Manager.  
2. Click **New** → Enter command (e.g., `::email`) and text.  
3. Click **Save**.  

## Using Snippets  
- Type `::command` in any text field (e.g., Notepad, Slack).  
- The command auto-replaces with your snippet text.  

## Managing Snippets  

| Action             | Steps                                     |
|--------------------|-------------------------------------------|
| **Edit a Snippet** | Select command → Modify text → Save      |
| **Delete a Snippet** | Select command → Delete → Confirm      |
| **Backup Snippets** | Copy `%APPDATA%\snippet_app\config.json` |

# 🛠️ Configuration  

# Command Syntax

- Commands must start with `::` (e.g., `::email`, `::sig`).
- Avoid triple `:`'s in a row (e.g. :::test) -> known bug fixing now!

# 🤝 Contributing

We welcome contributions!

1. **Fork the repository.**
2. **Create a feature branch:**

   ```sh
   git checkout -b feature/amazing-feature
   ```

3. **Commit changes:**

   ```sh
   git commit -m "Add amazing feature"
   ```

4. **Push to the branch:**

   ```sh
   git push origin feature/amazing-feature
   ```

5. **Open a Pull Request.**

# Planned Features

- 🌐 **Cloud sync** (Google Drive/Dropbox)
- 🔧 **Snippet variables** (e.g., `{{date}}`)
- 💻 **Cross-platform support**

# 📜 License

Distributed under the **MIT License**. See `LICENSE` for details.

# 🙏 Acknowledgments

- Icons by **Feather Icons**
- Built with **PySide6**

# 📬 Contact

- **Eric Zou**
- **Email:** e2zou@uwaterloo.ca
- **GitHub:** @EricJujianZou

