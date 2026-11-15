# 📄 LLM Document Extractor (Local AI)

> **Automate invoice processing, data entry, and document analysis with 100% data privacy using local Large Language Models.**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green)
![Ollama](https://img.shields.io/badge/AI-Ollama-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

## 🎯 The Problem
Businesses receive hundreds of PDF invoices, receipts, and purchase orders daily. Manually copying data (Invoice Number, Date, Total Amount, Vendor) into Excel is time-consuming, error-prone, and mind-numbing for employees.

## 💡 The Solution
**LLM Document Extractor** is a desktop application that acts as an intelligent data pipeline. You simply drag and drop a folder of documents, and the app uses a local LLM to read the text, understand the context, and export a perfectly structured Excel report.

**Why Local AI?** Unlike cloud-based solutions (OpenAI, AWS), this app uses **Ollama** to run LLMs directly on your machine. Your sensitive financial documents *never leave your computer*.

---

## 🚀 Key Features
*   **📂 Smart Drag & Drop:** Drop individual files OR entire folders. The app recursively scans directories to find all supported documents (`.pdf`, `.docx`, `.txt`).
*   **🛡️ 100% Privacy:** Runs entirely locally. No API keys, no cloud costs, no data leaks.
*   **🧠 Multi-Model Support:** Auto-detects installed Ollama models. Choose from `llama3.1`, `qwen2.5`, `mistral`, etc.
*   **⚙️ Custom Extraction Prompts:** Tell the AI exactly what to extract (e.g., *"Extract invoice number, date, and total amount"*).
*   **📊 Clean Excel Export:** Automatically formats column widths, handles missing fields gracefully, and saves data using Pandas.
*   **🚀 Multithreaded Architecture:** Processes files in the background (PyQt6 QThread), keeping the UI responsive with a live progress bar and emergency stop button.
*   **🩹 JSON Healing:** Uses `json-repair` to guarantee valid data parsing, even if the LLM hallucinates markdown formatting.

---

## 📸 Screenshots & Demo

*   **Main Interface:** 
    ![UI](https://github.com/user-attachments/assets/95c7fba3-e2b8-4961-9eb0-99551f5a272d)

*   **Excel Output:** 
    ![Excel](https://github.com/user-attachments/assets/89226d49-c2df-43b5-82e1-56c89fa1d421)


---

## 🏗️ Architecture & Tech Stack
The project is built using **Clean Architecture** principles to ensure maintainability.

*   **UI:** PyQt6 (Dark theme, Drag & Drop, QThread)
*   **AI Engine:** Ollama (local LLMs)
*   **Parsing:** `pypdf`, `python-docx`
*   **Data Handling:** `pandas`, `openpyxl`, `json-repair`
*   **Packaging:** PyInstaller (standalone `.exe`)

```text
[ GUI (PyQt6) ] -> [ QThread Worker ] -> [ Document Parser ]
                                              |
                                      [ Local LLM (Ollama) ]
                                              |
                                      [ JSON Parser ] -> [ Excel Exporter (Pandas) ]
```

---

## 🛠️ Installation & Usage

### Option 1: Using the Pre-built EXE (Windows)
1. Download the latest `LLM_Document_Extractor.exe` from the *Releases* section.
2. Ensure [Ollama](https://ollama.com/) is installed and running in the background.
3. Run the `.exe`. Drag and drop your files, and click "Start Extraction".

### Option 2: Run from Source
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/llm-document-extractor.git
   cd llm-document-extractor
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```
3. Pull a local model (we recommend `llama3.1`):
   ```bash
   ollama pull llama3.1
   ```
4. Run the app:
   ```bash
   python main.py
   ```

---

## 🧠 How it Works (Under the hood)
1. **Extraction:** Text is pulled from PDFs/DOCX files using robust Python parsers.
2. **Prompt Engineering:** The text is injected into a strict system prompt: *"You are an expert data extraction assistant. Return ONLY valid JSON..."*
3. **Ollama API:** The request is sent to the local `ollama` instance with `format="json"` to force structured output.
4. **Data Aggregation:** Results from all files are collected into a list of dictionaries and converted into a single Pandas DataFrame for Excel export.

---

## 🚧 Known Limitations
*   **Scanned PDFs (Images):** The app currently extracts the *text layer* of PDFs. If a PDF is a raw scan (image), it will yield no text. *(Future roadmap: integrate Tesseract/EasyOCR).*
*   **Context Window:** Extremely large PDFs (100+ pages) are truncated to ~30,000 characters to prevent local models from crashing.

---

## 👨‍💻 About the Developer
This project was built to demonstrate expertise in **Python, GUI Development (PyQt6), Local LLM Integration, and Process Automation**.

**Need custom modifications?**
I can adapt this pipeline for your specific business needs:
*   Integrating with your database (PostgreSQL, 1C, CRM).
*   Adding support for OCR (scanned documents).
*   Custom prompt tuning for highly specific document types.

📫 **Contact me:** [Your Email / Telegram / Upwork Link]
