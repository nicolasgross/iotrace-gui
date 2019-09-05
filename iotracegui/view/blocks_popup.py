from PySide2.QtCore import QFile, Qt, QSortFilterProxyModel
from PySide2.QtUiTools import QUiLoader

from iotracegui.view.shared_func import CopySelectedCellsAction


class BlocksPopup:

    def __init__(self, blocksModel, filename):
        self.__blocksModel = blocksModel
        uiFile = QFile("iotracegui/view/blocks_popup.ui")
        uiFile.open(QFile.ReadOnly)
        self.__window = QUiLoader().load(uiFile)
        uiFile.close()
        windowTitle = ''
        if len(filename) > 33:
            windowTitle = filename[:15] + ' ... ' + filename[-15:]
        else:
            windowTitle = filename
        self.__window.setWindowTitle(windowTitle)
        sortModel = QSortFilterProxyModel()
        sortModel.setSourceModel(blocksModel)
        self.__window.blocksTableView.setModel(sortModel)
        self.__window.blocksTableView.resizeColumnsToContents()
        self.__window.blocksTableView.addAction(
                CopySelectedCellsAction(self.__window.blocksTableView))

    def show(self, parent):
        self.__window.setParent(parent)
        self.__window.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        self.__window.show()
