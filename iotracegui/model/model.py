import os
import json
from PySide2.QtCore import QObject, Signal, Qt, QSortFilterProxyModel, \
        QModelIndex, Slot

from iotracegui.model.processes_model import ProcessesModel
from iotracegui.model.filestats_model import FilestatsModel
from iotracegui.model.rw_blocks_model import FilenamesModel, RwBlocksModel
from iotracegui.model.syscalls_model import SyscallsModel


class Model (QObject):

    modelsWillChange = Signal()
    modelsChanged = Signal()

    def __init__(self, files):
        QObject.__init__(self)
        self.__procsModel = None
        self.__filestatModels = None
        self.__filenameModels = None
        self.__rwBlocksModels = None
        self.__syscallModels = None
        self.setFiles(files)

    def __parseFiles(self, files):
        newProcStats = {}
        for filename in files:
            run, host, rank = os.path.splitext(
                    os.path.basename(filename))[0].split('_')
            fileStats = None
            with open(filename) as f:
                fileStats = json.load(f)
            newProcStats[(run, host, rank)] = fileStats
        return newProcStats

    def setFiles(self, files):
        newStats = {}  # dict ((host, rank) -> stats)
        newProcs = []
        newFilestatModels = {}  # dict ((host, rank) -> filestatModel)
        newFilenameModels = {}  # dict ((host, rank) -> files)
        newRwBlocksModels = {}  # dict ((host, rank) -> files -> blocksModel)
        newSyscallModels = {}  # dict ((host, rank) -> syscallModel)
        if files:
            newStats = self.__parseFiles(files)
            newProcs = [*newStats]
            for proc, stat in newStats.items():
                fstatsModel = FilestatsModel(stat['file statistics'])
                proxyFstatsModel = CheckboxRegexSortFilterProxyTableModel()
                proxyFstatsModel.setSourceModel(fstatsModel)
                newFilestatModels[proc] = proxyFstatsModel

                filenamesModel = FilenamesModel(stat['file statistics'])
                proxyFnamesModel = RegexSortFilterProxyListModel()
                proxyFnamesModel.setSourceModel(filenamesModel)
                newFilenameModels[proc] = proxyFnamesModel

                procsRwBlocksModels = {}
                for filestat in stat['file statistics']:
                    procsRwBlocksModels[filestat['filename']] = RwBlocksModel(
                            filestat)
                newRwBlocksModels[proc] = procsRwBlocksModels

                syscallsModel = SyscallsModel(stat['unmatched syscalls'])
                proxyScModel = RegexSortFilterProxyTableModel()
                proxyScModel.setSourceModel(syscallsModel)
                newSyscallModels[proc] = proxyScModel

        self.modelsWillChange.emit()

        self.__files = files
        self.__procStats = newStats
        self.__procsModel = ProcessesModel(newProcs)
        self.__filestatModels = newFilestatModels
        self.__filenameModels = newFilenameModels
        self.__rwBlocksModels = newRwBlocksModels
        self.__syscallModels = newSyscallModels
        self.modelsChanged.emit()

    def getProcsModel(self):
        return self.__procsModel

    def getFilestatsModel(self, proc):
        return self.__filestatModels[proc]

    def getFilenamesModel(self, proc):
        return self.__filenameModels[proc]

    def getRwBlocksModel(self, proc, filename):
        return self.__rwBlocksModels[proc][filename]

    def getSyscallsModel(self, proc):
        return self.__syscallModels[proc]


class CheckboxRegexSortFilterProxyTableModel (QSortFilterProxyModel):

    def __init__(self, parent=None):
        QSortFilterProxyModel.__init__(self, parent)
        self.__checkboxState = {}

    def filterAcceptsColumn(self, column, parent):
        return True

    def __fileCheckboxFiltered(self, fname):
        for prefix, flag in self.__checkboxState.items():
            if flag and (fname.startswith(prefix) or
                         fname.startswith('/' + prefix)):
                return True
        return False

    def filterAcceptsRow(self, row, parent):
        regex = self.filterRegularExpression()
        name = self.sourceModel().headerData(row, Qt.Vertical, Qt.ToolTipRole)
        if name and regex.isValid() and not self.__fileCheckboxFiltered(name):
            return regex.match(name).hasMatch()
        else:
            return False

    @Slot(dict)
    def setFilterCheckboxes(self, checkboxState):
        self.__checkboxState = checkboxState
        self.invalidate()


class RegexSortFilterProxyTableModel (QSortFilterProxyModel):

    def __init__(self, parent=None):
        QSortFilterProxyModel.__init__(self, parent)

    def filterAcceptsColumn(self, column, parent):
        return True

    def filterAcceptsRow(self, row, parent):
        regex = self.filterRegularExpression()
        name = self.sourceModel().headerData(row, Qt.Vertical, Qt.DisplayRole)
        if name and regex.isValid():
            return regex.match(name).hasMatch()
        else:
            return False


class RegexSortFilterProxyListModel (QSortFilterProxyModel):

    def __init__(self, parent=None):
        QSortFilterProxyModel.__init__(self, parent)

    def filterAcceptsColumn(self, column, parent):
        return True

    def filterAcceptsRow(self, row, parent):
        regex = self.filterRegularExpression()
        index = self.sourceModel().index(row, 0, parent=QModelIndex())
        name = self.sourceModel().data(index, Qt.DisplayRole)
        if name and regex.isValid():
            return regex.match(name).hasMatch()
        else:
            return False
