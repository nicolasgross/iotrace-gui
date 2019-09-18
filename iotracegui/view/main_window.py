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
        self._model = model
        self._initMenu()
        self._initTabs()
        self._initProcListView()

    def _initMenu(self):
        self.actionQuit.triggered.connect(self.close)
        self.actionOpen.triggered.connect(self._menuFileOpen)
        # TODO help about

    def _initProcListView(self):
        self._model.modelsChanged.connect(self._refreshProcListView)
        self.processesListView.setModel(self._model.getProcsModel())
        self.processesListView.selectionModel(). \
            currentChanged.connect(self._filestatsTab.showSelectedProc)
        self.processesListView.selectionModel(). \
            currentChanged.connect(self._syscallsTab.showSelectedProc)

    def _initTabs(self):
        self._filestatsTab = FilestatsTab(self, self._model)
        self._syscallsTab = SyscallsTab(self, self._model)

    def closeEvent(self, event):
        result = QMessageBox.question(
                self, 'Confirm Quit', 'Are you sure you want to quit?',
                QMessageBox.Yes | QMessageBox.No)
        if result == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def _menuFileOpen(self):
        files = QFileDialog.getOpenFileNames(self, "Open iotrace files", "",
                                             "iotrace JSON files (*.json)")
        if files[0]:
            try:
                self._model.setFiles(files[0])
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
                        "Unexpected error occurred" + os.linesep + str(e))

    @Slot()
    def _refreshProcListView(self):
        self.processesListView.selectionModel().currentChanged.disconnect(
                self._filestatsTab.showSelectedProc)
        self.processesListView.selectionModel().currentChanged.disconnect(
                self._syscallsTab.showSelectedProc)

        self.processesListView.setModel(self._model.getProcsModel())

        self.processesListView.selectionModel().currentChanged.connect(
                self._filestatsTab.showSelectedProc)
        self.processesListView.selectionModel().currentChanged.connect(
                self._syscallsTab.showSelectedProc)
        self.processesListView.setFocus()
