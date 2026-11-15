# main.py

import sys
import ctypes
import logging
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

# Включаем логирование в консоль
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Фикс для масштабирования Windows (чтобы интерфейс не был мыльным)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()