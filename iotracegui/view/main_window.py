import os
from PySide2.QtWidgets import QFileDialog, QErrorMessage, QMainWindow, \
        QMessageBox
from PySide2.QtCore import Slot

from iotracegui.view.ui_main_window import Ui_MainWindow
from iotracegui.view.filestats_tab import FilestatsTab
from iotracegui.view.syscalls_tab import SyscallsTab


class MainWindow (QMainWindow, Ui_MainWindow):

    def __init__(self, model):
        super().__init__()
        self.setupUi(self)
        self.__model = model
        self.__initMenu()
        self.__initTabs()
        self.__initProcListView()

    def __initMenu(self):
        self.actionQuit.triggered.connect(self.close)
        self.actionOpen.triggered.connect(self.__menuFileOpen)
        # TODO help about

    def __initProcListView(self):
        self.__model.modelsChanged.connect(self.__refreshProcListView)
        self.processesListView.setModel(self.__model.getProcsModel())
        self.processesListView.selectionModel(). \
            currentChanged.connect(self.__filestatsTab.showSelectedProc)
        self.processesListView.selectionModel(). \
            currentChanged.connect(self.__syscallsTab.showSelectedProc)

    def __initTabs(self):
        self.__filestatsTab = FilestatsTab(self, self.__model)
        self.__syscallsTab = SyscallsTab(self, self.__model)

    def closeEvent(self, event):
        result = QMessageBox.question(
                self, 'Confirm Quit', 'Are you sure you want to quit?',
                QMessageBox.Yes | QMessageBox.No)
        if result == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def __menuFileOpen(self):
        files = QFileDialog.getOpenFileNames(self, "Open iotrace files", "",
                                             "iotrace JSON files (*.json)")
        if files[0]:
            try:
                self.__model.setFiles(files[0])
            except ValueError:
                errorDialog = QErrorMessage(self)
                errorDialog.showMessage(
                        "The selected JSON file is not compatible with "
                        "iotrace-GUI." + os.linesep +
                        "Ensure that filenames were not changed from "
                        "filenames that were assigned by iotrace.")
            except Exception as e:
                errorDialog = QErrorMessage(self)
                errorDialog.showMessage(
                        "Unexpected error occurred" + os.linesep + e.message)

    @Slot()
    def __refreshProcListView(self):
        self.processesListView.selectionModel(). \
            currentChanged.disconnect(self.__filestatsTab.showSelectedProc)
        self.processesListView.selectionModel(). \
            currentChanged.disconnect(self.__syscallsTab.showSelectedProc)

        self.processesListView.setModel(self.__model.getProcsModel())

        self.processesListView.selectionModel(). \
            currentChanged.connect(self.__filestatsTab.showSelectedProc)
        self.processesListView.selectionModel(). \
            currentChanged.connect(self.__syscallsTab.showSelectedProc)
        self.processesListView.setFocus()
