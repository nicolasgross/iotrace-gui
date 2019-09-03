from PySide2.QtCore import Qt, QAbstractTableModel, QModelIndex, \
        QAbstractListModel


class FilenamesModel (QAbstractListModel):

    def __init__(self, filestats, parent=None):
        QAbstractListModel.__init__(self, parent)
        self.__filestats = filestats

    def rowCount(self, parent=QModelIndex()):
        return len(self.__filestats)

    def data(self, index, role):
        if (not index.isValid() or index.row() >= self.rowCount()):
            return None
        elif role == Qt.DisplayRole or role == Qt.ItemDataRole:
            return self.__filestats[index.row()]['filename']
        else:
            return None

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return f"Column {section}"
        else:
            return f"Row {section}"


class RwBlocksModel (QAbstractTableModel):

    def __init__(self, filestats, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.__filestats = filestats

    # TODO
