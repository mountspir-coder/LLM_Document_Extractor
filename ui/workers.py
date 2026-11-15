# ui/workers.py

import logging
from typing import List, Dict, Any
from PyQt6.QtCore import QThread, pyqtSignal

from parsers.document_parser import extract_text, UnsupportedFormatError, EmptyDocumentError
from core.extractor import DocumentExtractor

logger = logging.getLogger(__name__)

class ExtractionWorker(QThread):
    """
    Background worker to process multiple documents without freezing the UI.
    """
    # Signals to communicate with the GUI
    log_signal = pyqtSignal(str)                       # For general log messages
    progress_signal = pyqtSignal(int, int)             # (current_file_index, total_files)
    file_success_signal = pyqtSignal(str, dict)        # (filename, extracted_data)
    file_error_signal = pyqtSignal(str, str)           # (filename, error_message)
    finished_signal = pyqtSignal(list)                 # (list of all extracted dicts)

    def __init__(self, file_paths: List[str], prompt: str, model_name: str):
        super().__init__()
        self.file_paths = file_paths
        self.prompt = prompt
        self.model_name = model_name
        self.is_running = True
        
        # Initialize our core components
        self.extractor = DocumentExtractor()

    def run(self):
        """The main logic of the thread."""
        total_files = len(self.file_paths)
        all_results = []

        self.log_signal.emit(f"Starting extraction for {total_files} files using {self.model_name}...")

        for index, file_path in enumerate(self.file_paths):
            # Check for EMERGENCY STOP
            if not self.is_running:
                self.log_signal.emit("⚠️ Extraction aborted by user.")
                break

            filename = file_path.split("\\")[-1].split("/")[-1] # Extract just the file name
            self.log_signal.emit(f"[{index + 1}/{total_files}] Processing: {filename}")
            self.progress_signal.emit(index + 1, total_files)

            try:
                # 1. Extract text from PDF/DOCX/TXT
                text = extract_text(file_path)
                
                # 2. Send text to LLM
                extracted_data = self.extractor.extract_data(
                    text=text, 
                    custom_prompt=self.prompt, 
                    model_name=self.model_name
                )
                
                # Add the filename to the result so the user knows where it came from
                extracted_data["_source_file"] = filename
                
                # 3. Success
                all_results.append(extracted_data)
                self.file_success_signal.emit(filename, extracted_data)
                self.log_signal.emit(f"  ✅ Success: {filename}")

            except EmptyDocumentError:
                error_msg = "Document is empty or a scanned image (no text layer)."
                self.file_error_signal.emit(filename, error_msg)
                self.log_signal.emit(f"  ❌ Error: {filename} - {error_msg}")
                
            except UnsupportedFormatError:
                error_msg = "Unsupported file format."
                self.file_error_signal.emit(filename, error_msg)
                self.log_signal.emit(f"  ❌ Error: {filename} - {error_msg}")
                
            except Exception as e:
                error_msg = str(e)
                self.file_error_signal.emit(filename, error_msg)
                self.log_signal.emit(f"  ❌ LLM Error: {filename} - {error_msg}")

        # Signal that the whole batch is done, passing all collected data
        self.log_signal.emit(f"Finished processing. Successfully extracted {len(all_results)} out of {total_files} files.")
        self.finished_signal.emit(all_results)

    def stop(self):
        """Called from the GUI to stop the process."""
        self.is_running = False
        self.log_signal.emit("Stopping worker... Please wait for the current file to finish.")


# ==========================================
# TEST BLOCK (Run this file directly to test)
# ==========================================
if __name__ == "__main__":
    import sys
    import os
    from PyQt6.QtCore import QCoreApplication
    
    logging.basicConfig(level=logging.INFO)
    print("--- Testing Extraction Worker (QThread) ---")
    
    # Create a dummy text file for testing
    test_file = "sample_invoice.txt"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("INVOICE #999\nDate: 2024-01-01\nClient: Test Corp\nTotal: $1,000.00")
    
    # Create a dummy fake PDF name to simulate an error
    bad_file = "fake_missing_file.pdf"
    
    app = QCoreApplication(sys.argv)
    
    # Setup the worker
    files_to_process = [test_file, bad_file]
    worker = ExtractionWorker(
        file_paths=files_to_process,
        prompt="Extract invoice number, date, client, and total.",
        model_name="llama3.1:latest"
    )
    
    # Connect signals to console prints
    worker.log_signal.connect(lambda msg: print(f"LOG: {msg}"))
    worker.progress_signal.connect(lambda curr, total: print(f"PROGRESS: {curr}/{total}"))
    worker.file_success_signal.connect(lambda fname, data: print(f"SUCCESS: {fname} -> {data}"))
    worker.file_error_signal.connect(lambda fname, err: print(f"ERROR: {fname} -> {err}"))
    
    # When finished, quit the app
    worker.finished_signal.connect(lambda results: app.quit())
    
    # Start the thread
    worker.start()
    
    # Run the Qt event loop
    sys.exit(app.exec())
    
    # Cleanup test file
    if os.path.exists(test_file):
        os.remove(test_file)