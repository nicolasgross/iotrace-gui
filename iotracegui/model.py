import os
import json


class Model:
    def __init__(self, files):
        if files:
            self.updateFiles(files)
        else:
            self.__procStats = {}  # dict ((host, rank) -> stats)

    def updateFiles(self, files):
        newStats = self.__readStats(files)
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
