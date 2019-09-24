from PySide2.QtCore import Qt, QSortFilterProxyModel
from PySide2.QtWidgets import QDialog

from iotracegui.view.ui_blocks_dialog import Ui_BlocksDialog
from iotracegui.view.shared_func import CopySelectedCellsAction


class BlocksDialog (QDialog, Ui_BlocksDialog):

    def __init__(self, blocksModel, filename, parent):
        super().__init__()
        self.setupUi(self)
        self._blocksModel = blocksModel
        if len(filename) > 33:
            windowTitle = filename[:15] + ' ... ' + filename[-15:]
        else:
            windowTitle = filename
        self.setWindowTitle(windowTitle)
        sortModel = QSortFilterProxyModel()
        sortModel.setSourceModel(blocksModel)
        self.blocksTableView.setModel(sortModel)
        self.blocksTableView.resizeColumnsToContents()
        self.blocksTableView.addAction(CopySelectedCellsAction(
                self.blocksTableView))
        self.setParent(parent)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
