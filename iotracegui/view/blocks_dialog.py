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


from PySide2.QtCore import Qt, QSortFilterProxyModel
from PySide2.QtWidgets import QDialog

from iotracegui.view.ui_blocks_dialog import Ui_BlocksDialog
from iotracegui.view.shared_func import CopySelectedCellsAction


class BlocksDialog (QDialog, Ui_BlocksDialog):

    def __init__(self, blocksModel, filename, parent):
        super().__init__()
        self.setupUi(self)
        self._blocksModel = blocksModel
        if len(filename) > 33:
            windowTitle = filename[:15] + ' ... ' + filename[-15:]
        else:
            windowTitle = filename
        self.setWindowTitle(windowTitle)
        sortModel = QSortFilterProxyModel()
        sortModel.setSourceModel(blocksModel)
        self.blocksTableView.setModel(sortModel)
        self.blocksTableView.resizeColumnsToContents()
        self.blocksTableView.addAction(CopySelectedCellsAction(
                self.blocksTableView))
        self.setParent(parent)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
