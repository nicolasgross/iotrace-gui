from PySide2.QtCore import Qt, Slot, QRegularExpression


class RwBlocksTab:

    def __init__(self, window, model):
        self.__window = window
        self.__model = model
        self.__model.filesLoaded.connect(self.__refresh)
        self.__window.rwLineEdit.textChanged.connect(
                self.__validateRegex)

    @Slot()
    def __refresh(self):
        for proc in self.__model.getProcs():
            filenamesModel = self.__model.getFilenamesModel(proc)
            self.__window.rwLineEdit.textChanged.connect(
                    filenamesModel.setFilterRegularExpression)

    @Slot()
    def __validateRegex(self, pattern):
        regex = QRegularExpression(pattern)
        if regex.isValid():
            self.__window.rwLineEdit.setStyleSheet(
                    "background-color: white;")
        else:
            self.__window.rwLineEdit.setStyleSheet(
                    "background-color: orange;")

    @Slot()
    def showSelectedProc(self, current, previous):
        selectedProc = self.__model.procsModel.data(current, Qt.ItemDataRole)
        filenamesModel = self.__model.getFilenamesModel(selectedProc)
        self.__window.rwListView.setModel(filenamesModel)
