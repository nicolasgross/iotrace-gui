import os
import json
from PySide2.QtCore import QObject, Signal, Qt, QSortFilterProxyModel

from iotracegui.model.processes_model import ProcessesModel
from iotracegui.model.filestats_model import FilestatsModel
from iotracegui.model.syscalls_model import SyscallsModel


class Model (QObject):

    filesLoaded = Signal()

    def __init__(self, files):
        QObject.__init__(self)
        self.__procsModel = None
        self.__filestatModels = None
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
        newSyscallModels = {}  # dict ((host, rank) -> syscallModel)
        if files:
            newStats = self.__parseFiles(files)
            newProcs = [*newStats]
            for proc, stat in newStats.items():
                fstatsModel = FilestatsModel(stat["file statistics"])
                proxyFstatsModel = RegexSortFilterProxyModel()
                proxyFstatsModel.setSourceModel(fstatsModel)
                newFilestatModels[proc] = proxyFstatsModel
                syscallsModel = SyscallsModel(stat["unmatched syscalls"])
                proxyScModel = RegexSortFilterProxyModel()
                proxyScModel.setSourceModel(syscallsModel)
                newSyscallModels[proc] = proxyScModel

        # destruct manually because signals are still connected
        if self.__filestatModels:
            for proc, fstatModel in self.__filestatModels.items():
                del fstatModel
        if self.__syscallModels:
            for proc, syscallsModel in self.__syscallModels.items():
                del syscallsModel
        if self.__procsModel:
            del self.__procsModel

        self.procsModel = ProcessesModel(newProcs)
        self.__filestatModels = newFilestatModels
        self.__syscallModels = newSyscallModels
        self.__files = files
        self.__procStats = newStats
        self.filesLoaded.emit()

    def getProcs(self):
        return self.procsModel.getProcs()

    def getFilestatsModel(self, proc):
        return self.__filestatModels[proc]

    def getSyscallsModel(self, proc):
        return self.__syscallModels[proc]


class RegexSortFilterProxyModel (QSortFilterProxyModel):

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
