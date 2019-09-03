from PySide2.QtCore import Qt, Slot


class SyscallsTab:

    def __init__(self, window, model):
        self.__window = window
        self.__model = model

    @Slot()
    def showSelectedProc(self, current, previous):
        selectedProc = self.__model.procsModel.data(current, Qt.ItemDataRole)
        syscallsModel = self.__model.getSyscallsModel(selectedProc)
        self.__window.syscallsTableView.setModel(syscallsModel)
