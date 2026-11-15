# ui/main_window.py

import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QListWidget, QComboBox, QTextEdit, QPushButton,
                             QLabel, QProgressBar, QPlainTextEdit, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt

from ui.styles import DARK_THEME
from ui.workers import ExtractionWorker
from core.llm_client import LLMClient
from core.excel_exporter import ExcelExporter

# ==========================================
# КАСТОМНЫЙ СПИСОК ДЛЯ DRAG & DROP (Папки + Файлы)
# ==========================================
class DropListWidget(QListWidget):
    """Специальный список, который принимает файлы И папки."""
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        paths = [u.toLocalFile() for u in event.mimeData().urls()]
        for path in paths:
            if os.path.isdir(path):
                # Если это папка - сканируем её
                self.main_window.log(f"📂 Scanning folder: {os.path.basename(path)}...")
                self._scan_folder(path)
            elif os.path.isfile(path):
                # Если это файл - добавляем
                self._add_file(path)

    def _scan_folder(self, folder_path):
        """Рекурсивно обходит папку и добавляет все поддерживаемые файлы."""
        found_count = 0
        for root, _, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(root, file)
                if self._is_supported(full_path):
                    self._add_file(full_path)
                    found_count += 1
        
        if found_count > 0:
            self.main_window.log(f"   ✅ Found {found_count} supported files in folder.")
        else:
            self.main_window.log(f"   ⚠️ No supported files (PDF, DOCX, TXT) found in folder.")

    def _is_supported(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        return ext in ('.pdf', '.docx', '.txt')

    def _add_file(self, file_path):
        """Добавляет файл в список, если его там еще нет."""
        if not self._is_supported(file_path):
            # Логируем только если это одиночный файл (чтобы не спамить при сканировании папки)
            if not os.path.basename(file_path).startswith('.'):
                 self.main_window.log(f"⚠️ Unsupported format ignored: {os.path.basename(file_path)}")
            return
            
        # Проверка на дубликаты
        items = [self.item(i).text() for i in range(self.count())]
        if file_path not in items:
            self.addItem(file_path)


# ==========================================
# ГЛАВНОЕ ОКНО
# ==========================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LLM Document Extractor (Local AI)")
        self.resize(900, 700)
        
        self.worker = None
        self.extracted_data = [] 
        
        self.init_ui()
        self.setStyleSheet(DARK_THEME)
        self.load_models()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Верхняя панель: Настройки ---
        settings_layout = QHBoxLayout()
        
        model_layout = QVBoxLayout()
        model_layout.addWidget(QLabel("Select LLM Model:"))
        self.model_combo = QComboBox()
        model_layout.addWidget(self.model_combo)
        
        prompt_layout = QVBoxLayout()
        prompt_layout.addWidget(QLabel("Extraction Task (What to extract?):"))
        self.prompt_input = QTextEdit()
        self.prompt_input.setMaximumHeight(60)
        self.prompt_input.setText("Extract invoice number, date, customer name, and total amount.")
        prompt_layout.addWidget(self.prompt_input)

        settings_layout.addLayout(model_layout, stretch=1)
        settings_layout.addLayout(prompt_layout, stretch=3)
        main_layout.addLayout(settings_layout)

        # --- Средняя панель: Файлы и Логи ---
        middle_layout = QHBoxLayout()

        files_layout = QVBoxLayout()
        files_layout.addWidget(QLabel("Drag & Drop Files OR Folders Here:"))
        # Используем наш кастомный класс!
        self.file_list = DropListWidget(self)
        files_layout.addWidget(self.file_list)
        
        log_layout = QVBoxLayout()
        log_layout.addWidget(QLabel("Execution Log:"))
        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
        log_layout.addWidget(self.log_output)

        middle_layout.addLayout(files_layout, stretch=1)
        middle_layout.addLayout(log_layout, stretch=2)
        main_layout.addLayout(middle_layout, stretch=1)

        # --- Прогресс-бар ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # --- Нижняя панель: Кнопки ---
        bottom_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton("Clear List")
        self.clear_btn.clicked.connect(self.clear_files)
        
        self.start_btn = QPushButton("Start Extraction")
        self.start_btn.clicked.connect(self.start_extraction)
        
        self.stop_btn = QPushButton("🛑 Stop")
        self.stop_btn.setObjectName("stopBtn")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_extraction)
        
        self.save_btn = QPushButton("💾 Save to Excel")
        self.save_btn.setObjectName("saveBtn")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_to_excel)

        bottom_layout.addWidget(self.clear_btn)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.start_btn)
        bottom_layout.addWidget(self.stop_btn)
        bottom_layout.addWidget(self.save_btn)
        
        main_layout.addLayout(bottom_layout)

    def log(self, message: str):
        self.log_output.appendPlainText(message)
        scrollbar = self.log_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def load_models(self):
        client = LLMClient()
        if not client.is_available():
            self.log("❌ ERROR: Ollama is not running. Please start it.")
            return
            
        models = client.get_available_models()
        self.model_combo.addItems(models)
        
        index = self.model_combo.findText("llama3.1:latest")
        if index >= 0:
            self.model_combo.setCurrentIndex(index)
        self.log(f"✅ Loaded {len(models)} models. Ready to work.")

    def clear_files(self):
        self.file_list.clear()
        self.extracted_data = []
        self.log_output.clear()
        self.save_btn.setEnabled(False)
        self.progress_bar.setVisible(False)

    def start_extraction(self):
        if self.file_list.count() == 0:
            QMessageBox.warning(self, "No Files", "Please add at least one file.")
            return

        files = [self.file_list.item(i).text() for i in range(self.file_list.count())]
        prompt = self.prompt_input.toPlainText().strip()
        model = self.model_combo.currentText()

        if not prompt:
            QMessageBox.warning(self, "Empty Prompt", "Please enter an extraction task.")
            return

        self.log_output.clear()
        self.extracted_data = []
        self.save_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.start_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        self.worker = ExtractionWorker(files, prompt, model)
        self.worker.log_signal.connect(self.log)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.finished_signal.connect(self.on_worker_finished)
        self.worker.start()

    def stop_extraction(self):
        if self.worker:
            self.worker.stop()
            self.stop_btn.setEnabled(False)
            self.log("⏳ Finishing current file before stopping...")

    def update_progress(self, current, total):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)

    def on_worker_finished(self, results):
        self.extracted_data = results
        self.start_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        if results:
            self.save_btn.setEnabled(True)
            self.log(f"🎉 Processing complete! {len(results)} files ready to export.")
        else:
            self.log("⚠️ No data extracted.")

    def save_to_excel(self):
        if not self.extracted_data:
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Excel Report", 
            os.path.join(os.path.expanduser("~"), "Documents", "Extracted_Report.xlsx"),
            "Excel Files (*.xlsx)"
        )
        
        if filepath:
            success = ExcelExporter.save_to_excel(self.extracted_data, filepath)
            if success:
                QMessageBox.information(self, "Success", f"File successfully saved to:\n{filepath}")
                self.log(f"💾 Saved to Excel: {filepath}")
            else:
                QMessageBox.critical(self, "Error", "Failed to save Excel file.")