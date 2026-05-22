"""
MyDCIMFiles
A minimalist MTP transfer utility for FreeBSD.
Author: [Andi-Mihai Anton]
License: 2-Clause BSD
"""

import sys
import subprocess
import os
import math
from datetime import datetime

# Force a standard theme to avoid DBus warnings on FreeBSD
os.environ["QT_QPA_PLATFORMTHEME"] = "qt6ct" 

from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QCheckBox, QLineEdit, QListWidget, 
                             QPushButton, QLabel, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, QCoreApplication, QTimer

class MyDCIMFiles(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MyDCIMFiles : Connecting...")
        self.resize(650, 750)
        self.remote_path = "DCIM/Camera"
        self.all_files = [] 
        self.transfer_queue = [] # Coada de așteptare pentru procesare secvențială

        self.init_ui()
        # Start scanning after UI is visible
        QTimer.singleShot(100, self.refresh_file_list)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.status_label = QLabel("Initializing...")
        self.status_label.setStyleSheet("font-weight: bold; color: #2c3e50; padding: 5px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        filter_layout = QHBoxLayout()
        self.chk_images = QCheckBox("Images")
        self.chk_videos = QCheckBox("Videos")
        self.chk_images.stateChanged.connect(self.update_display_list)
        self.chk_videos.stateChanged.connect(self.update_display_list)
        filter_layout.addWidget(self.chk_images)
        filter_layout.addWidget(self.chk_videos)
        layout.addLayout(filter_layout)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search file...")
        self.search_input.textChanged.connect(self.update_display_list)
        layout.addWidget(self.search_input)

        self.file_list_widget = QListWidget()
        self.file_list_widget.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        layout.addWidget(self.file_list_widget)

        button_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("Refresh List")
        self.btn_refresh.clicked.connect(self.refresh_file_list)
        
        self.btn_download = QPushButton("Download Selected")
        self.btn_download.setStyleSheet("background-color: #d1e7dd;")
        self.btn_download.clicked.connect(self.download_file)
        
        self.btn_upload = QPushButton("Upload to Camera")
        self.btn_upload.setStyleSheet("background-color: #cfe2ff;")
        self.btn_upload.clicked.connect(self.upload_files)
        
        button_layout.addWidget(self.btn_refresh)
        button_layout.addWidget(self.btn_download)
        button_layout.addWidget(self.btn_upload)
        layout.addLayout(button_layout)

    def set_loading_state(self, is_loading, message=""):
        if is_loading:
            self.status_label.setText(f"⏳ {message}")
            self.centralWidget().setEnabled(False)
        else:
            self.status_label.setText(message)
            self.centralWidget().setEnabled(True)
        QCoreApplication.processEvents()
        
    def format_size(self, size_bytes):
        try:
            size_bytes = int(size_bytes)
            if size_bytes <= 0: return "0 B"
            size_name = ("B", "KB", "MB", "GB", "TB")
            i = int(math.floor(math.log(size_bytes, 1024)))
            p = math.pow(1024, i)
            s = round(size_bytes / p, 2)
            return f"{s} {size_name[i]}"
        except:
            return "Unknown Size"
            
    def get_timestamp(self):
        return datetime.now().strftime("%H:%M:%S")

    def refresh_file_list(self):
        timestamp_start = self.get_timestamp()
        print(f"\n--- Scanning MTP Device at {timestamp_start} ---")
        self.set_loading_state(True, "Scanning files... please wait")
        
        try:
            result = subprocess.run(
                ["aft-mtp-cli", f"ls {self.remote_path}"], 
                capture_output=True, text=True
            )
            
            if result.returncode != 0:
                self.setWindowTitle("MyDCIMFiles : Disconnected")
                self.set_loading_state(False, "Error: Check connection.")
                return 

            self.setWindowTitle("MyDCIMFiles : Connected")
            lines = result.stdout.splitlines()
            self.all_files = []

            for line in lines:
                parts = line.strip().split()
                if len(parts) < 2: continue
                size_val = 0
                actual_name = ""
                if parts[0].isdigit() and parts[1].isdigit():
                    size_val = int(parts[1])
                    actual_name = " ".join(parts[2:])
                elif parts[0].isdigit():
                    actual_name = " ".join(parts[1:])
                else: continue
                if not actual_name or ".pending" in actual_name.lower() or actual_name.startswith("."):
                    continue
                if size_val > 0:
                    readable_size = self.format_size(size_val)
                    self.all_files.append(f"{actual_name} | {readable_size}")
                else:
                    self.all_files.append(actual_name)

            self.all_files.sort(key=lambda x: x.lower())
            self.update_display_list()
            
            timestamp_end = self.get_timestamp()
            self.set_loading_state(False, f"Done! {len(self.all_files)} files found. [{timestamp_end}]")
            print(f"Log: Found {len(self.all_files)} files.")
            print(f"--- Scan Finished at {timestamp_end} ---\n")
            
        except Exception as e:
            self.setWindowTitle("MyDCIMFiles : Error")
            self.set_loading_state(False, "Error during scan.")

    def update_display_list(self):
        self.file_list_widget.clear()
        search_text = self.search_input.text().lower()
        img_ext = ('.jpg', '.jpeg', '.png', '.gif', '.heic')
        vid_ext = ('.mp4', '.mkv', '.mov', '.avi', '.3gp')

        for entry in self.all_files:
            file_name = entry.split(" | ")[0] 
            if search_text and search_text not in file_name.lower(): 
                continue
                
            is_img = file_name.lower().endswith(img_ext)
            is_vid = file_name.lower().endswith(vid_ext)

            if not self.chk_images.isChecked() and not self.chk_videos.isChecked():
                self.file_list_widget.addItem(entry)
            elif self.chk_images.isChecked() and is_img:
                self.file_list_widget.addItem(entry)
            elif self.chk_videos.isChecked() and is_vid:
                self.file_list_widget.addItem(entry)

    def download_file(self):
        selected_items = self.file_list_widget.selectedItems()
        if not selected_items: return
        
        self.transfer_queue = []
        count = len(selected_items)

        if count == 1:
            remote_name = selected_items[0].text().split(" | ")[0]
            save_path, _ = QFileDialog.getSaveFileName(self, "Save File As...", remote_name)
            if save_path:
                self.transfer_queue.append((remote_name, save_path))
        else:
            dest_dir = QFileDialog.getExistingDirectory(self, "Select Destination Directory")
            if dest_dir:
                for item in selected_items:
                    remote_name = item.text().split(" | ")[0]
                    save_path = os.path.join(dest_dir, remote_name)
                    self.transfer_queue.append((remote_name, save_path))
        
        if self.transfer_queue:
            print(f"\n--- Starting Download of {len(self.transfer_queue)} file(s) ---")
            # Pauză de 150ms pentru a permite ferestrei QFileDialog să dispară vizual
            QTimer.singleShot(150, self._process_download_queue)

    def _process_download_queue(self):
        if not self.transfer_queue:
            timestamp = self.get_timestamp()
            print(f"--- All tasks finished at {timestamp} ---\n")
            self.set_loading_state(False, f"Done! [{timestamp}]")
            return

        remote_name, local_path = self.transfer_queue.pop(0)
        self._execute_download(remote_name, local_path)
        
        # Continuăm coada după o mini-pauză pentru refresh UI
        QTimer.singleShot(50, self._process_download_queue)

    def _execute_download(self, remote_name, local_path):
        try:
            print(f"Log: Downloading {remote_name}...", flush=True) 
            self.set_loading_state(True, f"Downloading: {remote_name}")
            
            # Reconstruim comanda ca un singur string brut, fix cum îi place lui aft-mtp-cli
            command = f'aft-mtp-cli "get \\"{self.remote_path}/{remote_name}\\" \\"{local_path}\\""'
            
            # Rulăm prin shell=True ca să poată parsa ghilimelele, dar FĂRĂ capture_output
            result = subprocess.run(
                command,
                shell=True
            )
            
            if result.returncode == 0:
                print(f"Log: -> OK [{self.get_timestamp()}]\n")
            else:
                print(f"Log: -> FAILED! Exit code: {result.returncode}\n")
        except Exception as e:
            print(f"Log Error: {e}\n")

    def upload_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files to Upload")
        if not files: return
        
        existing_names = [f.split(" | ")[0] for f in self.all_files]
        self.transfer_queue = []

        for f in files:
            file_name = os.path.basename(f)
            if file_name in existing_names:
                ans = QMessageBox.question(self, "Overwrite?", f"Overwrite {file_name}?", 
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if ans == QMessageBox.StandardButton.No: continue
            self.transfer_queue.append(f)

        if self.transfer_queue:
            print(f"\n--- Batch Upload Started ---")
            QTimer.singleShot(150, self._process_upload_queue)

    def _process_upload_queue(self):
        if not self.transfer_queue:
            timestamp = self.get_timestamp()
            self.set_loading_state(False, f"Upload complete. [{timestamp}]")
            print(f"--- Batch upload complete at {timestamp} ---\n")
            self.refresh_file_list()
            return

        file_path = self.transfer_queue.pop(0)
        file_name = os.path.basename(file_path)
        
        try:
            self.set_loading_state(True, f"Uploading: {file_name}")
            print(f"Log: Uploading {file_name}...", end=" ", flush=True)
            result = subprocess.run(
                ["aft-mtp-cli", f"put \"{file_path}\" \"{self.remote_path}\""],
                capture_output=True, text=True
            )
            print("-> OK" if result.returncode == 0 else "-> FAILED")
        except Exception as e:
            print(f"Log Error: {e}")

        QTimer.singleShot(50, self._process_upload_queue)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyDCIMFiles()
    window.show()
    sys.exit(app.exec())
