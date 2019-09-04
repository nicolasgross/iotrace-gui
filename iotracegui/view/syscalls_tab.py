from PySide2.QtCore import Qt, Slot

from iotracegui.view.shared_tab_func import validateRegex


class SyscallsTab:

    def __init__(self, window, model):
        self.__window = window
        self.__model = model
        self.__currentSelection = None
        self.__model.modelsWillChange.connect(self.disconnectSignals)
        self.__window.syscallsLineEdit.textChanged.connect(
                self.__validateRegex)

    @Slot()
    def __validateRegex(self, pattern):
        validateRegex(pattern, self.__window.syscallsLineEdit)

    @Slot()
    def disconnectSignals(self):
        if self.__currentSelection:
            procsModel = self.__model.getProcsModel()
            selectedProc = procsModel.data(self.__currentSelection,
                                           Qt.ItemDataRole)
            syscallsModel = self.__model.getSyscallsModel(selectedProc)
            self.__window.syscallsLineEdit.textChanged.disconnect(
                     syscallsModel.setFilterRegularExpression)

    @Slot()
    def showSelectedProc(self, current, previous):
        procsModel = self.__model.getProcsModel()

        # disconnect previous syscalls model
        prevProc = procsModel.data(previous, Qt.ItemDataRole)
        if prevProc:
            prevSyscallsModel = self.__model.getSyscallsModel(prevProc)
            self.__window.syscallsLineEdit.textChanged.disconnect(
                     prevSyscallsModel.setFilterRegularExpression)

        # connect new syscalls model
        self.__currentSelection = current
        selectedProc = procsModel.data(current, Qt.ItemDataRole)
        syscallsModel = self.__model.getSyscallsModel(selectedProc)
        self.__window.syscallsLineEdit.textChanged.connect(
                 syscallsModel.setFilterRegularExpression)
        regex = self.__window.syscallsLineEdit.text()
        self.__window.syscallsLineEdit.textChanged.emit(regex)

        # show new syscalls model
        self.__window.syscallsTableView.setModel(syscallsModel)
