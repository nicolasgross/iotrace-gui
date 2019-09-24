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


class RwBlocksModel (QAbstractTableModel):

    columnNames = [
            'R Block (byte)', 'R Count (#)', 'W Block (byte)', 'W Count (#)'
        ]

    columnTooltips = [
            'Read block size',
            'Count of the respective read block size',
            'Write block size',
            'Count of the respective write block size'
        ]

    def __init__(self, filestats, parent=None):
        super().__init__(parent)
        self._filestats = filestats

    def rowCount(self, parent=QModelIndex()):
        return max(len(self._filestats['read-blocks']),
                   len(self._filestats['write-blocks']))

    def columnCount(self, parent=QModelIndex()):
        return 4

    def data(self, index, role):
        if (not index.isValid() or index.column() >= self.columnCount() or
                index.row() >= self.rowCount()):
            return None
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignRight
        elif role == Qt.DisplayRole:
            if index.column() < 2:
                blocks = self._filestats['read-blocks']
                if index.row() < len(blocks):
                    return blocks[index.row()][index.column()]
                else:
                    return None
            elif index.column() > 1 and index.column() < 4:
                blocks = self._filestats['write-blocks']
                if index.row() < len(blocks):
                    return blocks[index.row()][index.column() % 2]
                else:
                    return None
        else:
            return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.columnNames[section]
            else:
                return None
        elif role == Qt.ToolTipRole:
            if orientation == Qt.Horizontal:
                return self.columnTooltips[section]
            else:
                return None
        else:
            return None
