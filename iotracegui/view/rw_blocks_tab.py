from PySide2.QtCore import Qt, Slot

from iotracegui.view.shared_tab_func import validateRegex


class RwBlocksTab:

    def __init__(self, window, model):
        self.__window = window
        self.__model = model
        self.__currentSelection = None
        self.__model.modelsWillChange.connect(self.disconnectSignals)
        self.__window.rwLineEdit.textChanged.connect(
                self.__validateRegex)

    @Slot()
    def __validateRegex(self, pattern):
        validateRegex(pattern, self.__window.rwLineEdit)

    @Slot()
    def disconnectSignals(self):
        if self.__currentSelection:
            procsModel = self.__model.getProcsModel()
            selectedProc = procsModel.data(self.__currentSelection,
                                           Qt.ItemDataRole)
            filenamesModel = self.__model.getFilenamesModel(selectedProc)
            self.__window.rwLineEdit.textChanged.disconnect(
                     filenamesModel.setFilterRegularExpression)

    @Slot()
    def showSelectedProc(self, current, previous):
        procsModel = self.__model.getProcsModel()

        # disconnect previous filenames model
        prevProc = procsModel.data(previous, Qt.ItemDataRole)
        if prevProc:
            prevFilenamesModel = self.__model.getFilenamesModel(prevProc)
            self.__window.rwLineEdit.textChanged.disconnect(
                     prevFilenamesModel.setFilterRegularExpression)

        # connect new filenames model
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
