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


from PySide2.QtCore import Qt, Slot, QItemSelection

from iotracegui.view.shared_func import validateRegex, CopySelectedCellsAction


class SyscallsTab:

    def __init__(self, window, model):
        self._window = window
        self._model = model
        self._window.syscallsLineEdit.textChanged.connect(
                self._validateRegex)
        self._window.syscallsTableView.addAction(
                CopySelectedCellsAction(self._window.syscallsTableView))

    @Slot(str)
    def _validateRegex(self, pattern):
        validateRegex(pattern, self._window.syscallsLineEdit)

    def disconnectSignals(self):
        syscallsModel = self._window.syscallsTableView.model()
        if syscallsModel:
            self._window.syscallsLineEdit.textChanged.disconnect(
                     syscallsModel.setFilterRegularExpression)

    @Slot(QItemSelection, QItemSelection)
    def showSelectedProc(self, selected, deselected):
        self.disconnectSignals()

        selectedProcs = self._window.processesTreeView.selectedIndexes()
        if len(selectedProcs) != 1:
            self._window.syscallsTableView.setModel(None)
            return

        # connect new syscalls model
        procsModel = self._model.getProcsModel()
        selectedProc = procsModel.data(selectedProcs[0], Qt.ItemDataRole)
        syscallsModel = self._model.getSyscallsModel(selectedProc.proc)
        self._window.syscallsLineEdit.textChanged.connect(
                 syscallsModel.setFilterRegularExpression)
        regex = self._window.syscallsLineEdit.text()
        self._window.syscallsLineEdit.textChanged.emit(regex)

        # show new syscalls model
        self._window.syscallsTableView.setModel(syscallsModel)
