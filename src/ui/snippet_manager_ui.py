from PySide6.QtWidgets import (
    QApplication, QWidget, QListWidget, QTextEdit, QVBoxLayout, 
    QPushButton, QInputDialog, QMessageBox, QHBoxLayout, QStackedWidget, QLabel,
    QFormLayout, QComboBox, QCheckBox, QPlainTextEdit, QTableWidget, QHeaderView,
    QTableWidgetItem, QAbstractItemView
)
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt, Slot
import os

from ..storage.snippet_storage import SnippetStorage
from ..storage.settings_storage import SettingsStorage
from ..storage.history_storage import HistoryStorage
from .frameless_window import FramelessWindow

class SnippetUI(QWidget):
    def __init__(self, storage: SnippetStorage, settings: SettingsStorage, history: HistoryStorage, parent=None):
        super().__init__(parent)
        self.storage = storage
        self.settings = settings
        self.history = history
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("Expandr Dashboard")
        self.resize(800, 600)

        main_layout = QHBoxLayout(self)

        # --- Left Navigation Pane ---
        self.nav_list = QListWidget()
        self.nav_list.addItem("Snippets")
        self.nav_list.addItem("Settings")
        self.nav_list.addItem("History")
        self.nav_list.setMaximumWidth(150)
        main_layout.addWidget(self.nav_list)

        # --- Main Content Area ---
        self.pages = QStackedWidget()
        main_layout.addWidget(self.pages)

        # Create the different pages for the content area
        self.snippet_page = self._create_snippet_page()
        self.settings_page = self._create_settings_page()
        self.history_page = self._create_history_page()

        # Add pages to the stacked widget
        self.pages.addWidget(self.snippet_page)
        self.pages.addWidget(self.settings_page)
        self.pages.addWidget(self.history_page)

        # Connect navigation list to the stacked widget
        self.nav_list.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.nav_list.currentRowChanged.connect(self._on_page_changed)

    def _create_snippet_page(self):
        """Creates the widget for the 'Snippets' page."""
        page = QWidget()
        layout = QVBoxLayout(page)

        self.snippet_list_widget = QListWidget()
        self._refresh_list()
        layout.addWidget(self.snippet_list_widget)

        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)

        btn_layout = QHBoxLayout()

        self.save_button = QPushButton("Save")
        self.save_button.setObjectName("saveButton")
        self.save_button.setIcon(QIcon.fromTheme("document-save"))
        self.save_button.clicked.connect(self._save_snippet)
        btn_layout.addWidget(self.save_button)

        self.new_button = QPushButton("Create New Snippet")
        self.new_button.setObjectName("newButton")
        self.new_button.setIcon(QIcon.fromTheme("document-new"))
        self.new_button.clicked.connect(self._new_snippet)
        btn_layout.addWidget(self.new_button)

        self.del_button = QPushButton("Delete a Snippet")
        self.del_button.setObjectName("deleteButton")
        self.del_button.setIcon(QIcon.fromTheme("edit-delete"))
        self.del_button.clicked.connect(self._del_snippet)
        btn_layout.addWidget(self.del_button)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.snippet_list_widget.itemClicked.connect(self._load_snippet)
        
        return page

    def _create_settings_page(self):
        """Creates the widget for the 'Settings' page."""
        page = QWidget()
        layout = QFormLayout(page)
        layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        # --- Theme Selection ---
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        # Ensure the value from settings is treated as a string
        self.theme_combo.setCurrentText(str(self.settings.get("theme", "Dark")))
        self.theme_combo.currentTextChanged.connect(self._on_setting_changed)
        layout.addRow("Theme:", self.theme_combo)

        # --- Clear Clipboard ---
        self.clear_clipboard_checkbox = QCheckBox("Clear clipboard after pasting")
        # Ensure the value from settings is treated as a boolean
        self.clear_clipboard_checkbox.setChecked(bool(self.settings.get("clear_clipboard_on_paste", False)))
        self.clear_clipboard_checkbox.stateChanged.connect(self._on_setting_changed)
        layout.addRow(self.clear_clipboard_checkbox)

        # --- Blacklisted Apps ---
        self.blacklist_edit = QPlainTextEdit()
        blacklist = self.settings.get("blacklisted_apps", [])
        # Ensure blacklist is a list before joining
        if isinstance(blacklist, list):
            self.blacklist_edit.setPlainText("\n".join(blacklist))
        self.blacklist_edit.setPlaceholderText("One app name per line, e.g., my_game.exe")
        self.blacklist_edit.textChanged.connect(self._on_setting_changed)
        layout.addRow("Blacklisted Apps:", self.blacklist_edit)
        
        return page

    def _on_setting_changed(self):
        """Generic slot to save any setting that has been changed."""
        sender = self.sender()
        # Check the type of the sender to safely access its methods
        if isinstance(sender, QComboBox) and sender == self.theme_combo:
            self.settings.set("theme", sender.currentText())
            QMessageBox.information(self, "Theme Changed", "Theme will be applied on next restart.")
        elif isinstance(sender, QCheckBox) and sender == self.clear_clipboard_checkbox:
            self.settings.set("clear_clipboard_on_paste", sender.isChecked())
        elif isinstance(sender, QPlainTextEdit) and sender == self.blacklist_edit:
            apps = sender.toPlainText().strip().split('\n')
            self.settings.set("blacklisted_apps", [app.strip() for app in apps if app.strip()])

    def _create_history_page(self):
        """Creates the widget for the 'History' page."""
        page = QWidget()
        layout = QVBoxLayout(page)

        # --- Table for History ---
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(3)
        self.history_table.setHorizontalHeaderLabels(["Timestamp", "Query", "Result"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.history_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        # Enable context menu
        self.history_table.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)

        # --- Context Menu Actions ---
        copy_action = QAction("Copy Result", self.history_table)
        copy_action.triggered.connect(self._copy_history_result)
        self.history_table.addAction(copy_action)

        save_as_snippet_action = QAction("Save as Snippet", self.history_table)
        save_as_snippet_action.triggered.connect(self._save_history_as_snippet)
        self.history_table.addAction(save_as_snippet_action)

        layout.addWidget(self.history_table)

        # --- Clear History Button ---
        self.clear_history_button = QPushButton("Clear All History")
        self.clear_history_button.clicked.connect(self._clear_history)
        layout.addWidget(self.clear_history_button, alignment=Qt.AlignmentFlag.AlignRight)

        return page

    def _on_page_changed(self, index):
        """Slot to refresh data when a page becomes visible."""
        # Index 2 corresponds to the History page
        if index == 2:
            self._refresh_history_table()

    def _refresh_history_table(self):
        """Reloads all entries from history storage into the table."""
        self.history_table.setRowCount(0) # Clear table
        history_entries = self.history.get_all()
        self.history_table.setRowCount(len(history_entries))

        for row, entry in enumerate(history_entries):
            self.history_table.setItem(row, 0, QTableWidgetItem(entry.get("timestamp", "")))
            self.history_table.setItem(row, 1, QTableWidgetItem(entry.get("query", "")))
            self.history_table.setItem(row, 2, QTableWidgetItem(entry.get("result", "")))

    def _copy_history_result(self):
        """Copies the result from the selected history row to the clipboard."""
        selected_items = self.history_table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        result_item = self.history_table.item(row, 2)
        if result_item:
            QApplication.clipboard().setText(result_item.text())
            QMessageBox.information(self, "Copied", "Result copied to clipboard.")

    def _save_history_as_snippet(self):
        """Saves the selected history item as a new snippet."""
        selected_items = self.history_table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        result_item = self.history_table.item(row, 2)
        if not result_item:
            return

        command, ok = QInputDialog.getText(self, "New Snippet", "Enter command for the new snippet (e.g. ::mysnippet):")
        if ok and command:
            self.storage.save(command, result_item.text())
            QMessageBox.information(self, "Snippet Saved", f"Saved as new snippet with command: {command}")

    def _clear_history(self):
        """Asks for confirmation and clears the history."""
        confirm = QMessageBox.question(
            self, "Clear History",
            "Are you sure you want to delete all history entries? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.history.clear()
            self._refresh_history_table()
            QMessageBox.information(self, "History Cleared", "All history has been deleted.")

    def _refresh_list(self):
        self.snippet_list_widget.clear()
        for cmd in self.storage.snippets:
            self.snippet_list_widget.addItem(cmd)

    @Slot() 
    def _load_snippet(self, item):
        cmd = item.text()
        self.text_edit.setPlainText(self.storage.snippets[cmd])
    
    @Slot()
    def _save_snippet(self):
        selected_item = self.snippet_list_widget.currentItem()
        if selected_item:
            cmd = selected_item.text()
            new_text = self.text_edit.toPlainText()
            self.storage.save(cmd, new_text)
        else:
            QMessageBox.warning(self, "No snippet selected", "Please select a snippet to save")

    @Slot()
    def _new_snippet(self):
        command, ok = QInputDialog.getText(self, "New Snippet", "Enter command (e.g. ::email)")
        if ok and command: 
            text, ok = QInputDialog.getText(self, "New Snippet", "Enter snippet text: ")
            if ok and text:
                self.storage.save(command, text)
                self._refresh_list()

    @Slot()
    def _del_snippet(self):
        selected_item = self.snippet_list_widget.currentItem()
        if selected_item:
            cmd = selected_item.text()
            confirm = QMessageBox.question(
                self, "Delete Snippet",
                f"Are you sure you want to delete {cmd}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if confirm == QMessageBox.StandardButton.Yes:
                self.storage.delete(cmd)
                self._refresh_list()
        else:
            QMessageBox.warning(self, "No snippet selected", "Please select a snippet to delete")

def load_stylesheet(file_path):
    try:
        with open(file_path, "r") as f:
            return f.read()
    except Exception as e:
        print(f"Error loading stylesheet: {e}")
        return ""
        
if __name__ == "__main__":
    app = QApplication([])
    
    style_path = os.path.join(os.path.dirname(__file__), '..', 'style.qss')
    stylesheet = load_stylesheet(style_path)
    app.setStyleSheet(stylesheet)

    storage = SnippetStorage()
    settings = SettingsStorage()
    history = HistoryStorage()
    # The SnippetUI is now the content, wrapped by our new FramelessWindow
    dashboard_content = SnippetUI(storage, settings, history)
    window = FramelessWindow(dashboard_content)
    window.show()
    app.exec()

