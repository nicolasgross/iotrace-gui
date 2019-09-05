from PySide2.QtCore import Qt, QRegularExpression
from PySide2.QtWidgets import QAction, QTableView, QApplication
from PySide2.QtGui import QKeySequence


def validateRegex(pattern, lineEdit):
    regex = QRegularExpression(pattern)
    if regex.isValid():
        lineEdit.setStyleSheet("background-color: white;")
    else:
        lineEdit.setStyleSheet("background-color: red;")


# https://stackoverflow.com/questions/21675330/copy-paste-in-qtableview/21679553#21679553
class CopySelectedCellsAction (QAction):

    def __init__(self, tableView):
        if not isinstance(tableView, QTableView):
            raise ValueError("CopySelectedCellsAction must be initialized " +
                             "with a QTableView.")
        super(CopySelectedCellsAction, self).__init__("Copy", tableView)
        self.setShortcuts(QKeySequence.keyBindings(QKeySequence.Copy))
        self.triggered.connect(self.copyCellsToClipboard)
        self.__tableView = tableView

    def copyCellsToClipboard(self):
        selection = self.__tableView.selectionModel().selectedIndexes()
        if len(selection) != 1:
            return
        content = self.__tableView.model().data(selection[0], Qt.DisplayRole)
        QApplication.clipboard().setText(str(content))
