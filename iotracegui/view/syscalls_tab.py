from PySide2.QtCore import Qt, Slot

from iotracegui.view.shared_func import validateRegex, CopySelectedCellsAction


class SyscallsTab:

    def __init__(self, window, model):
        self._window = window
        self._model = model
        self._currentProc = None
        self._model.modelsWillChange.connect(self.disconnectSignalsSlot)
        self._window.syscallsLineEdit.textChanged.connect(
                self._validateRegex)
        self._window.syscallsTableView.addAction(
                CopySelectedCellsAction(self._window.syscallsTableView))

    @Slot()
    def _validateRegex(self, pattern):
        validateRegex(pattern, self._window.syscallsLineEdit)

    @Slot()
    def disconnectSignalsSlot(self):
        self._disconnectSignals(self._currentProc)

    def _disconnectSignals(self, previous):
        if previous:
            procsModel = self._model.getProcsModel()
            prevProc = procsModel.data(previous, Qt.ItemDataRole)
            if prevProc:
                syscallsModel = self._model.getSyscallsModel(prevProc)
                self._window.syscallsLineEdit.textChanged.disconnect(
                         syscallsModel.setFilterRegularExpression)

    @Slot()
    def showSelectedProc(self, current, previous):
        self._disconnectSignals(previous)

        # connect new syscalls model
        procsModel = self._model.getProcsModel()
        self._currentProc = current
        selectedProc = procsModel.data(current, Qt.ItemDataRole)
        syscallsModel = self._model.getSyscallsModel(selectedProc)
        self._window.syscallsLineEdit.textChanged.connect(
                 syscallsModel.setFilterRegularExpression)
        regex = self._window.syscallsLineEdit.text()
        self._window.syscallsLineEdit.textChanged.emit(regex)

        # show new syscalls model
        self._window.syscallsTableView.setModel(syscallsModel)
