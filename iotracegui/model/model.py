import os
import json

from iotracegui.model.processes_model import ProcessesModel


class Model:
    def __init__(self, files):
        self.updateFiles(files)

    def updateFiles(self, files):
        newStats = {}  # dict ((host, rank) -> stats)
        if files:
            newStats = self.__readStats(files)
            self.procsModel = ProcessesModel([*newStats])
        else:
            self.procsModel = ProcessesModel([])
        self.__procStats = newStats
        self.__files = files
        # TODO update list and table models (refresh observed values)

    def __readStats(self, files):
        newProcStats = {}
        for filename in files:
            run, host, rank = os.path.splitext(
                    os.path.basename(filename))[0].split('_')
            fileStats = None
            with open(filename) as openFile:
                fileStats = json.load(openFile)
            newProcStats[(host, rank)] = fileStats

        return newProcStats
