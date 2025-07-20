from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect

class CustomTitleBar(QWidget):
    """A custom title bar with window controls and drag functionality."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CustomTitleBar")
        self.setFixedHeight(40)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 0, 0)
        layout.setSpacing(0)

        # App Icon and Title
        # In a real app, you might add an icon here.
        self.title_label = QLabel("PromptAssist Dashboard")
        self.title_label.setObjectName("titleLabel")
        layout.addWidget(self.title_label)

        layout.addStretch()

        # Window control buttons
        self.minimize_button = QPushButton("—")
        self.maximize_button = QPushButton("□")
        self.close_button = QPushButton("✕")
        
        self.minimize_button.setObjectName("minimizeButton")
        self.maximize_button.setObjectName("maximizeButton")
        self.close_button.setObjectName("closeButton")

        for btn in [self.minimize_button, self.maximize_button, self.close_button]:
            btn.setFixedSize(45, 40) # Width, Height
            layout.addWidget(btn)

        # Connect signals to window functions
        self.minimize_button.clicked.connect(self._minimize_window)
        self.maximize_button.clicked.connect(self._maximize_window)
        self.close_button.clicked.connect(self._close_window)

        self.start_move_pos = None

    def _minimize_window(self):
        self.window().showMinimized()

    def _maximize_window(self):
        if self.window().isMaximized():
            self.window().showNormal()
            self.maximize_button.setText("□")
        else:
            self.window().showMaximized()
            self.maximize_button.setText("❐") # Character for restore

    def _close_window(self):
        self.window().close()

    # The following three methods implement window dragging
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_move_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.start_move_pos:
            delta = event.globalPosition().toPoint() - self.start_move_pos
            self.window().move(self.window().pos() + delta)
            self.start_move_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.start_move_pos = None


class FramelessWindow(QWidget):
    """A base window that is frameless and uses a custom title bar."""
    def __init__(self, content_widget: QWidget, parent=None):
        super().__init__(parent)
        # Make the window frameless and the background translucent
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setObjectName("FramelessWindow")
        
        # Main layout holds a container that we can apply a shadow to
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10) # Margins to make space for the shadow
        main_layout.setSpacing(0)

        # Shadow container holds the actual UI (title bar + content)
        shadow_container = QWidget()
        shadow_container.setObjectName("shadowContainer")
        shadow_layout = QVBoxLayout(shadow_container)
        shadow_layout.setContentsMargins(0, 0, 0, 0)
        shadow_layout.setSpacing(0)
        main_layout.addWidget(shadow_container)

        # Title bar
        self.title_bar = CustomTitleBar(self)
        shadow_layout.addWidget(self.title_bar)

        # Content
        shadow_layout.addWidget(content_widget)

        # Add a drop shadow effect for a modern look
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(Qt.GlobalColor.black)
        shadow_container.setGraphicsEffect(shadow)

        self.resize(800, 600)
