from PySide2.QtCore import QFile, Qt, QSortFilterProxyModel
from PySide2.QtUiTools import QUiLoader

from iotracegui.view.shared_func import CopySelectedCellsAction


class BlocksPopup:

    def __init__(self, blocksModel, filename):
        self._blocksModel = blocksModel
        uiFile = QFile("iotracegui/view/blocks_popup.ui")
        uiFile.open(QFile.ReadOnly)
        self._window = QUiLoader().load(uiFile)
        uiFile.close()
        windowTitle = ''
        if len(filename) > 33:
            windowTitle = filename[:15] + ' ... ' + filename[-15:]
        else:
            windowTitle = filename
        self._window.setWindowTitle(windowTitle)
        sortModel = QSortFilterProxyModel()
        sortModel.setSourceModel(blocksModel)
        self._window.blocksTableView.setModel(sortModel)
        self._window.blocksTableView.resizeColumnsToContents()
        self._window.blocksTableView.addAction(
                CopySelectedCellsAction(self._window.blocksTableView))

    def show(self, parent):
        self._window.setParent(parent)
        self._window.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        self._window.show()
