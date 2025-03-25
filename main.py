import sys
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QWidget,
    QHBoxLayout, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy, QMenu
)
from PyQt5.QtGui import QPixmap, QDesktopServices, QIcon
from PyQt5.QtCore import Qt, QUrl, QPropertyAnimation

# --- TitleBar Widget with Settings Button ---
class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)
        self.setStyleSheet("background-color: #1F1F1F;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 0, 5, 0)
        
        # Logo in the title bar (24x24 pixels)
        self.logo_label = QLabel(self)
        logo_pixmap = QPixmap(r"C:\Users\ianso\Downloads\TrinityLogoUpdate.png")
        if not logo_pixmap.isNull():
            scaled_logo = logo_pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(scaled_logo)
        self.logo_label.setStyleSheet("border: none; background: transparent;")
        layout.addWidget(self.logo_label, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        
        # Title label next to the logo
        self.title_label = QLabel("Trinity", self)
        self.title_label.setStyleSheet("color: white; font-size: 14px; margin-left: 5px; border: none; background: transparent;")
        layout.addWidget(self.title_label, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        
        layout.addStretch()
        
        # Settings button (gear icon)
        self.settings_button = QPushButton("⚙", self)
        self.settings_button.setFixedSize(30, 30)
        self.settings_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        # Open theme menu on click
        self.settings_button.clicked.connect(lambda: self.window().openThemeMenu())
        layout.addWidget(self.settings_button, alignment=Qt.AlignRight | Qt.AlignVCenter)
        
        # Custom close button ("X") on the top right
        self.close_button = QPushButton("X", self)
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: red;
            }
        """)
        self.close_button.clicked.connect(self.window().close)
        layout.addWidget(self.close_button, alignment=Qt.AlignRight | Qt.AlignVCenter)
        
        self._clickPos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._clickPos = event.globalPos() - self.window().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._clickPos:
            self.window().move(event.globalPos() - self._clickPos)
            event.accept()

# --- MainWindow with dynamic theme, fade-in animation, and theme menu ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Trinity")
        self.setFixedSize(533, 267)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Set the taskbar icon
        self.setWindowIcon(QIcon(r"C:\Users\ianso\Downloads\TrinityLogoUpdate.png"))
        
        # Define two themes:
        self.theme_default = {
            "title_bar_bg": "#1F1F1F",
            "central_bg": "#1F1F1F",
            "central_border": "#2D2D2D",
            "launch_bg": "#2D2D2D",
            "launch_hover": "#37393B",
            "discord_text": "rgb(0,170,255)",
            "discord_hover": "#37393B",
            "title_text": "white"
        }
        self.theme_regular = {
            "title_bar_bg": "#F0F0F0",
            "central_bg": "#FFFFFF",
            "central_border": "#CCCCCC",
            "launch_bg": "#E0E0E0",
            "launch_hover": "#D0D0D0",
            "discord_text": "black",
            "discord_hover": "#D0D0D0",
            "title_text": "black"
        }
        self.current_theme = "default"  # Default is dark
        
        # Central widget with rounded corners and border
        self.central = QWidget(self)
        self.central.setStyleSheet(f"background-color: {self.theme_default['central_bg']}; border-radius: 10px; border: 1px solid {self.theme_default['central_border']};")
        self.setCentralWidget(self.central)
        
        v_layout = QVBoxLayout(self.central)
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.setSpacing(0)
        
        # Custom title bar
        self.title_bar = TitleBar(self)
        v_layout.addWidget(self.title_bar)
        
        # Content widget
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: transparent;")
        v_layout.addWidget(content_widget)
        
        main_layout = QHBoxLayout(content_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # LEFT SIDE: Composite Logo/Title/Version and Buttons
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(5)
        
        left_layout.addStretch()
        
        # Composite widget for logo, title, and version info (transparent)
        logo_title_widget = QWidget()
        logo_title_widget.setStyleSheet("background: transparent; border: none;")
        logo_title_layout = QHBoxLayout(logo_title_widget)
        logo_title_layout.setContentsMargins(0, 0, 0, 0)
        logo_title_layout.setSpacing(5)
        
        # Logo label (scaled to a fixed height of 80px)
        comp_logo_label = QLabel()
        comp_logo_pixmap = QPixmap(r"C:\Users\ianso\Downloads\TrinityLogoUpdate.png")
        if not comp_logo_pixmap.isNull():
            comp_logo_scaled = comp_logo_pixmap.scaledToHeight(80, Qt.SmoothTransformation)
            comp_logo_label.setPixmap(comp_logo_scaled)
        comp_logo_label.setStyleSheet("background: transparent; border: none;")
        logo_title_layout.addWidget(comp_logo_label)
        
        # Vertical layout for title and version info
        title_version_layout = QVBoxLayout()
        title_version_layout.setContentsMargins(0, 0, 0, 0)
        title_version_layout.setSpacing(0)
        title_text = QLabel("Trinity")
        title_text.setStyleSheet(f"color: {self.theme_default['title_text']}; font-size: 16px; background: transparent; border: none;")
        version_text = QLabel("v2.90.0")
        version_text.setStyleSheet("color: gray; font-size: 10px; background: transparent; border: none;")
        title_version_layout.addWidget(title_text)
        title_version_layout.addWidget(version_text)
        
        logo_title_layout.addLayout(title_version_layout)
        logo_title_widget.setLayout(logo_title_layout)
        
        left_layout.addWidget(logo_title_widget, alignment=Qt.AlignCenter)
        
        left_layout.addSpacerItem(QSpacerItem(20, 5, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        left_layout.addStretch()
        
        # "Join the Discord" button
        self.discord_button = QPushButton("Join the Discord")
        self.discord_button.setFixedSize(200, 40)
        self.discord_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {self.theme_default['discord_text']};
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {self.theme_default['discord_hover']};
            }}
        """)
        self.discord_button.clicked.connect(self.join_discord)
        left_layout.addWidget(self.discord_button, alignment=Qt.AlignCenter)
        
        # "About Trinity" button
        self.about_button = QPushButton("About Trinity")
        self.about_button.setFixedSize(200, 40)
        self.about_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {self.theme_default['discord_text']};
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {self.theme_default['discord_hover']};
            }}
        """)
        self.about_button.clicked.connect(self.about_trinity)
        left_layout.addWidget(self.about_button, alignment=Qt.AlignCenter)
        
        left_layout.addStretch()

        # RIGHT SIDE: Launch Application Button
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        right_layout.setAlignment(Qt.AlignCenter)

        self.launch_button = QPushButton("Launch Application")
        self.launch_button.setFixedSize(200, 50)
        self.launch_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme_default['launch_bg']};
                border: none;
                color: white;
                font-size: 12px;
                padding: 3px;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {self.theme_default['launch_hover']};
            }}
        """)
        self.launch_button.clicked.connect(self.run_exe)
        right_layout.addWidget(self.launch_button, alignment=Qt.AlignCenter)

        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)
        
        self.updateTheme()  # Apply the default theme
        
        # Fade-in animation on show
        self.setWindowOpacity(0)
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(500)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.start()

    def updateTheme(self):
        if self.current_theme == "default":
            theme = self.theme_default
        else:
            theme = self.theme_regular
        # Update title bar background
        self.title_bar.setStyleSheet(f"background-color: {theme['title_bar_bg']};")
        # Update central widget background and border
        self.central.setStyleSheet(f"background-color: {theme['central_bg']}; border-radius: 10px; border: 1px solid {theme['central_border']};")
        # Update launch button
        self.launch_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme['launch_bg']};
                border: none;
                color: white;
                font-size: 12px;
                padding: 3px;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {theme['launch_hover']};
            }}
        """)
        # Update Discord and About buttons
        self.discord_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {theme['discord_text']};
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {theme['discord_hover']};
            }}
        """)
        self.about_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {theme['discord_text']};
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {theme['discord_hover']};
            }}
        """)
        # Update title text in title bar
        self.title_bar.title_label.setStyleSheet(f"color: {theme['title_text']}; font-size: 14px; margin-left: 5px; border: none; background: transparent;")
        
    def openThemeMenu(self):
        menu = QMenu(self)
        action_default = menu.addAction("Default")
        action_regular = menu.addAction("Regular")
        pos = self.title_bar.settings_button.mapToGlobal(self.title_bar.settings_button.rect().bottomLeft())
        action = menu.exec_(pos)
        if action == action_default:
            self.current_theme = "default"
        elif action == action_regular:
            self.current_theme = "regular"
        self.updateTheme()

    def run_exe(self):
        exe_path = r"C:\Users\ianso\Downloads\TrinityTest.exe"
        try:
            subprocess.Popen([exe_path])
        except Exception as e:
            print("Error launching the executable:", e)

    def join_discord(self):
        url = QUrl("https://discord.gg/HNWaj5cfQ6")
        QDesktopServices.openUrl(url)

    def about_trinity(self):
        print("About Trinity button clicked.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())