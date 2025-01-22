import sys
from PyQt6.QtWidgets import QApplication

from src.UtcTool2d.selectImage_ui_helper import SelectImageGUI_UtcTool2dIQ

if __name__ == "__main__":
    utcApp = QApplication(sys.argv)
    utcUI = SelectImageGUI_UtcTool2dIQ()
    utcUI.show()
    sys.exit(utcApp.exec())
