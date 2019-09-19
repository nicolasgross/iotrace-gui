import os
from PySide2.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QAction
from PySide2.QtCore import Slot, QItemSelection, Qt

from iotracegui.view.ui_main_window import Ui_MainWindow
from iotracegui.view.filestats_tab import FilestatsTab
from iotracegui.view.syscalls_tab import SyscallsTab
from iotracegui.model.model import AlreadyOpenError


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
        self._removeAction = QAction("Remove", self)
        self._removeAction.setEnabled(False)
        self._removeAction.triggered.connect(self._removeProcs)
        self._mergeAction = QAction("Merge", self)
        self._mergeAction.setEnabled(False)
        self._mergeAction.triggered.connect(self._mergeProcs)
        self.processesListView.addAction(self._removeAction)
        self.processesListView.addAction(self._mergeAction)
        self.processesListView.setModel(self._model.getProcsModel())
        self.processesListView.selectionModel().selectionChanged. \
            connect(self._filestatsTab.showSelectedProc)
        self.processesListView.selectionModel().selectionChanged. \
            connect(self._syscallsTab.showSelectedProc)
        self.processesListView.selectionModel().selectionChanged. \
            connect(self._updateContextMenuState)

    @Slot()
    def _removeProcs(self):
        selectedIndexes = self.processesListView.selectedIndexes()
        selectedProcs = []
        for index in selectedIndexes:
            selectedProcs.append(self._model.getProcsModel().data(
                index, Qt.ItemDataRole))
        self.processesListView.clearSelection()
        selectedIndexes.sort(reverse=True)
        for index in selectedIndexes:
            self._model.getProcsModel().removeRow(index.row())
        for proc in selectedProcs:
            self._model.removeProc(proc)

    @Slot()
    def _mergeProcs(self):
        # TODO
        pass

    @Slot(QItemSelection, QItemSelection)
    def _updateContextMenuState(self, selected, deselected):
        hasSelection = self.processesListView.selectionModel().hasSelection()
        self._removeAction.setEnabled(hasSelection)
        selectedIndexes = self.processesListView.selectedIndexes()
        self._mergeAction.setEnabled(len(selectedIndexes) > 1)

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
                self._model.openFiles(files[0])
            except (KeyError, ValueError, TypeError) as e:
                QMessageBox.warning(
                        self, "Warning", "The selected JSON file is not "
                        "compatible with iotrace-GUI:" + os.linesep +
                        os.linesep + str(e))
            except AlreadyOpenError as e:
                QMessageBox.warning(
                        self, "Warning", "Some files are already loaded:" +
                        os.linesep + os.linesep + str(e))
