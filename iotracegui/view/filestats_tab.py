from PySide2.QtCore import Qt, Signal, Slot, QObject, QModelIndex

from iotracegui.view.shared_func import validateRegex, CopySelectedCellsAction
from iotracegui.view.blocks_popup import BlocksPopup


class FilestatsTab (QObject):

    checkboxesChanged = Signal(dict)

    def __init__(self, window, model, parent=None):
        QObject.__init__(self, parent)
        self.__window = window
        self.__model = model
        self.__currentProc = None
        self.__model.modelsWillChange.connect(self.disconnectSignalsSlot)
        self.__window.filestatsLineEdit.textChanged.connect(
                self.__validateRegex)
        self.__window.filestatsTableView.addAction(
                CopySelectedCellsAction(self.__window.filestatsTableView))
        self.__window.filestatsTableView.doubleClicked.connect(
                self.__openBlocksPopup)
        self.__initFilterCheckBoxes()

    def __initFilterCheckBoxes(self):
        self.__window.checkBoxBin.stateChanged.connect(
                self.__emitCheckBoxState)
        self.__window.checkBoxDev.stateChanged.connect(
                self.__emitCheckBoxState)
        self.__window.checkBoxEtc.stateChanged.connect(
                self.__emitCheckBoxState)
        self.__window.checkBoxHome.stateChanged.connect(
                self.__emitCheckBoxState)
        self.__window.checkBoxOpt.stateChanged.connect(
                self.__emitCheckBoxState)
        self.__window.checkBoxProc.stateChanged.connect(
                self.__emitCheckBoxState)
        self.__window.checkBoxRun.stateChanged.connect(
                self.__emitCheckBoxState)
        self.__window.checkBoxSys.stateChanged.connect(
                self.__emitCheckBoxState)
        self.__window.checkBoxTmp.stateChanged.connect(
                self.__emitCheckBoxState)
        self.__window.checkBoxUsr.stateChanged.connect(
                self.__emitCheckBoxState)
        self.__window.checkBoxVar.stateChanged.connect(
                self.__emitCheckBoxState)

    @Slot(int)
    def __emitCheckBoxState(self, newVal):
        state = {}
        state['bin'] = self.__window.checkBoxBin.isChecked()
        state['dev'] = self.__window.checkBoxDev.isChecked()
        state['etc'] = self.__window.checkBoxEtc.isChecked()
        state['home'] = self.__window.checkBoxHome.isChecked()
        state['opt'] = self.__window.checkBoxOpt.isChecked()
        state['proc'] = self.__window.checkBoxProc.isChecked()
        state['run'] = self.__window.checkBoxRun.isChecked()
        state['sys'] = self.__window.checkBoxSys.isChecked()
        state['tmp'] = self.__window.checkBoxTmp.isChecked()
        state['usr'] = self.__window.checkBoxUsr.isChecked()
        state['var'] = self.__window.checkBoxVar.isChecked()
        self.checkboxesChanged.emit(state)

    @Slot(QModelIndex)
    def __openBlocksPopup(self, index):
        if self.__currentProc:
            procsModel = self.__model.getProcsModel()
            selectedProc = procsModel.data(self.__currentProc, Qt.ItemDataRole)
            filestatModel = self.__model.getFilestatsModel(selectedProc)
            filename = filestatModel.headerData(index.row(), Qt.Vertical,
                                                Qt.ToolTipRole)
            if filename:
                rwBlocksModel = self.__model.getRwBlocksModel(selectedProc,
                                                              filename)
                popup = BlocksPopup(rwBlocksModel, filename)
                popup.show(self.__window)

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
                self.checkboxesChanged.disconnect(
                        filestatModel.setFilterCheckboxes)
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
        self.checkboxesChanged.connect(filestatModel.setFilterCheckboxes)
        self.__window.filestatsLineEdit.textChanged.connect(
                filestatModel.setFilterRegularExpression)
        regex = self.__window.filestatsLineEdit.text()
        self.__window.filestatsLineEdit.textChanged.emit(regex)

        # show new filestats model
        self.__window.filestatsTableView.setModel(filestatModel)
