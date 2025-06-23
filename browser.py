import sys
import os
import threading
from PySide6.QtCore import QUrl, Qt, QSize
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                          QHBoxLayout, QPushButton, QLineEdit, QTabWidget, QToolBar)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QIcon, QAction
from werkzeug.serving import make_server
import app as flask_app

class FlaskThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.srv = make_server('127.0.0.1', 5000, flask_app.app)
        self.ctx = flask_app.app.app_context()
        self.ctx.push()

    def run(self):
        self.srv.serve_forever()

    def shutdown(self):
        self.srv.shutdown()

class BrowserTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # Navigation bar
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(2)
        nav_layout.setContentsMargins(2, 2, 2, 2)
        
        # Create compact buttons
        button_size = QSize(24, 24)
        
        # Back button
        self.back_btn = QPushButton("←")
        self.back_btn.setFixedSize(button_size)
        self.back_btn.clicked.connect(self.navigate_back)
        self.back_btn.setToolTip("Back")
        nav_layout.addWidget(self.back_btn)
        
        # Forward button
        self.forward_btn = QPushButton("→")
        self.forward_btn.setFixedSize(button_size)
        self.forward_btn.clicked.connect(self.navigate_forward)
        self.forward_btn.setToolTip("Forward")
        nav_layout.addWidget(self.forward_btn)
        
        # Reload button
        self.reload_btn = QPushButton("↻")
        self.reload_btn.setFixedSize(button_size)
        self.reload_btn.clicked.connect(self.reload_page)
        self.reload_btn.setToolTip("Reload")
        nav_layout.addWidget(self.reload_btn)
        
        # Home button
        self.home_btn = QPushButton("⌂")
        self.home_btn.setFixedSize(button_size)
        self.home_btn.clicked.connect(self.go_home)
        self.home_btn.setToolTip("Home")
        nav_layout.addWidget(self.home_btn)
        
        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.setFixedHeight(24)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        nav_layout.addWidget(self.url_bar)
        
        # Add navigation bar to layout
        nav_container = QWidget()
        nav_container.setLayout(nav_layout)
        nav_container.setFixedHeight(30)
        self.layout.addWidget(nav_container)
        
        # Web view
        self.web_view = QWebEngineView()
        self.web_view.urlChanged.connect(self.update_url)
        self.web_view.page().setBackgroundColor(Qt.white)
        
        # Handle target="_blank" links
        self.web_view.page().newWindowRequested.connect(self.handle_new_window)
        
        self.layout.addWidget(self.web_view)
        
        # Load home page
        self.go_home()

    def handle_new_window(self, request):
        # Open new tab instead of new window
        main_window = self.window()
        new_tab = main_window.add_new_tab()
        new_tab.web_view.setUrl(request.requestedUrl())
        request.reject()  # Reject the new window request

    def navigate_back(self):
        self.web_view.back()

    def navigate_forward(self):
        self.web_view.forward()

    def reload_page(self):
        self.web_view.reload()

    def go_home(self):
        self.web_view.setUrl(QUrl("http://127.0.0.1:5000"))

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        self.web_view.setUrl(QUrl(url))

    def update_url(self, url):
        url_str = url.toString()
        if url_str.startswith('http://127.0.0.1:5000'):
            self.url_bar.setText('https://search.imedrasphere.com')
        else:
            self.url_bar.setText(url_str)

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IMEDRA Browser")
        self.setGeometry(100, 100, 1280, 800)

        # Create minimal toolbar for new tab
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setIconSize(QSize(16, 16))
        new_tab_action = QAction("+ New Tab", self)
        new_tab_action.setShortcut("Ctrl+T")
        new_tab_action.triggered.connect(self.add_new_tab)
        toolbar.addAction(new_tab_action)
        self.addToolBar(toolbar)
        toolbar.setFixedHeight(24)

        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.setDocumentMode(True)  # More compact tabs
        self.setCentralWidget(self.tabs)

        # Start Flask server
        self.flask_thread = FlaskThread()
        self.flask_thread.start()

        # Add initial tab
        self.add_new_tab()

    def add_new_tab(self):
        tab = BrowserTab()
        index = self.tabs.addTab(tab, "New Tab")
        self.tabs.setCurrentIndex(index)
        return tab

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.close()

    def closeEvent(self, event):
        self.flask_thread.shutdown()
        event.accept()

if __name__ == "__main__":
    qt_app = QApplication(sys.argv)
    qt_app.setStyle('Fusion')  # Modern style
    browser = Browser()
    browser.show()
    sys.exit(qt_app.exec())
