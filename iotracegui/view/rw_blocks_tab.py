from PySide2.QtCore import Qt, Slot

from iotracegui.view.shared_func import validateRegex, CopySelectedCellsAction


class RwBlocksTab:

    def __init__(self, window, model):
        self.__window = window
        self.__model = model
        self.__currentProc = None
        self.__model.modelsWillChange.connect(self.disconnectSignalsSlot)
        self.__window.rwLineEdit.textChanged.connect(
                self.__validateRegex)
        self.__window.rwTableView.addAction(
                CopySelectedCellsAction(self.__window.rwTableView))

    @Slot()
    def __validateRegex(self, pattern):
        validateRegex(pattern, self.__window.rwLineEdit)

    @Slot()
    def disconnectSignalsSlot(self):
        self.__disconnectSignals(self.__currentProc)

    def __disconnectSignals(self, previous):
        if previous:
            procsModel = self.__model.getProcsModel()
            prevProc = procsModel.data(previous, Qt.ItemDataRole)
            if prevProc:
                filenamesModel = self.__model.getFilenamesModel(prevProc)
                self.__window.rwLineEdit.textChanged.disconnect(
                        filenamesModel.setFilterRegularExpression)
                self.__window.rwListView.selectionModel().currentChanged. \
                    disconnect(self.showSelectedFile)

    @Slot()
    def showSelectedProc(self, current, previous):
        self.__disconnectSignals(previous)

        # connect new filenames model
        procsModel = self.__model.getProcsModel()
        self.__currentProc = current
        selectedProc = procsModel.data(current, Qt.ItemDataRole)
        filenamesModel = self.__model.getFilenamesModel(selectedProc)
        self.__window.rwLineEdit.textChanged.connect(
                 filenamesModel.setFilterRegularExpression)
        regex = self.__window.rwLineEdit.text()
        self.__window.rwLineEdit.textChanged.emit(regex)

        # show new filenames model
        self.__window.rwListView.setModel(filenamesModel)
        self.__window.rwListView.selectionModel().currentChanged.connect(
                self.showSelectedFile)

    @Slot()
    def showSelectedFile(self, current, previous):
        procsModel = self.__model.getProcsModel()
        selectedProc = procsModel.data(self.__currentProc, Qt.ItemDataRole)
        filenamesModel = self.__model.getFilenamesModel(selectedProc)
        selectedFile = filenamesModel.data(current, Qt.ItemDataRole)
        if selectedProc and selectedFile:
            rwBlocksModel = self.__model.getRwBlocksModel(selectedProc,
                                                          selectedFile)
            self.__window.rwTableView.setModel(rwBlocksModel)
        else:
            self.__window.rwTableView.setModel(None)
