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
