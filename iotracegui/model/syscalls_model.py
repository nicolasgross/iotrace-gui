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


from PySide2.QtCore import Qt, QAbstractTableModel, QModelIndex


class SyscallsModel (QAbstractTableModel):

    columnNames = [
            'Count (#)', 'Total (ms)', 'Average (ms)'
        ]

    columnTooltips = [
            'Count of all calls',
            'Total time spent in all calls'
            'Average time spent in a single call'
        ]

    def __init__(self, syscalls, parent=None):
        super().__init__(parent)
        self._syscalls = syscalls

    def getSyscalls(self):
        return self._syscalls

    def rowCount(self, parent=QModelIndex()):
        return len(self._syscalls)

    def columnCount(self, parent=QModelIndex()):
        return 3

    def data(self, index, role):
        if (not index.isValid() or index.column() >= self.columnCount() or
                index.row() >= self.rowCount()):
            return None
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignRight
        elif role == Qt.DisplayRole:
            scStat = self._syscalls[index.row()]
            if index.column() == 0:
                return scStat['count']
            elif index.column() == 1:
                return scStat['total ns'] / 1000000.0
            else:
                if scStat['count'] == 0:
                    return 0
                else:
                    return (scStat['total ns'] / 1000000.0) / scStat['count']
        else:
            return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.columnNames[section]
            else:
                return self._syscalls[section]["syscall"]
        elif role == Qt.ToolTipRole:
            if orientation == Qt.Horizontal:
                return self.columnTooltips[section]
            else:
                return None
        else:
            return None
