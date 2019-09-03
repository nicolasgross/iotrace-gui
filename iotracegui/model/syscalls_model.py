from PySide2.QtCore import Qt, QAbstractTableModel, QModelIndex, \
        QSortFilterProxyModel


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
        QAbstractTableModel.__init__(self, parent)
        self.__syscalls = syscalls

    def rowCount(self, parent=QModelIndex()):
        return len(self.__syscalls)

    def columnCount(self, parent=QModelIndex()):
        return 3

    def data(self, index, role):
        if (not index.isValid() or index.column() >= self.columnCount() or
                index.row() >= self.rowCount() or role != Qt.DisplayRole):
            return None
        else:
            scStat = self.__syscalls[index.row()]
            if index.column() == 0:
                return scStat['count']
            elif index.column() == 1:
                return scStat['total ns'] / 1000000.0
            else:
                if scStat['count'] == 0:
                    return 0
                else:
                    return (scStat['total ns'] / 1000000.0) / scStat['count']

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.columnNames[section]
            else:
                return self.__syscalls[section]["syscall"]
        elif role == Qt.ToolTipRole:
            if orientation == Qt.Horizontal:
                return self.columnTooltips[section]
            else:
                return None
        else:
            return None


class SyscallsSortFilterProxyModel (QSortFilterProxyModel):

    def __init__(self, parent=None):
        QSortFilterProxyModel.__init__(self, parent)

    def filterAcceptsColumn(self, column, parent):
        return True

    def filterAcceptsRow(self, row, parent):
        regex = self.filterRegularExpression()
        scName = self.sourceModel().headerData(row, Qt.Vertical,
                                               Qt.DisplayRole)
        if scName and regex.isValid():
            return regex.match(scName).hasMatch()
        else:
            return False
