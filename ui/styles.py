# ui/styles.py

DARK_THEME = """
QMainWindow {
    background-color: #1e1e1e;
}
QWidget {
    color: #d4d4d4;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
}
QListWidget {
    background-color: #252526;
    border: 2px dashed #3c3c3c;
    border-radius: 8px;
    padding: 10px;
    color: #cccccc;
}
QListWidget::item {
    padding: 5px;
    border-bottom: 1px solid #3c3c3c;
}
QComboBox, QLineEdit {
    background-color: #2d2d2d;
    border: 1px solid #3c3c3c;
    border-radius: 5px;
    padding: 8px;
    color: #ffffff;
}
QComboBox:focus, QLineEdit:focus {
    border: 1px solid #007acc;
}

/* ФИКС ВЫПАДАЮЩЕГО СПИСКА */
QComboBox QAbstractItemView {
    background-color: #2d2d2d;
    color: #ffffff;
    selection-background-color: #007acc;
    selection-color: #ffffff;
    border: 1px solid #3c3c3c;
    outline: 0; 
}
QComboBox::drop-down {
    border: 0px;
}
QComboBox::down-arrow {
    image: none; 
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #d4d4d4;
    margin-right: 10px;
}

QTextEdit, QPlainTextEdit {
    background-color: #1e1e1e;
    border: 1px solid #3c3c3c;
    border-radius: 5px;
    padding: 5px;
    color: #d4d4d4;
    font-family: 'Consolas', 'Courier New', monospace;
}
QPushButton {
    background-color: #0e639c;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 10px 20px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #1177bb;
}
QPushButton:disabled {
    background-color: #3c3c3c;
    color: #7f7f7f;
}
QPushButton#stopBtn {
    background-color: #d32f2f;
}
QPushButton#stopBtn:hover {
    background-color: #f44336;
}
QPushButton#saveBtn {
    background-color: #2e7d32;
}
QPushButton#saveBtn:hover {
    background-color: #388e3c;
}
QProgressBar {
    border: 1px solid #3c3c3c;
    border-radius: 5px;
    text-align: center;
    background-color: #252526;
}
QProgressBar::chunk {
    background-color: #007acc;
    border-radius: 4px;
}

/* ========================================= */
/* ФИКС ВСПЛЫВАЮЩИХ ОКОН (MESSAGE BOX)       */
/* ========================================= */
QMessageBox {
    background-color: #1e1e1e;
}
QMessageBox QLabel {
    color: #d4d4d4;
    background-color: transparent;
}
QMessageBox QPushButton {
    min-width: 80px;
}
"""