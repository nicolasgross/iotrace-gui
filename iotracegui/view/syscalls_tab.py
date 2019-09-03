from PySide2.QtCore import Qt, Slot, QRegularExpression


class SyscallsTab:

    def __init__(self, window, model):
        self.__window = window
        self.__model = model
        self.__model.filesLoaded.connect(self.__refresh)
        self.__window.syscallsLineEdit.textChanged.connect(
                self.__validateRegex)

    @Slot()
    def __refresh(self):
        for proc in self.__model.getProcs():
            syscallsModel = self.__model.getSyscallsModel(proc)
            self.__window.syscallsLineEdit.textChanged.connect(
                    syscallsModel.setFilterRegularExpression)

    @Slot()
    def __validateRegex(self, pattern):
        regex = QRegularExpression(pattern)
        if regex.isValid():
            self.__window.syscallsLineEdit.setStyleSheet(
                    "background-color: white;")
        else:
            self.__window.syscallsLineEdit.setStyleSheet(
                    "background-color: orange;")

    @Slot()
    def showSelectedProc(self, current, previous):
        selectedProc = self.__model.procsModel.data(current, Qt.ItemDataRole)
        syscallsModel = self.__model.getSyscallsModel(selectedProc)
        self.__window.syscallsTableView.setModel(syscallsModel)
