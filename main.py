import sys
import os
import json
import requests
import subprocess
import tempfile
import hashlib
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                            QHBoxLayout, QWidget, QPushButton, QLabel, 
                            QTextEdit, QProgressBar, QMessageBox)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont

# Version of your application
APP_VERSION = "1.0.0"
UPDATE_SERVER = "https://api.github.com/repos/yourusername/yourrepo/releases/latest"

class UpdateChecker(QThread):
    update_available = pyqtSignal(dict)
    no_update = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, current_version):
        super().__init__()
        self.current_version = current_version
    
    def run(self):
        try:
            response = requests.get(UPDATE_SERVER, timeout=10)
            if response.status_code == 200:
                release_info = response.json()
                latest_version = release_info['tag_name'].lstrip('v')
                
                if self.is_newer_version(latest_version, self.current_version):
                    # Find the appropriate asset for the current platform
                    asset_url = None
                    for asset in release_info['assets']:
                        if sys.platform.startswith('win') and asset['name'].endswith('.exe'):
                            asset_url = asset['browser_download_url']
                            break
                        elif sys.platform.startswith('darwin') and 'mac' in asset['name'].lower():
                            asset_url = asset['browser_download_url']
                            break
                        elif sys.platform.startswith('linux') and 'linux' in asset['name'].lower():
                            asset_url = asset['browser_download_url']
                            break
                    
                    if asset_url:
                        update_info = {
                            'version': latest_version,
                            'url': asset_url,
                            'notes': release_info.get('body', 'No release notes available')
                        }
                        self.update_available.emit(update_info)
                    else:
                        self.no_update.emit()
                else:
                    self.no_update.emit()
            else:
                self.error_occurred.emit(f"Failed to check for updates: HTTP {response.status_code}")
        except Exception as e:
            self.error_occurred.emit(f"Update check failed: {str(e)}")
    
    def is_newer_version(self, latest, current):
        """Simple version comparison (assumes semantic versioning)"""
        latest_parts = [int(x) for x in latest.split('.')]
        current_parts = [int(x) for x in current.split('.')]
        
        # Pad shorter version with zeros
        max_len = max(len(latest_parts), len(current_parts))
        latest_parts.extend([0] * (max_len - len(latest_parts)))
        current_parts.extend([0] * (max_len - len(current_parts)))
        
        return latest_parts > current_parts

