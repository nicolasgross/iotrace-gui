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


from PySide2.QtCore import Qt, QAbstractItemModel, QModelIndex


class ProcItem:
    def __init__(self, proc, parent, children):
        self.proc = proc                # (trace_id, hostname, rank)
        self.parent = parent            # ProcItem or None
        self.children = children        # [ProcItem] or []


class ProcessesModel (QAbstractItemModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._procs = []

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return len(parent.internalPointer().children)
        else:
            return len(self._procs)

    def columnCount(self, parent=QModelIndex()):
        return 1

    def parent(self, child):
        if child.isValid():
            parent = child.internalPointer().parent
            if parent:
                row = self._procs.index(parent)
                return self.createIndex(row, 0, parent)
        return QModelIndex()

    def index(self, row, column, parent=QModelIndex()):
        if row >= self.rowCount(parent) or column >= self.columnCount(parent):
            return QModelIndex()

        if parent.isValid():
            procItem = parent.internalPointer().children[row]
        else:
            procItem = self._procs[row]
        return self.createIndex(row, column, procItem)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        elif role == Qt.DisplayRole or role == Qt.ToolTipRole:
            proc = index.internalPointer().proc
            return f"{proc[0]} - {proc[1]} - rank {proc[2]}"
        elif role == Qt.ItemDataRole:
            return index.internalPointer()
        else:
            return None

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            if section == 0:
                return "Processes"
            else:
                return f"Column {section}"
        else:
            return f"Row {section}"

    def insertRows(self, row, procs, parent=QModelIndex()):
        self.beginInsertRows(parent, row, row + len(procs) - 1)
        if parent.isValid():
            parentItem = parent.internalPointer()
            for proc in reversed(procs):
                parentItem.children.insert(row, ProcItem(proc, parentItem, []))
        else:
            for proc in reversed(procs):
                self._procs.insert(row, ProcItem(proc, None, []))
        self.endInsertRows()
        return True

    def removeRows(self, row, count, parent=QModelIndex()):
        self.beginRemoveRows(parent, row, row + count - 1)
        if parent.isValid():
            del parent.internalPointer().children[row:row + count]
        else:
            del self._procs[row:row + count]
        self.endRemoveRows()
        return True

    def getProcs(self):
        procList = list(self._procs)
        i = 0
        while i < len(procList):
            procItem = procList[i]
            if procItem.children:
                procList.extend(procItem.children)
            i += 1
        return procList
