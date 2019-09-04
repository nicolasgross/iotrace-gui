from PySide2.QtCore import Qt, Slot

from iotracegui.view.shared_tab_func import validateRegex


class FilestatsTab:

    def __init__(self, window, model):
        self.__window = window
        self.__model = model
        self.__currentSelection = None
        self.__model.modelsWillChange.connect(self.disconnectSignals)
        self.__window.filestatsLineEdit.textChanged.connect(
                self.__validateRegex)

    @Slot()
    def __validateRegex(self, pattern):
        validateRegex(pattern, self.__window.filestatsLineEdit)

    @Slot()
    def disconnectSignals(self):
        if self.__currentSelection:
            procsModel = self.__model.getProcsModel()
            selectedProc = procsModel.data(self.__currentSelection,
                                           Qt.ItemDataRole)
            filestatModel = self.__model.getFilestatsModel(selectedProc)
            self.__window.filestatsLineEdit.textChanged.disconnect(
                     filestatModel.setFilterRegularExpression)

    @Slot()
    def showSelectedProc(self, current, previous):
        procsModel = self.__model.getProcsModel()

        # disconnect previous filestats model
        prevProc = procsModel.data(previous, Qt.ItemDataRole)
        if prevProc:
            prevFilestatModel = self.__model.getFilestatsModel(prevProc)
            self.__window.filestatsLineEdit.textChanged.disconnect(
                     prevFilestatModel.setFilterRegularExpression)

        # connect new filestats model
        self.__currentSelection = current
        selectedProc = procsModel.data(current, Qt.ItemDataRole)
        filestatModel = self.__model.getFilestatsModel(selectedProc)
        self.__window.filestatsLineEdit.textChanged.connect(
                 filestatModel.setFilterRegularExpression)
        regex = self.__window.filestatsLineEdit.text()
        self.__window.filestatsLineEdit.textChanged.emit(regex)

        # show new filestats model
        self.__window.filestatsTableView.setModel(filestatModel)
