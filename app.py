import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QWidget, QVBoxLayout, QLabel, QPushButton, QDateEdit, QLineEdit, QComboBox, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QDate
from scraper import Scraper
# from ebay_listing import EBayListing
import json
import subprocess
import platform
import os
from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("ENV")

class EbayAutoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ERIARCH -GBPスクレイピングツール")
        self.initUI()
        self.input_csv_path = None

    def initUI(self):
        layout = QVBoxLayout()

        layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        # Label to display selected file path
        self.file_label = QLabel("CSVファイルが選択されていません")
        layout.addWidget(self.file_label)

        # Button to import CSV file
        self.load_csv_button = QPushButton("CSVファイルをインポートします")
        self.load_csv_button.setMinimumWidth(400)
        self.load_csv_button.setFixedHeight(30)
        self.load_csv_button.clicked.connect(self.load_csv_file)
        layout.addWidget(self.load_csv_button)
        
        self.run_button = QPushButton("出力")
        self.run_button.setMinimumWidth(400)
        self.run_button.setFixedHeight(30)
        self.run_button.clicked.connect(self.run_scraping)
        layout.addWidget(self.run_button)
        # self.setCentralWidget(self.run_button)
        
        self.widget = QWidget()
        self.widget.setLayout(layout)

        self.setCentralWidget(self.widget)

        self.setGeometry(100, 100, 600, 300)  # Set window size
        self.center()
    
    def center(self):
        qr = self.frameGeometry()  
        cp = QDesktopWidget().availableGeometry().center()  # Get screen center
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def run_command(self, command):
        os_name = platform.system().lower()  # Get OS name (windows, linux, darwin for macOS)
    
        if os_name == "windows":
            # Open a new Command Prompt and run the command
            subprocess.Popen(f'start cmd /k "{command}"', shell=True)
        
        elif os_name == "linux":
            # Open a new terminal window and execute the command
            subprocess.Popen(['x-terminal-emulator', '-e'] + command)

        elif os_name == "darwin":  # macOS
            # Open Terminal on macOS and run the command
            subprocess.Popen(['osascript', '-e', f'tell application "Terminal" to do script "{command}"'])

        else:
            print("Unsupported OS:", os_name)

    def load_csv_file(self):
        """Open a file dialog and load CSV file path."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options)
        
        if file_path:
            self.input_csv_path = file_path
            self.file_label.setText(f"{file_path}")
            print("Loaded CSV File:", file_path)  # Print path to console for debugging

    def show_warning(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Warning")
        msg.setText(f"{message}")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def run_scraping(self):
        if self.input_csv_path == None:
            self.show_warning(f"CSVファイルを選択してください")
            return

        if ENV == "development":
            command = f"python scraper.py {self.input_csv_path}"      # dev mode
        else:
            command = f"scraper.exe {self.input_csv_path}"        # live mode
            
        self.run_command(command)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EbayAutoApp()
    window.show()
    # sys.exit(app.exec_())
    app.exec()
