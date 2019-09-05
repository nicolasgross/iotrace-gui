from PySide2.QtCore import Qt, Slot

from iotracegui.view.shared_func import validateRegex, CopySelectedCellsAction


class SyscallsTab:

    def __init__(self, window, model):
        self.__window = window
        self.__model = model
        self.__currentProc = None
        self.__model.modelsWillChange.connect(self.disconnectSignalsSlot)
        self.__window.syscallsLineEdit.textChanged.connect(
                self.__validateRegex)
        self.__window.syscallsTableView.addAction(
                CopySelectedCellsAction(self.__window.syscallsTableView))

    @Slot()
    def __validateRegex(self, pattern):
        validateRegex(pattern, self.__window.syscallsLineEdit)

    @Slot()
    def disconnectSignalsSlot(self):
        self.__disconnectSignals(self.__currentProc)

    def __disconnectSignals(self, previous):
        if previous:
            procsModel = self.__model.getProcsModel()
            prevProc = procsModel.data(previous, Qt.ItemDataRole)
            if prevProc:
                syscallsModel = self.__model.getSyscallsModel(prevProc)
                self.__window.syscallsLineEdit.textChanged.disconnect(
                         syscallsModel.setFilterRegularExpression)

    @Slot()
    def showSelectedProc(self, current, previous):
        self.__disconnectSignals(previous)

        # connect new syscalls model
        procsModel = self.__model.getProcsModel()
        self.__currentProc = current
        selectedProc = procsModel.data(current, Qt.ItemDataRole)
        syscallsModel = self.__model.getSyscallsModel(selectedProc)
        self.__window.syscallsLineEdit.textChanged.connect(
                 syscallsModel.setFilterRegularExpression)
        regex = self.__window.syscallsLineEdit.text()
        self.__window.syscallsLineEdit.textChanged.emit(regex)

        # show new syscalls model
        self.__window.syscallsTableView.setModel(syscallsModel)
