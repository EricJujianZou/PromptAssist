from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListWidget, 
QTextEdit, QVBoxLayout, QWidget, QPushButton, QInputDialog, QMessageBox, QHBoxLayout
)
import os
from PySide6.QtGui import QIcon
from PySide6.QtCore import Slot
from storage import SnippetStorage #importing class

class SnippetUI (QMainWindow):
    def __init__(self, storage = None, parent_app=None):
        super().__init__()
        self.storage = storage or SnippetStorage()
        self._init_ui()

    def _init_ui(self):
        self.statusBar().showMessage("Ready")
        #window
        self.setWindowTitle("Snippet Manager")
        self.resize(400,600)

        #central widget
        central_widget = QWidget()#instance
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout() #vertical layout
        
        #list widget
        self.list_widget = QListWidget()
        self._refresh_list()
        layout.addWidget(self.list_widget)

        #text editor to modify snippets
        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)



        #----------------------------------------buttons----------------------------------------
        btn_layout = QHBoxLayout()

        #Save button
        self.save_button = QPushButton("Save")
        self.save_button.setObjectName("saveButton")
        self.save_button.setIcon(QIcon.fromTheme("document-save"))
        self.save_button.clicked.connect(self._save_snippet)
        layout.addWidget(self.save_button)

        #new Snippet button
        self.new_button = QPushButton("Create New Snippet")
        self.new_button.setObjectName("newButton")
        self.new_button.setIcon(QIcon.fromTheme("document-new"))
        self.new_button.clicked.connect(self._new_snippet)
        layout.addWidget(self.new_button)

        #delete Snippet button
        self.del_button = QPushButton("Delete a Snippet")
        self.del_button.setObjectName("deleteButton")
        self.del_button.setIcon(QIcon.fromTheme("edit-delete"))
        self.del_button.clicked.connect(self._del_snippet)
        layout.addWidget(self.del_button)

        # Existing buttons:  
        btn_layout.addWidget(self.save_button)  
        btn_layout.addWidget(self.new_button)  
        btn_layout.addWidget(self.del_button)  

        # Optional: Add spacers to push buttons left  
        btn_layout.addStretch()  

        #connecting signals and slots
        self.list_widget.itemClicked.connect(self._load_snippet)
        layout.addLayout(btn_layout)
        central_widget.setLayout(layout)

    

    #resetting and adding commands when user edits list
    def _refresh_list(self):
        self.list_widget.clear()
        for cmd in self.storage.snippets:
            self.list_widget.addItem(cmd)

    #Slot decorator for event handling and signal and slot connection
    @Slot() 
    def _load_snippet(self, item):
        cmd = item.text()
        self.text_edit.setPlainText(self.storage.snippets[cmd])
    
    @Slot()
    def _save_snippet(self):
        selected_item = self.list_widget.currentItem()
        if selected_item:
            cmd = selected_item.text() #whatever command I must update
            new_text = self.text_edit.toPlainText() #edited text
            self.storage.save(cmd, new_text)  #save to file
            self._refresh_list()#update list
            self.statusBar().showMessage(f"Snippet Saved: {cmd}", 3000)#3 seocnd display of success
        else:
            QMessageBox.warning(self, "No snippet selected", "Please select a snippet to save")
            return
        if self.parent_app:
            self.parent_app.refresh_commands() #refresh in main app so the storage are linked

    @Slot()
    def _new_snippet(self):
        #using a tuple to store the command and text, depending if user clicked ok or cancel
        #the buttons are default provided by QInputDialog
        command, ok = QInputDialog.getText(self, "New Snippet", "Enter command (e.g. ::email)")
        if ok and command: 
            text, ok = QInputDialog.getText(self, "New Snippet", "Enter snippet text: ")
            if ok and text:
                self.storage.save(command, text)
                self._refresh_list() #updating list
            else:
                return
        else:
            return
        if self.parent_app:
            self.parent_app.refresh_commands() #refresh in main app so the storage are linked

    #method to delete a snippet
    @Slot()
    def _del_snippet(self):
        selected_item = self.list_widget.currentItem()
        if selected_item:
            cmd = selected_item.text() #getting key
            confirm = QMessageBox.question(
                self, "Delete Snippet",
                f"Are you sure you want to delete {cmd}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if confirm == QMessageBox.StandardButton.Yes:
                self.storage.delete(cmd)#deleting key-value pair
                self._refresh_list()
                self.statusBar().showMessage(f"Snippet Deleted: {cmd}", 3000)
            else: 
                return
        else:
            QMEessageBox.warning(self, "No snippet selected", "Please select a snippet to delete")
        if self.parent_app:
            self.parent_app.refresh_commands()


def load_stylesheet(file_path):
    #load external stylesheet from qss
    try:
        with open(file_path, 'r')as f:
            return f.read()
    except FileNotFoundError as e:
        print (f"Error loading stylesheet: {e}")
        return ""
if __name__ == "__main__":
    app = QApplication([])
    
    #load stylesheet
    style_path = os.path.join(os.path.dirname(__file__), 'style.qss')
    stylesheet = load_stylesheet(style_path)
    app.setStyleSheet(stylesheet)

    window = SnippetUI()
    window.show()
    app.exec()

