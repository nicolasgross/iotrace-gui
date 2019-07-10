import os
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QFileDialog, QErrorMessage
from PySide2.QtCore import QFile


class MainWindow:
    def __init__(self, app, model):
        self.__app = app
        self.__model = model
        uiFile = QFile("iotracegui/main_window.ui")
        uiFile.open(QFile.ReadOnly)
        self.__window = QUiLoader().load(uiFile)
        uiFile.close()
        self.__initMenu()
        self.__initTabs()

    def __initMenu(self):
        self.__window.actionQuit.triggered.connect(self.__app.exit)
        self.__window.actionOpen.triggered.connect(self.menuFileOpen)
        # TODO open recent
        # TODO view adjust columns
        # TODO help about

    def __initTabs(self):
        self.__window.processesListView.setModel(self.__model.procsModel)

    def menuFileOpen(self):
        files = QFileDialog.getOpenFileNames(
                self.__window, "Open iotrace files", "",
                "iotrace JSON files (*.json)")
        if files[0]:
            try:
                self.__model.updateFiles(files[0])
                self.__initTabs()
            except ValueError:
                # TODO catch other errors
                errorDialog = QErrorMessage(self.__window)
                errorDialog.showMessage(
                        "The selected JSON file is not compatible with "
                        "iotrace-GUI." + os.linesep +
                        "Ensure that filenames were not changed from "
                        "filenames that were assigned by iotrace.")

    def show(self):
        self.__window.show()
