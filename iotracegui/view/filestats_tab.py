from PySide2.QtCore import Qt, Slot, QRegularExpression


class FilestatsTab:

    def __init__(self, window, model):
        self.__window = window
        self.__model = model
        self.__model.filesLoaded.connect(self.__refresh)
        self.__window.filestatsLineEdit.textChanged.connect(
                self.__validateRegex)

    @Slot()
    def __refresh(self):
        for proc in self.__model.getProcs():
            filestatModel = self.__model.getFilestatsModel(proc)
            self.__window.filestatsLineEdit.textChanged.connect(
                    filestatModel.setFilterRegularExpression)

    @Slot()
    def __validateRegex(self, pattern):
        regex = QRegularExpression(pattern)
        if regex.isValid():
            self.__window.filestatsLineEdit.setStyleSheet(
                    "background-color: white;")
        else:
            self.__window.filestatsLineEdit.setStyleSheet(
                    "background-color: orange;")

    @Slot()
    def showSelectedProc(self, current, previous):
        selectedProc = self.__model.procsModel.data(current, Qt.ItemDataRole)
        filestatModel = self.__model.getFilestatsModel(selectedProc)
        self.__window.filestatsTableView.setModel(filestatModel)
