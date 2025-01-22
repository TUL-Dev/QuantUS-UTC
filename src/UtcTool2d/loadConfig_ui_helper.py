import os
import pickle

from PyQt6.QtWidgets import QWidget, QFileDialog
from src.UtcTool2d.loadConfig_ui import Ui_loadConfig
import src.UtcTool2d.analysisParamsSelection_ui_helper as AnalysisConfigSection

class LoadConfigGUI(Ui_loadConfig, QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.analysisParamsGUI: AnalysisConfigSection.AnalysisParamsGUI

        self.chooseFileButton.clicked.connect(self.chooseFile)
        self.clearFileButton.clicked.connect(self.clearFile)
        self.openRoiButton.clicked.connect(self.getConfigPath)
        self.backButton.clicked.connect(self.backToChoice)

    def backToChoice(self):
        self.hide()
        self.analysisParamsGUI.show()

    def chooseFile(self):
        fileName, _ = QFileDialog.getOpenFileName(None, "Open file", filter="*.pkl")
        if fileName != "":
            self.roiPathInput.setText(fileName)

    def clearFile(self):
        self.roiPathInput.clear()

    def getConfigPath(self):
        if os.path.exists(self.roiPathInput.text()):
            with open(self.roiPathInput.text(), "rb") as f:
                configInfo = pickle.load(f)

            if (self.analysisParamsGUI.imagePathInput.text() != configInfo["Image Name"] or 
                self.analysisParamsGUI.phantomPathInput.text() != configInfo["Phantom Name"]): 
                print("Selected ROI for wrong image")
                return
            
            self.analysisParamsGUI.utcData.utcAnalysis.config = configInfo["Config"]
            self.analysisParamsGUI.initParams()
            # self.analysisParamsGUI.plotRoiPreview()

            self.hide()
            self.analysisParamsGUI.show()
