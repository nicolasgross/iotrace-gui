from PySide2.QtCore import Qt, Signal, Slot, QObject, QModelIndex

from iotracegui.view.shared_func import validateRegex, CopySelectedCellsAction
from iotracegui.view.blocks_popup import BlocksPopup


class FilestatsTab (QObject):

    checkboxesChanged = Signal(dict)

    def __init__(self, window, model, parent=None):
        QObject.__init__(self, parent)
        self._window = window
        self._model = model
        self._currentProc = None
        self._model.modelsWillChange.connect(self.disconnectSignalsSlot)
        self._window.filestatsLineEdit.textChanged.connect(
                self._validateRegex)
        self._window.filestatsTableView.addAction(
                CopySelectedCellsAction(self._window.filestatsTableView))
        self._window.filestatsTableView.doubleClicked.connect(
                self._openBlocksPopup)
        self._initFilterCheckBoxes()

    def _initFilterCheckBoxes(self):
        self._window.checkBoxBin.stateChanged.connect(
                self._emitCheckBoxState)
        self._window.checkBoxDev.stateChanged.connect(
                self._emitCheckBoxState)
        self._window.checkBoxEtc.stateChanged.connect(
                self._emitCheckBoxState)
        self._window.checkBoxHome.stateChanged.connect(
                self._emitCheckBoxState)
        self._window.checkBoxOpt.stateChanged.connect(
                self._emitCheckBoxState)
        self._window.checkBoxProc.stateChanged.connect(
                self._emitCheckBoxState)
        self._window.checkBoxRun.stateChanged.connect(
                self._emitCheckBoxState)
        self._window.checkBoxSys.stateChanged.connect(
                self._emitCheckBoxState)
        self._window.checkBoxTmp.stateChanged.connect(
                self._emitCheckBoxState)
        self._window.checkBoxUsr.stateChanged.connect(
                self._emitCheckBoxState)
        self._window.checkBoxVar.stateChanged.connect(
                self._emitCheckBoxState)

    @Slot(int)
    def _emitCheckBoxState(self, newVal):
        state = {}
        state['bin'] = self._window.checkBoxBin.isChecked()
        state['dev'] = self._window.checkBoxDev.isChecked()
        state['etc'] = self._window.checkBoxEtc.isChecked()
        state['home'] = self._window.checkBoxHome.isChecked()
        state['opt'] = self._window.checkBoxOpt.isChecked()
        state['proc'] = self._window.checkBoxProc.isChecked()
        state['run'] = self._window.checkBoxRun.isChecked()
        state['sys'] = self._window.checkBoxSys.isChecked()
        state['tmp'] = self._window.checkBoxTmp.isChecked()
        state['usr'] = self._window.checkBoxUsr.isChecked()
        state['var'] = self._window.checkBoxVar.isChecked()
        self.checkboxesChanged.emit(state)

    @Slot(QModelIndex)
    def _openBlocksPopup(self, index):
        if self._currentProc:
            procsModel = self._model.getProcsModel()
            selectedProc = procsModel.data(self._currentProc, Qt.ItemDataRole)
            filestatModel = self._model.getFilestatsModel(selectedProc)
            filename = filestatModel.headerData(index.row(), Qt.Vertical,
                                                Qt.ToolTipRole)
            if filename:
                rwBlocksModel = self._model.getRwBlocksModel(selectedProc,
                                                              filename)
                popup = BlocksPopup(rwBlocksModel, filename)
                popup.show(self._window)

    @Slot()
    def _validateRegex(self, pattern):
        validateRegex(pattern, self._window.filestatsLineEdit)

    @Slot()
    def disconnectSignalsSlot(self):
        self._disconnectSignals(self._currentProc)

    def _disconnectSignals(self, previous):
        if previous:
            procsModel = self._model.getProcsModel()
            prevProc = procsModel.data(previous, Qt.ItemDataRole)
            if prevProc:
                filestatModel = self._model.getFilestatsModel(prevProc)
                self.checkboxesChanged.disconnect(
                        filestatModel.setFilterCheckboxes)
                self._window.filestatsLineEdit.textChanged.disconnect(
                        filestatModel.setFilterRegularExpression)

    @Slot()
    def showSelectedProc(self, current, previous):
        self._disconnectSignals(previous)

        # connect new filestats model
        procsModel = self._model.getProcsModel()
        self._currentProc = current
        selectedProc = procsModel.data(current, Qt.ItemDataRole)
        filestatModel = self._model.getFilestatsModel(selectedProc)
        self.checkboxesChanged.connect(filestatModel.setFilterCheckboxes)
        self._window.filestatsLineEdit.textChanged.connect(
                filestatModel.setFilterRegularExpression)
        regex = self._window.filestatsLineEdit.text()
        self._window.filestatsLineEdit.textChanged.emit(regex)

        # show new filestats model
        self._window.filestatsTableView.setModel(filestatModel)
