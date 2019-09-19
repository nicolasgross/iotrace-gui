from PySide2.QtCore import Qt, QAbstractListModel, QModelIndex


class ProcessesModel (QAbstractListModel):

    def __init__(self, procs, parent=None):
        super().__init__(parent)
        self._procs = procs

    def rowCount(self, parent=QModelIndex()):
        return len(self._procs)

    def data(self, index, role):
        if (not index.isValid() or index.row() >= self.rowCount()):
            return None
        elif role == Qt.DisplayRole:
            proc = self._procs[index.row()]
            return f"{proc[0]} - {proc[1]} - rank {proc[2]}"
        elif role == Qt.ItemDataRole:
            return self._procs[index.row()]
        else:
            return None

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return f"Column {section}"
        else:
            return f"Row {section}"

    def insertRows(self, row, count, parent=None):
        self.beginInsertRows(QModelIndex(), row, row + count - 1)
        self.endInsertRows()
        return True

    def removeRow(self, row, parent=None):
        self.beginRemoveRows(QModelIndex(), row, row)
        self.endRemoveRows()
        return True

    def insertProcs(self, procs, row):
        self._procs[row:row] = procs

    def removeProc(self, proc):
        self._procs.remove(proc)

    def getProcs(self):
        return self._procs
