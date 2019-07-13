from PySide2.QtCore import Qt, QAbstractListModel, QModelIndex


class ProcessesModel (QAbstractListModel):

    def __init__(self, procs, parent=None):
        QAbstractListModel.__init__(self, parent)
        self.__procs = procs

    def rowCount(self, parent=QModelIndex()):
        return len(self.__procs)

    def data(self, index, role):
        if (not index.isValid() or index.row() >= self.rowCount()):
            return None
        elif role == Qt.DisplayRole:
            proc = self.__procs[index.row()]
            return f"{proc[0]} - {proc[1]} - rank {proc[2]}"
        elif role == Qt.ItemDataRole:
            return self.__procs[index.row()]
        else:
            return None

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return f"Column {section}"
        else:
            return f"Row {section}"

    def getProcs(self):
        return self.__procs
