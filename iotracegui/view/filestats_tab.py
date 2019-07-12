from PySide2.QtCore import Qt, Slot


class FilestatsTab:
    def __init__(self, window, model):
        self.__window = window
        self.__model = model
        self.__model.filesLoaded.connect(self.__refreshData)
        self.__refreshData()

    @Slot()
    def __refreshData(self):
        self.__window.processesListView.setModel(self.__model.procsModel)
        self.__window.processesListView.selectionModel(). \
            currentChanged.connect(self.__showSelectedProc)

    @Slot()
    def __showSelectedProc(self, current, previous):
        selectedProc = self.__model.procsModel.data(current, Qt.ItemDataRole)
        filestatModel = self.__model.getFilestatModel(selectedProc)
        self.__window.filestatsTableView.setModel(filestatModel)
