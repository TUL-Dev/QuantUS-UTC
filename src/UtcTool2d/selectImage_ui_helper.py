import os
import platform
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QWidget, QApplication, QFileDialog

from pyquantus.parse.canon import findPreset
from pyquantus.parse.philipsMat import philips2dRfMatParser
from pyquantus.parse.philipsRf import philipsRfParser
from pyquantus.parse.siemens import siemensRfParser
from pyquantus.parse.clarius import clariusRfParser
from pyquantus.utc import UtcData
from pyquantus.parse.objects import ScConfig
from src.UtcTool2d.loadingScreen_ui_helper import LoadingScreenGUI
from src.UtcTool2d.selectImage_ui import Ui_selectImage
from src.UtcTool2d.roiSelection_ui_helper import RoiSelectionGUI
import src.Parsers.philips3dRf as phil3d

system = platform.system()


def selectImageHelper(pathInput, fileExts):
    if not os.path.exists(pathInput.text()):  # check if file path is manually typed
        # NOTE: .bin is currently not supported
        fileName, _ = QFileDialog.getOpenFileName(None, "Open File", filter=fileExts)
        if fileName != "":  # If valid file is chosen
            pathInput.setText(fileName)
        else:
            return


class SelectImageGUI_UtcTool2dIQ(Ui_selectImage, QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        if system == "Windows":
            self.roiSidebarLabel.setStyleSheet(
                """QLabel {
                font-size: 18px;
                color: rgb(255, 255, 255);
                background-color: rgba(255, 255, 255, 0);
                border: 0px;
                font-weight: bold;
            }"""
            )
            self.imageSelectionLabelSidebar.setStyleSheet(
                """QLabel {
                font-size: 18px;
                color: rgb(255, 255, 255);
                background-color: rgba(255, 255, 255, 0);
                border: 0px;
                font-weight: bold;
            }"""
            )
            self.imageLabel.setStyleSheet(
                """QLabel {
                font-size: 13px;
                color: rgb(255, 255, 255);
                background-color: rgba(255, 255, 255, 0);
                border: 0px;
                font-weight: bold;
            }"""
            )
            self.phantomLabel.setStyleSheet(
                """QLabel {
                font-size: 13px;
                color: rgb(255, 255, 255);
                background-color: rgba(255, 255, 255, 0);
                border: 0px;
                font-weight: bold;
            }"""
            )
            self.imageFilenameDisplay.setStyleSheet(
                """QLabel {
                font-size: 11px;
                color: rgb(255, 255, 255);
                background-color: rgba(255, 255, 255, 0);
                border: 0px;
            }"""
            )
            self.phantomFilenameDisplay.setStyleSheet(
                """QLabel {
                font-size: 11px;
                color: rgb(255, 255, 255);
                background-color: rgba(255, 255, 255, 0);
                border: 0px;
            }"""
            )
            self.analysisParamsLabel.setStyleSheet(
                """QLabel {
                font-size: 18px;
                color: rgb(255, 255, 255);
                background-color: rgba(255, 255, 255, 0);
                border: 0px;
                font-weight:bold;
            }"""
            )
            self.rfAnalysisLabel.setStyleSheet(
                """QLabel {
                font-size: 18px;
                color: rgb(255, 255, 255);
                background-color: rgba(255, 255, 255, 0);
                border: 0px;
                font-weight:bold;
            }"""
            )
            self.exportResultsLabel.setStyleSheet(
                """QLabel {
                font-size: 18px;
                color: rgb(255, 255, 255);
                background-color: rgba(255, 255, 255, 0);
                border: 0px;
                font-weight:bold;
            }"""
            )

        self.hideImageSelectionUI()

        self.welcomeGui: QWidget
        self.roiSelectionGUI = None
        self.machine = None
        self.fileExts = None
        self.frame = 0
        self.imArray: np.ndarray
        self.loadingScreen = LoadingScreenGUI()

        self.terasonButton.clicked.connect(self.terasonClicked)
        self.philipsButton.clicked.connect(self.philipsClicked)
        self.canonButton.clicked.connect(self.canonClicked)
        self.clariusButton.clicked.connect(self.clariusClicked)
        self.siemensButton.clicked.connect(self.siemensClicked)
        # self.verasonicsButton.clicked.connect(self.verasonicsClicked)
        self.chooseImageFileButton.clicked.connect(self.selectImageFile)
        self.choosePhantomFileButton.clicked.connect(self.selectPhantomFile)
        self.clearImagePathButton.clicked.connect(self.clearImagePath)
        self.clearPhantomPathButton.clicked.connect(self.clearPhantomPath)
        self.generateImageButton.clicked.connect(self.moveToRoiSelection)
        self.backButton.clicked.connect(self.backToFirstScreen)
        
    def hideImageSelectionUI(self):
        self.backButton.setHidden(True)
        self.chooseImageFileButton.setHidden(True)
        self.choosePhantomFileButton.setHidden(True)
        self.chooseImageFolderButton.setHidden(True)
        self.choosePhantomFolderButton.setHidden(True)
        self.clearImagePathButton.setHidden(True)
        self.clearPhantomPathButton.setHidden(True)
        self.selectImageErrorMsg.setHidden(True)
        self.generateImageButton.setHidden(True)
        self.imagePathInput.setHidden(True)
        self.phantomPathInput.setHidden(True)
        self.selectDataLabel.setHidden(True)
        self.imageFilenameDisplay.setHidden(True)
        self.phantomFilenameDisplay.setHidden(True)
        self.imagePathLabelCanon.setHidden(True)
        self.phantomPathLabelCanon.setHidden(True)
        self.imagePathLabelClarius.setHidden(True)
        self.phantomPathLabelClarius.setHidden(True)
        self.imagePathLabelVerasonics.setHidden(True)
        self.phantomPathLabelVerasonics.setHidden(True)
        self.imagePathLabel.setHidden(True)
        self.phantomPathLabel.setHidden(True)
        self.acceptFrameButton.setHidden(True)
        self.totalFramesLabel.setHidden(True)
        self.ofFramesLabel.setHidden(True)
        self.curFrameSlider.setHidden(True)
        self.curFrameLabel.setHidden(True)
        self.imPreview.setHidden(True)
        self.selectFrameLabel.setHidden(True)
        self.philips3dCheckBox.setHidden(True)
        
    def backToFirstScreen(self):
        self.hideImageSelectionUI()
        self.selectImageMethodLabel.setHidden(False)
        self.canonButton.setHidden(False)
        self.clariusButton.setHidden(False)
        self.verasonicsButton.setHidden(False)
        self.terasonButton.setHidden(False)
        self.philipsButton.setHidden(False)
        self.siemensButton.setHidden(False)
        

    def moveToRoiSelection(self):
        if self.machine == "Verasonics":
            self.phantomPathInput.setText(self.imagePathInput.text())
        if os.path.exists(self.imagePathInput.text()) and os.path.exists(
            self.phantomPathInput.text()
        ):
            self.loadingScreen.show()
            QApplication.processEvents()
            if self.roiSelectionGUI is not None:
                plt.close(self.roiSelectionGUI.figure)
            del self.roiSelectionGUI
            self.roiSelectionGUI = RoiSelectionGUI()
            self.roiSelectionGUI.utcData = UtcData()
            self.roiSelectionGUI.setFilenameDisplays(
                self.imagePathInput.text().split("/")[-1],
                self.phantomPathInput.text().split("/")[-1],
            )
            if self.machine == "Verasonics":
                self.roiSelectionGUI.openImageVerasonics(
                    self.imagePathInput.text(), self.phantomPathInput.text()
                )
            elif self.machine == "Canon":
                preset1 = findPreset(self.imagePathInput.text())
                preset2 = findPreset(self.phantomPathInput.text())
                if preset1 == preset2:
                    self.roiSelectionGUI.openImageCanon(
                        self.imagePathInput.text(), self.phantomPathInput.text()
                    )
                else:
                    self.selectImageErrorMsg.setText("ERROR: Presets don't match")
                    self.selectImageErrorMsg.setHidden(False)
                    return
            elif self.machine == "Clarius":
                self.openClariusImage()
                return
            elif self.machine == "Terason":
                self.roiSelectionGUI.openImageTerason(
                    self.imagePathInput.text(), self.phantomPathInput.text()
                )
            elif self.machine == "Philips":
                self.openPhilipsImage()
                return
            elif self.machine == "Siemens":
                self.openSiemensImage()
                return
            else:
                print("ERROR: Machine match not found")
                return
            self.roiSelectionGUI.show()
            self.roiSelectionGUI.lastGui = self
            self.selectImageErrorMsg.setHidden(True)
            self.loadingScreen.hide()
            self.hide()

    def openSiemensImage(self):
        imageFilePath = self.imagePathInput.text()
        phantomFilePath = self.phantomPathInput.text()

        self.imArray, self.imgDataStruct, self.imgInfoStruct, self.refDataStruct, self.refInfoStruct = siemensRfParser(
            imageFilePath, phantomFilePath)
        self.initialImgRf = self.imgDataStruct.rf
        self.initialRefRf = self.refDataStruct.rf

        self.acceptFrameButton.clicked.connect(self.acceptSiemensFrame)
        self.displaySlidingFrames()
        
    def openClariusImage(self):
        imageRfPath = self.imagePathInput.text()
        imageInfoPath = imageRfPath.replace(".raw", ".yml")
        imageTgcPath = imageRfPath.replace("_rf.raw", "_env.tgc.yml")
        phantomRfPath = self.phantomPathInput.text()
        phantomInfoPath = phantomRfPath.replace(".raw", ".yml")
        phantomTgcPath = phantomRfPath.replace("_rf.raw", "_env.tgc.yml")

        self.imgDataStruct, self.imgInfoStruct, self.refDataStruct, self.refInfoStruct = clariusRfParser(
            imageRfPath, imageTgcPath, imageInfoPath,
            phantomRfPath, phantomTgcPath, phantomInfoPath
        )
        self.imArray = self.imgDataStruct.scBmode
        self.initialImgRf = self.imgDataStruct.rf
        self.initialRefRf = self.refDataStruct.rf

        scConfig = ScConfig()
        scConfig.width = self.imgInfoStruct.width1
        scConfig.tilt = self.imgInfoStruct.tilt1
        scConfig.startDepth = self.imgInfoStruct.startDepth1
        scConfig.endDepth = self.imgInfoStruct.endDepth1

        utcData = UtcData()
        utcData.scConfig = scConfig
        utcData.scConfig = scConfig
        self.roiSelectionGUI.utcData = utcData
        self.roiSelectionGUI.ultrasoundImage.xmap = self.imgDataStruct.scBmodeStruct.xmap
        self.roiSelectionGUI.ultrasoundImage.ymap = self.imgDataStruct.scBmodeStruct.ymap

        self.acceptFrameButton.clicked.connect(self.acceptClariusFrame)
        self.displaySlidingFrames()

    def openPhilipsImage(self):
        imageFilePath = Path(self.imagePathInput.text())
        phantomFilePath = Path(self.phantomPathInput.text())
        
        if self.philips3dCheckBox.isChecked():
            self.imgDataStruct, self.imgInfoStruct = phil3d.getVolume(imageFilePath)
            self.refDataStruct, self.refInfoStruct = phil3d.getVolume(phantomFilePath)
            self.imArray = self.imgDataStruct.bMode
            self.initialImgRf = self.imgDataStruct.rf
            self.initialRefRf = self.refDataStruct.rf
            self.displaySlidingFrames()
            return
        
        imageFile = open(imageFilePath, 'rb')
        imageSig = list(imageFile.read(8))
        phantomFile = open(phantomFilePath, 'rb')
        phantomSig = list(phantomFile.read(8))
        
        if imageFilePath.suffix == '.rf':
            assert imageSig == [0,0,0,0,255,255,0,0]
            destImgFilePath = Path(imageFilePath.__str__().replace('.rf', '.mat'))
            philipsRfParser(imageFilePath.__str__())
            
        if phantomFilePath.suffix == '.rf':
            assert phantomSig == [0,0,0,0,255,255,0,0]
            destPhantomFilePath = Path(phantomFilePath.__str__().replace('.rf', '.mat'))
            philipsRfParser(phantomFilePath.__str__())
        
        if imageFilePath.suffix == '.mat':
            destImgFilePath = imageFilePath
        if phantomFilePath.suffix == '.mat':
            destPhantomFilePath = phantomFilePath

        self.imgDataStruct, self.imgInfoStruct, self.refDataStruct, self.refInfoStruct = philips2dRfMatParser(
            destImgFilePath, destPhantomFilePath, self.frame)
        self.imData = self.imgDataStruct.bMode
        self.initialImgRf = [self.imgDataStruct.rf]
        self.initialRefRf = [self.refDataStruct.rf]
        
        scConfig = ScConfig()
        scConfig.width = self.imgInfoStruct.width1
        scConfig.tilt = self.imgInfoStruct.tilt1
        scConfig.startDepth = self.imgInfoStruct.startDepth1
        scConfig.endDepth = self.imgInfoStruct.endDepth1

        utcData = UtcData()
        utcData.scConfig = scConfig
        self.roiSelectionGUI.utcData = utcData
        self.roiSelectionGUI.ultrasoundImage.bmode = self.imgDataStruct.bMode
        self.roiSelectionGUI.ultrasoundImage.scBmode = self.imgDataStruct.scBmodeStruct.scArr
        self.roiSelectionGUI.ultrasoundImage.xmap = self.imgDataStruct.scBmodeStruct.xmap
        self.roiSelectionGUI.ultrasoundImage.ymap = self.imgDataStruct.scBmodeStruct.ymap
        self.roiSelectionGUI.ultrasoundImage.axialResRf = self.imgInfoStruct.depth / self.imgDataStruct.rf.shape[0]
        self.roiSelectionGUI.ultrasoundImage.lateralResRf = self.roiSelectionGUI.ultrasoundImage.axialResRf * (
            self.imgDataStruct.rf.shape[0]/self.imgDataStruct.rf.shape[1]
        ) # placeholder
        self.acceptFrame()

    def displaySlidingFrames(self):
        self.imData = np.array(self.imArray[self.frame]).reshape(self.imArray.shape[1], self.imArray.shape[2])
        self.imData = np.require(self.imData,np.uint8,'C')
        self.bytesLine = self.imData.strides[0]
        self.arHeight = self.imData.shape[0]
        self.arWidth = self.imData.shape[1]
        self.qIm = QImage(self.imData, self.arWidth, self.arHeight, self.bytesLine, QImage.Format.Format_Grayscale8)

        quotient = self.imgInfoStruct.width / self.imgInfoStruct.depth
        if quotient > (721/501):
            self.widthScale = 721
            self.depthScale = self.widthScale / (self.imgInfoStruct.width/self.imgInfoStruct.depth)
        else:
            self.widthScale = 501 * quotient
            self.depthScale = 501
        self.yBorderMin = 110 + ((501 - self.depthScale)/2)
        self.yBorderMax = 611 - ((501 - self.depthScale)/2)
        self.xBorderMin = 410 + ((721 - self.widthScale)/2)
        self.xBorderMax = 1131 - ((721 - self.widthScale)/2)

        self.imPreview.setPixmap(QPixmap.fromImage(self.qIm).scaled(self.imPreview.width(), self.imPreview.height(), Qt.AspectRatioMode.IgnoreAspectRatio))

        self.totalFramesLabel.setHidden(False)
        self.ofFramesLabel.setHidden(False)
        self.curFrameSlider.setHidden(False)
        self.curFrameLabel.setHidden(False)
        self.imPreview.setHidden(False)
        self.selectFrameLabel.setHidden(False)
        self.imagePathInput.setHidden(True)
        self.phantomPathInput.setHidden(True)
        self.clearImagePathButton.setHidden(True)
        self.clearPhantomPathButton.setHidden(True)
        self.generateImageButton.setHidden(True)
        self.selectImageMethodLabel.setHidden(True)
        self.canonButton.setHidden(True)
        self.clariusButton.setHidden(True)
        self.imagePathLabelClarius.setHidden(True)
        self.phantomPathLabelClarius.setHidden(True)
        self.verasonicsButton.setHidden(True)
        self.terasonButton.setHidden(True)
        self.philipsButton.setHidden(True)
        self.siemensButton.setHidden(True)
        self.chooseImageFileButton.setHidden(True)
        self.choosePhantomFileButton.setHidden(True)
        self.imagePathLabel.setHidden(True)
        self.phantomPathLabel.setHidden(True)
        self.selectDataLabel.setHidden(True)
        self.acceptFrameButton.setHidden(False)
        self.philips3dCheckBox.setHidden(True)

        self.curFrameSlider.setMinimum(0)
        self.curFrameSlider.setMaximum(self.imArray.shape[0]-1)
        self.curFrameLabel.setText("0")
        self.totalFramesLabel.setText(str(self.imArray.shape[0]-1))
        self.curFrameSlider.valueChanged.connect(self.frameChanged)

        self.loadingScreen.hide()
        self.update()   
    
    def frameChanged(self):
        self.frame = self.curFrameSlider.value()
        self.curFrameLabel.setText(str(self.frame))
        self.plotPreviewFrame()

    def acceptSiemensFrame(self):
        self.roiSelectionGUI.ultrasoundImage.bmode = self.imgDataStruct.bMode[self.frame]
        self.roiSelectionGUI.ultrasoundImage.axialResRf = self.imgInfoStruct.depth / self.initialImgRf.shape[1]
        self.roiSelectionGUI.ultrasoundImage.lateralResRf = self.roiSelectionGUI.ultrasoundImage.axialResRf * (
            self.initialImgRf.shape[1]/self.initialImgRf.shape[2]
        ) # placeholder
        self.imgDataStruct.rf = self.initialImgRf[self.frame]
        self.refDataStruct.rf = self.initialRefRf[0]
        self.acceptFrame()

    def acceptClariusFrame(self):
        self.roiSelectionGUI.ultrasoundImage.scBmode = self.imgDataStruct.scBmode[self.frame]
        self.roiSelectionGUI.ultrasoundImage.bmode = self.imgDataStruct.bMode[self.frame]
        self.roiSelectionGUI.ultrasoundImage.axialResRf = self.imgInfoStruct.depth / self.initialImgRf.shape[1]
        self.roiSelectionGUI.ultrasoundImage.lateralResRf = self.roiSelectionGUI.ultrasoundImage.axialResRf * (
            self.initialImgRf.shape[1]/self.initialImgRf.shape[2]
        )
        self.imgDataStruct.rf = self.initialImgRf[self.frame]
        self.refDataStruct.rf = self.initialRefRf[self.frame]
        self.acceptFrame()

    def acceptFrame(self):
        self.roiSelectionGUI.frame = self.frame
        self.roiSelectionGUI.processImage(self.imgDataStruct, self.refDataStruct, self.imgInfoStruct, self.refInfoStruct)
        self.roiSelectionGUI.lastGui = self
        self.roiSelectionGUI.show()
        self.loadingScreen.hide()
        self.hide()

    def plotPreviewFrame(self):
        self.imData = np.array(self.imArray[self.frame]).reshape(self.imArray.shape[1], self.imArray.shape[2])
        self.imData = np.require(self.imData,np.uint8,'C')
        self.qIm = QImage(self.imData, self.arWidth, self.arHeight, self.bytesLine, QImage.Format.Format_Grayscale8)
        self.imPreview.setPixmap(QPixmap.fromImage(self.qIm).scaled(self.imPreview.width(), self.imPreview.height(), Qt.AspectRatioMode.IgnoreAspectRatio))
        self.update()

    def clearImagePath(self):
        self.imagePathInput.clear()

    def clearPhantomPath(self):
        self.phantomPathInput.clear()

    def chooseImagePrep(self):
        self.backButton.setHidden(False)
        self.imagePathInput.setHidden(False)
        self.phantomPathInput.setHidden(False)
        self.clearImagePathButton.setHidden(False)
        self.clearPhantomPathButton.setHidden(False)
        self.generateImageButton.setHidden(False)
        self.selectImageMethodLabel.setHidden(True)
        self.canonButton.setHidden(True)
        self.clariusButton.setHidden(True)
        self.verasonicsButton.setHidden(True)
        self.terasonButton.setHidden(True)
        self.philipsButton.setHidden(True)
        self.siemensButton.setHidden(True)

    def philipsClicked(self):
        self.chooseImagePrep()
        self.selectDataLabel.setHidden(False)
        self.imagePathLabel.setHidden(False)
        self.phantomPathLabel.setHidden(False)
        self.chooseImageFileButton.setHidden(False)
        self.choosePhantomFileButton.setHidden(False)
        self.philips3dCheckBox.setHidden(False)

        self.imagePathLabel.setText("Input Path to Image file\n (.rf, .mat)")
        self.phantomPathLabel.setText("Input Path to Phantom file\n (.rf, .mat)")

        self.machine = "Philips"
        self.fileExts = "*.rf *.mat"

    def terasonClicked(self):
        self.chooseImagePrep()
        self.selectDataLabel.setHidden(False)
        self.imagePathLabel.setHidden(False)
        self.phantomPathLabel.setHidden(False)
        self.chooseImageFileButton.setHidden(False)
        self.choosePhantomFileButton.setHidden(False)

        self.imagePathLabel.setText("Input Path to Image file\n (.mat)")
        self.phantomPathLabel.setText("Input Path to Phantom file\n (.mat)")

        self.machine = "Terason"
        self.fileExts = "*.mat"

    def siemensClicked(self):
        self.chooseImagePrep()
        self.selectDataLabel.setHidden(False)
        self.imagePathLabel.setHidden(False)
        self.phantomPathLabel.setHidden(False)
        self.chooseImageFileButton.setHidden(False)
        self.choosePhantomFileButton.setHidden(False)

        self.imagePathLabel.setText("Input Path to Image file\n (.rfd)")
        self.phantomPathLabel.setText("Input Path to Phantom file\n (.rfd)")

        self.machine = "Siemens"
        self.fileExts = "*.rfd"

    def canonClicked(
        self,
    ):  # Move user to screen to select individual files to generate image
        self.chooseImagePrep()
        self.selectDataLabel.setHidden(False)
        self.imagePathLabelCanon.setHidden(False)
        self.phantomPathLabelCanon.setHidden(False)
        self.chooseImageFileButton.setHidden(False)
        self.choosePhantomFileButton.setHidden(False)

        self.machine = "Canon"
        self.fileExts = "*.bin"

    def clariusClicked(self):
        self.chooseImagePrep()
        self.selectDataLabel.setHidden(False)
        self.imagePathLabelClarius.setHidden(False)
        self.phantomPathLabelClarius.setHidden(False)
        self.chooseImageFileButton.setHidden(False)
        self.choosePhantomFileButton.setHidden(False)

        self.machine = "Clarius"
        self.fileExts = "*.raw"

    def verasonicsClicked(
        self,
    ):  # Move user to screen to select individual files to generate image
        self.chooseImagePrep()
        self.selectDataLabel.setHidden(False)
        self.imagePathLabelVerasonics.setHidden(False)
        self.chooseImageFileButton.setHidden(False)

        self.phantomPathInput.setHidden(True)
        self.clearPhantomPathButton.setHidden(True)

        imagePathLabelPos = self.imagePathLabelCanon.pos()
        imagePathLabelPos.setX(625)
        self.imagePathLabelVerasonics.move(imagePathLabelPos)
        chooseImageFilePos = self.chooseImageFileButton.pos()
        chooseImageFilePos.setX(625)
        self.chooseImageFileButton.move(chooseImageFilePos)
        clearImagePathPos = self.clearImagePathButton.pos()
        clearImagePathPos.setX(765)
        self.clearImagePathButton.move(clearImagePathPos)
        imagePathPos = self.imagePathInput.pos()
        imagePathPos.setX(655)
        self.imagePathInput.move(imagePathPos)

        self.machine = "Verasonics"
        self.fileExts = "*.mat"

    def selectImageFile(self):
        # Create folder to store ROI drawings
        if os.path.exists("Junk"):
            shutil.rmtree("Junk")
        os.mkdir("Junk")

        selectImageHelper(self.imagePathInput, self.fileExts)
        self.selectImageErrorMsg.setHidden(True)

    def selectPhantomFile(self):
        selectImageHelper(self.phantomPathInput, self.fileExts)
        self.selectImageErrorMsg.setHidden(True)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = SelectImageGUI_UtcTool2dIQ()
    ui.show()
    sys.exit(app.exec_())

