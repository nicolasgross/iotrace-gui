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


from PySide2.QtCore import Qt, QRegularExpression
from PySide2.QtWidgets import QAction, QTableView, QApplication
from PySide2.QtGui import QKeySequence


def validateRegex(pattern, lineEdit):
    regex = QRegularExpression(pattern)
    if regex.isValid():
        lineEdit.setStyleSheet("background-color: white;")
    else:
        lineEdit.setStyleSheet("background-color: red;")


# https://stackoverflow.com/questions/21675330/copy-paste-in-qtableview/21679553#21679553
class CopySelectedCellsAction (QAction):

    def __init__(self, tableView):
        if not isinstance(tableView, QTableView):
            raise ValueError("CopySelectedCellsAction must be initialized " +
                             "with a QTableView.")
        super(CopySelectedCellsAction, self).__init__("Copy", tableView)
        self.setShortcuts(QKeySequence.keyBindings(QKeySequence.Copy))
        self.triggered.connect(self.copyCellsToClipboard)
        self._tableView = tableView

    def copyCellsToClipboard(self):
        selection = self._tableView.selectionModel().selectedIndexes()
        if len(selection) != 1:
            return
        content = self._tableView.model().data(selection[0], Qt.DisplayRole)
        QApplication.clipboard().setText(str(content))
