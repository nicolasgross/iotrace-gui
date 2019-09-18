import os
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QFileDialog, QErrorMessage
from PySide2.QtCore import QFile, Slot

from iotracegui.view.filestats_tab import FilestatsTab
from iotracegui.view.syscalls_tab import SyscallsTab


class MainWindow:

    def __init__(self, app, model):
        self.__app = app
        self.__model = model
        uiFile = QFile("iotracegui/view/main_window.ui")
        uiFile.open(QFile.ReadOnly)
        self.__window = QUiLoader().load(uiFile)
        uiFile.close()
        self.__initMenu()
        self.__initTabs()
        self.__initProcListView()

    def __initMenu(self):
        self.__window.actionQuit.triggered.connect(self.__app.exit) # TODO confirmation
        self.__window.actionOpen.triggered.connect(self.__menuFileOpen)
        # TODO help about

    def __initProcListView(self):
        self.__model.modelsChanged.connect(self.__refreshProcListView)
        self.__window.processesListView.setModel(self.__model.getProcsModel())
        self.__window.processesListView.selectionModel(). \
            currentChanged.connect(self.__filestatsTab.showSelectedProc)
        self.__window.processesListView.selectionModel(). \
            currentChanged.connect(self.__syscallsTab.showSelectedProc)

    def __initTabs(self):
        self.__filestatsTab = FilestatsTab(self.__window, self.__model)
        self.__syscallsTab = SyscallsTab(self.__window, self.__model)

    def __menuFileOpen(self):
        files = QFileDialog.getOpenFileNames(
                self.__window, "Open iotrace files", "",
                "iotrace JSON files (*.json)")
        if files[0]:
            try:
                self.__model.setFiles(files[0])
            except ValueError:
                # TODO catch other errors
                errorDialog = QErrorMessage(self.__window)
                errorDialog.showMessage(
                        "The selected JSON file is not compatible with "
                        "iotrace-GUI." + os.linesep +
                        "Ensure that filenames were not changed from "
                        "filenames that were assigned by iotrace.")

    @Slot()
    def __refreshProcListView(self):
        self.__window.processesListView.selectionModel(). \
            currentChanged.disconnect(self.__filestatsTab.showSelectedProc)
        self.__window.processesListView.selectionModel(). \
            currentChanged.disconnect(self.__syscallsTab.showSelectedProc)

        self.__window.processesListView.setModel(self.__model.getProcsModel())

        self.__window.processesListView.selectionModel(). \
            currentChanged.connect(self.__filestatsTab.showSelectedProc)
        self.__window.processesListView.selectionModel(). \
            currentChanged.connect(self.__syscallsTab.showSelectedProc)
        self.__window.processesListView.setFocus()

    def show(self):
        self.__window.show()
