import os
import json
from PySide2.QtCore import QObject, Signal

from iotracegui.model.processes_model import ProcessesModel
from iotracegui.model.filestats_model import FilestatsModel, \
        FilestatsSortFilterProxyModel


class Model (QObject):

    filesLoaded = Signal()

    def __init__(self, files):
        QObject.__init__(self)
        self.__procsModel = None
        self.__filestatModels = None
        self.setFiles(files)

    def __parseFiles(self, files):
        newProcStats = {}
        for filename in files:
            run, host, rank = os.path.splitext(
                    os.path.basename(filename))[0].split('_')
            fileStats = None
            with open(filename) as openFile:
                fileStats = json.load(openFile)
            newProcStats[(run, host, rank)] = fileStats

        return newProcStats

    def setFiles(self, files):
        newStats = {}  # dict ((host, rank) -> stats)
        newProcs = []
        newFilestatModels = {}  # dict ((host, rank) -> filestatModel)
        if files:
            newStats = self.__parseFiles(files)
            newProcs = [*newStats]
            for proc, stat in newStats.items():
                fstatModel = FilestatsModel(stat["file statistics"])
                proxyFstatModel = FilestatsSortFilterProxyModel()
                proxyFstatModel.setSourceModel(fstatModel)
                newFilestatModels[proc] = proxyFstatModel

        # destruct manually because signals are still connected
        if self.__filestatModels:
            for proc, fstatModel in self.__filestatModels.items():
                del fstatModel
        if self.__procsModel:
            del self.__procsModel

        self.procsModel = ProcessesModel(newProcs)
        self.__filestatModels = newFilestatModels
        self.__files = files
        self.__procStats = newStats
        self.filesLoaded.emit()

    def getFilestatModel(self, proc):
        return self.__filestatModels[proc]

    def getProcs(self):
        return self.procsModel.getProcs()