class UpdateDownloader(QThread):
    progress_updated = pyqtSignal(int)
    download_finished = pyqtSignal(str)
    download_failed = pyqtSignal(str)
    
    def __init__(self, url, filename):
        super().__init__()
        self.url = url
        self.filename = filename
    
    def run(self):
        try:
            response = requests.get(self.url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            temp_dir = tempfile.gettempdir()
            file_path = os.path.join(temp_dir, self.filename)
            
            with open(file_path, 'wb') as file:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            self.progress_updated.emit(progress)
            
            self.download_finished.emit(file_path)
        except Exception as e:
            self.download_failed.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"PyQt Auto-Update Demo v{APP_VERSION}")
        self.setGeometry(300, 300, 800, 600)
        
        # Initialize UI
        self.setup_ui()
        
        # Auto-check for updates on startup (after 3 seconds)
        QTimer.singleShot(3000, self.check_for_updates)
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel(f"PyQt Demo Application")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        version_label = QLabel(f"Version: {APP_VERSION}")
        version_label.setFont(QFont("Arial", 10))
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(version_label)
        layout.addLayout(header_layout)
        
        # Main content area
        self.text_area = QTextEdit()
        self.text_area.setPlainText("This is a demo PyQt application with auto-update functionality.\n\n"
                                   "Features:\n"
                                   "- Built with PyQt5\n"
                                   "- Packaged with PyInstaller\n"
                                   "- Auto-update capability\n"
                                   "- Cross-platform support\n\n"
                                   "Click 'Check for Updates' to manually check for new versions.")
        layout.addWidget(self.text_area)
        
        # Update section
        update_layout = QVBoxLayout()
        
        button_layout = QHBoxLayout()
        self.check_update_btn = QPushButton("Check for Updates")
        self.check_update_btn.clicked.connect(self.check_for_updates)
        button_layout.addWidget(self.check_update_btn)
        button_layout.addStretch()
        
        update_layout.addLayout(button_layout)
        
        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        update_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready")
        update_layout.addWidget(self.status_label)
        
        layout.addLayout(update_layout)
        
        # Add some demo buttons
        demo_layout = QHBoxLayout()
        demo_btn1 = QPushButton("Demo Button 1")
        demo_btn2 = QPushButton("Demo Button 2")
        demo_btn1.clicked.connect(lambda: self.show_message("Demo Button 1 clicked!"))
        demo_btn2.clicked.connect(lambda: self.show_message("Demo Button 2 clicked!"))
        
        demo_layout.addWidget(demo_btn1)
        demo_layout.addWidget(demo_btn2)
        layout.addLayout(demo_layout)
    
    def show_message(self, message):
        self.text_area.append(f"\n{message}")
    
    def check_for_updates(self):
        self.status_label.setText("Checking for updates...")
        self.check_update_btn.setEnabled(False)
        
        self.update_checker = UpdateChecker(APP_VERSION)
        self.update_checker.update_available.connect(self.on_update_available)
        self.update_checker.no_update.connect(self.on_no_update)
        self.update_checker.error_occurred.connect(self.on_update_error)
        self.update_checker.start()
    
    def on_update_available(self, update_info):
        self.status_label.setText(f"Update available: v{update_info['version']}")
        self.check_update_btn.setEnabled(True)
        
        reply = QMessageBox.question(
            self, 
            "Update Available",
            f"A new version (v{update_info['version']}) is available!\n\n"
            f"Release Notes:\n{update_info['notes'][:200]}...\n\n"
            "Would you like to download and install it?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            self.download_update(update_info['url'])
    
    def on_no_update(self):
        self.status_label.setText("You have the latest version")
        self.check_update_btn.setEnabled(True)
    
    def on_update_error(self, error_message):
        self.status_label.setText(f"Update check failed: {error_message}")
        self.check_update_btn.setEnabled(True)
    
    def download_update(self, url):
        filename = os.path.basename(url)
        self.status_label.setText("Downloading update...")
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        
        self.downloader = UpdateDownloader(url, filename)
        self.downloader.progress_updated.connect(self.progress_bar.setValue)
        self.downloader.download_finished.connect(self.on_download_finished)
        self.downloader.download_failed.connect(self.on_download_failed)
        self.downloader.start()
    
    def on_download_finished(self, file_path):
        self.progress_bar.hide()
        self.status_label.setText("Download completed")
        
        reply = QMessageBox.question(
            self,
            "Install Update",
            f"Update downloaded successfully!\n\n"
            f"Location: {file_path}\n\n"
            "The application will close and the new version will be installed.",
            QMessageBox.Ok | QMessageBox.Cancel,
            QMessageBox.Ok
        )
        
        if reply == QMessageBox.Ok:
            self.install_update(file_path)
    
    def on_download_failed(self, error_message):
        self.progress_bar.hide()
        self.status_label.setText(f"Download failed: {error_message}")
        QMessageBox.critical(self, "Download Error", f"Failed to download update:\n{error_message}")
    
    def install_update(self, file_path):
        """Install the update and restart the application"""
        try:
            if sys.platform.startswith('win'):
                # On Windows, start the installer
                subprocess.Popen([file_path])
            elif sys.platform.startswith('darwin'):
                # On macOS, open the dmg/pkg file
                subprocess.Popen(['open', file_path])
            elif sys.platform.startswith('linux'):
                # On Linux, make executable and run
                os.chmod(file_path, 0o755)
                subprocess.Popen([file_path])
            
            # Close the current application
            QApplication.quit()
            
        except Exception as e:
            QMessageBox.critical(self, "Installation Error", 
                               f"Failed to install update:\n{str(e)}\n\n"
                               f"Please manually install from: {file_path}")

def main():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("PyQt Auto-Update Demo")
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("Your Organization")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()