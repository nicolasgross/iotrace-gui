from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QFile


class MainWindow():
    def __init__(self):
        uiFile = QFile("iotracegui/mainwindow.ui")
        uiFile.open(QFile.ReadOnly)
        self.__window = QUiLoader().load(uiFile)
        uiFile.close()
        self.__initMenu()

    def __initMenu(self):
        self.__window.actionQuit.triggered.connect(
                QApplication.closeAllWindows)

    def show(self):
        self.__window.show()
