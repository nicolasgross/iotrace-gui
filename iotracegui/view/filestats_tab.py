# Copyright (C) 2019 HLRS, University of Stuttgart
# <https://www.hlrs.de/>, <https://www.uni-stuttgart.de/>
#
# This file is part of iotrace-GUI.
#
# iotrace-GUI is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# iotrace-GUI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with iotrace-GUI.  If not, see <https://www.gnu.org/licenses/>.
#
# The following people contributed to the project (in alphabetic order
# by surname):
#
# - Nicolas Gross <https://github.com/nicolasgross>


from PySide2.QtCore import Qt, Signal, Slot, QObject, QModelIndex, \
    QItemSelection

from iotracegui.view.shared_func import validateRegex, CopySelectedCellsAction
from iotracegui.view.blocks_dialog import BlocksDialog


class FilestatsTab (QObject):

    checkboxesChanged = Signal(dict)

    def __init__(self, window, model, parent=None):
        super().__init__(parent)
        self._window = window
        self._model = model
        self._window.filestatsLineEdit.textChanged.connect(
                self._validateRegex)
        self._window.filestatsTableView.addAction(
                CopySelectedCellsAction(self._window.filestatsTableView))
        self._window.filestatsTableView.doubleClicked.connect(
                self._openBlocksDialog)
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
    def _openBlocksDialog(self, index):
        selectedProcs = self._window.processesTreeView.selectedIndexes()
        if len(selectedProcs) == 1:
            procsModel = self._model.getProcsModel()
            selectedProc = procsModel.data(selectedProcs[0], Qt.ItemDataRole)
            filestatModel = self._model.getFilestatsModel(selectedProc.proc)
            filename = filestatModel.headerData(index.row(), Qt.Vertical,
                                                Qt.ToolTipRole)
            if filename:
                rwBlocksModel = self._model.getRwBlocksModel(selectedProc,
                                                             filename)
                dialog = BlocksDialog(rwBlocksModel, filename, self._window)
                dialog.show()

    @Slot(str)
    def _validateRegex(self, pattern):
        validateRegex(pattern, self._window.filestatsLineEdit)

    def disconnectSignals(self):
        filestatModel = self._window.filestatsTableView.model()
        if filestatModel:
            self.checkboxesChanged.disconnect(
                    filestatModel.setFilterCheckboxes)
            self._window.filestatsLineEdit.textChanged.disconnect(
                    filestatModel.setFilterRegularExpression)

    @Slot(QItemSelection, QItemSelection)
    def showSelectedProc(self, selected, deselected):
        self.disconnectSignals()

        selectedProcs = self._window.processesTreeView.selectedIndexes()
        if len(selectedProcs) != 1:
            self._window.filestatsTableView.setModel(None)
            return

        # connect new filestats model
        procsModel = self._model.getProcsModel()
        selectedProc = procsModel.data(selectedProcs[0], Qt.ItemDataRole)
        filestatModel = self._model.getFilestatsModel(selectedProc.proc)
        self.checkboxesChanged.connect(filestatModel.setFilterCheckboxes)
        self._window.filestatsLineEdit.textChanged.connect(
                filestatModel.setFilterRegularExpression)
        regex = self._window.filestatsLineEdit.text()
        self._window.filestatsLineEdit.textChanged.emit(regex)
        self._emitCheckBoxState(0)

        # show new filestats model
        self._window.filestatsTableView.setModel(filestatModel)
