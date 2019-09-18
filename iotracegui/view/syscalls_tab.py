from PySide2.QtCore import Qt, Slot, QItemSelection

from iotracegui.view.shared_func import validateRegex, CopySelectedCellsAction


class SyscallsTab:

    def __init__(self, window, model):
        self._window = window
        self._model = model
        self._model.modelsWillChange.connect(self.disconnectSignals)
        self._window.syscallsLineEdit.textChanged.connect(
                self._validateRegex)
        self._window.syscallsTableView.addAction(
                CopySelectedCellsAction(self._window.syscallsTableView))

    @Slot(str)
    def _validateRegex(self, pattern):
        validateRegex(pattern, self._window.syscallsLineEdit)

    @Slot()
    def disconnectSignals(self):
        syscallsModel = self._window.syscallsTableView.model()
        if syscallsModel:
            self._window.syscallsLineEdit.textChanged.disconnect(
                     syscallsModel.setFilterRegularExpression)

    @Slot(QItemSelection, QItemSelection)
    def showSelectedProc(self, selected, deselected):
        self.disconnectSignals()

        selectedProcs = self._window.processesListView.selectedIndexes()
        if len(selectedProcs) != 1:
            self._window.syscallsTableView.setModel(None)
            return

        # connect new syscalls model
        procsModel = self._model.getProcsModel()
        selectedProc = procsModel.data(selectedProcs[0], Qt.ItemDataRole)
        syscallsModel = self._model.getSyscallsModel(selectedProc)
        self._window.syscallsLineEdit.textChanged.connect(
                 syscallsModel.setFilterRegularExpression)
        regex = self._window.syscallsLineEdit.text()
        self._window.syscallsLineEdit.textChanged.emit(regex)

        # show new syscalls model
        self._window.syscallsTableView.setModel(syscallsModel)
