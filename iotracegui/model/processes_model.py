from PySide2.QtCore import Qt, QAbstractListModel, QModelIndex


class ProcessesModel (QAbstractListModel):
    def __init__(self, procs, parent=None):
        QAbstractListModel.__init__(self, parent)
        self.__procs = procs

    def rowCount(self, parent=QModelIndex()):
        return len(self.__procs)

    def data(self, index, role):
        if (not index.isValid() or index.row() >= len(self.__procs) or
                role != Qt.DisplayRole):
            return None
        else:
            proc = self.__procs[index.row()]
            return f"{proc[0]} - rank {proc[1]}"

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return "Column %s" % section
        else:
            return "Row %s" % section
