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
        QAbstractTableModel.__init__(self, parent)
        self.__filestats = filestats

    def rowCount(self, parent=QModelIndex()):
        return max(len(self.__filestats['read-blocks']),
                   len(self.__filestats['write-blocks']))

    def columnCount(self, parent=QModelIndex()):
        return 4

    def data(self, index, role):
        if (not index.isValid() or index.column() >= self.columnCount() or
                index.row() >= self.rowCount() or role != Qt.DisplayRole):
            return None
        else:
            if index.column() < 2:
                blocks = self.__filestats['read-blocks']
                if index.row() < len(blocks):
                    return blocks[index.row()][index.column()]
                else:
                    return None
            elif index.column() > 1 and index.column() < 4:
                blocks = self.__filestats['write-blocks']
                if index.row() < len(blocks):
                    return blocks[index.row()][index.column() % 2]
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
