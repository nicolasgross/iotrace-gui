from PySide2.QtCore import Qt, Slot

from iotracegui.view.shared_func import validateRegex


class RwBlocksTab:

    def __init__(self, window, model):
        self.__window = window
        self.__model = model
        self.__currentSelection = None
        self.__model.modelsWillChange.connect(self.disconnectSignalsSlot)
        self.__window.rwLineEdit.textChanged.connect(
                self.__validateRegex)

    @Slot()
    def __validateRegex(self, pattern):
        validateRegex(pattern, self.__window.rwLineEdit)

    @Slot()
    def disconnectSignalsSlot(self):
        self.__disconnectSignals(self.__currentSelection)

    def __disconnectSignals(self, previous):
        if previous:
            procsModel = self.__model.getProcsModel()
            prevProc = procsModel.data(previous, Qt.ItemDataRole)
            if prevProc:
                filenamesModel = self.__model.getFilenamesModel(prevProc)
                self.__window.rwLineEdit.textChanged.disconnect(
                         filenamesModel.setFilterRegularExpression)

    @Slot()
    def showSelectedProc(self, current, previous):
        self.__disconnectSignals(previous)

        # connect new filenames model
        procsModel = self.__model.getProcsModel()
        self.__currentSelection = current
        selectedProc = procsModel.data(current, Qt.ItemDataRole)
        filenamesModel = self.__model.getFilenamesModel(selectedProc)
        self.__window.rwLineEdit.textChanged.connect(
                 filenamesModel.setFilterRegularExpression)
        regex = self.__window.rwLineEdit.text()
        self.__window.rwLineEdit.textChanged.emit(regex)

        # show new filenames model
        self.__window.rwListView.setModel(filenamesModel)

    # @Slot()
    # def showSelectedFile(self, current, previous):
    #     selectedFile = self.__model.
