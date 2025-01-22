from pathlib import Path

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QMovie
from PyQt6.QtCore import QSize

from src.UtcTool2d.loadingScreen_ui import Ui_LoadingScreen

class LoadingScreenGUI(Ui_LoadingScreen, QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        rect = self.loadingLabel.geometry()
        size = QSize(min(rect.width(), rect.height()), min(rect.width(), rect.height()))
        self.gif = QMovie(str(Path("Images/loading-gif.gif")))
        self.gif.setScaledSize(size)
        self.loadingLabel.setMovie(self.gif)
        self.gif.start()