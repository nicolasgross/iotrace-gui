from PySide2.QtCore import Qt, Slot

from iotracegui.view.shared_func import validateRegex


class FilestatsTab:

    def __init__(self, window, model):
        self.__window = window
        self.__model = model
        self.__currentProc = None
        self.__model.modelsWillChange.connect(self.disconnectSignalsSlot)
        self.__window.filestatsLineEdit.textChanged.connect(
                self.__validateRegex)

    @Slot()
    def __validateRegex(self, pattern):
        validateRegex(pattern, self.__window.filestatsLineEdit)

    @Slot()
    def disconnectSignalsSlot(self):
        self.__disconnectSignals(self.__currentProc)

    def __disconnectSignals(self, previous):
        if previous:
            procsModel = self.__model.getProcsModel()
            prevProc = procsModel.data(previous, Qt.ItemDataRole)
            if prevProc:
                filestatModel = self.__model.getFilestatsModel(prevProc)
                self.__window.filestatsLineEdit.textChanged.disconnect(
                         filestatModel.setFilterRegularExpression)

    @Slot()
    def showSelectedProc(self, current, previous):
        self.__disconnectSignals(previous)

        # connect new filestats model
        procsModel = self.__model.getProcsModel()
        self.__currentProc = current
        selectedProc = procsModel.data(current, Qt.ItemDataRole)
        filestatModel = self.__model.getFilestatsModel(selectedProc)
        self.__window.filestatsLineEdit.textChanged.connect(
                 filestatModel.setFilterRegularExpression)
        regex = self.__window.filestatsLineEdit.text()
        self.__window.filestatsLineEdit.textChanged.emit(regex)

        # show new filestats model
        self.__window.filestatsTableView.setModel(filestatModel)
