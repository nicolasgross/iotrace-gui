from PySide2.QtCore import Qt, Slot, QRegularExpression


class FilestatsTab:
    def __init__(self, window, model):
        self.__window = window
        self.__model = model
        self.__model.filesLoaded.connect(self.__refreshData)
        self.__window.filestatsLineEdit.textChanged.connect(self.__checkRegex)
        self.__refreshData()

    @Slot()
    def __refreshData(self):
        self.__window.processesListView.setModel(self.__model.procsModel)
        self.__window.processesListView.selectionModel(). \
            currentChanged.connect(self.__showSelectedProc)
        for proc in self.__model.getProcs():
            filestatModel = self.__model.getFilestatModel(proc)
            self.__window.filestatsLineEdit.textChanged.connect(
                    filestatModel.setFilterRegularExpression)

    @Slot()
    def __showSelectedProc(self, current, previous):
        selectedProc = self.__model.procsModel.data(current, Qt.ItemDataRole)
        filestatModel = self.__model.getFilestatModel(selectedProc)
        self.__window.filestatsTableView.setModel(filestatModel)

    @Slot()
    def __checkRegex(self, pattern):
        regex = QRegularExpression(pattern)
        if regex.isValid():
            self.__window.filestatsLineEdit.setStyleSheet(
                    "background-color: white;")
        else:
            self.__window.filestatsLineEdit.setStyleSheet(
                    "background-color: orange;")
