import json
from PySide2.QtCore import Qt, QSortFilterProxyModel, Slot

from iotracegui.model.processes_model import ProcessesModel
from iotracegui.model.filestats_model import FilestatsModel
from iotracegui.model.rw_blocks_model import RwBlocksModel
from iotracegui.model.syscalls_model import SyscallsModel


class Model:

    def __init__(self, files):
        self._procsModel = ProcessesModel([])
        self._filestatModels = {}  # (id, host, rank) -> filestatModel
        self._rwBlocksModels = {}  # (id, host, rank) -> files -> blocksModel
        self._syscallModels = {}  # (id, host, rank) -> syscallModel

    def _parseFiles(self, files):
        newProcStats = {}
        for filename in files:
            with open(filename) as f:
                fileStats = json.load(f)
                newProcStats[(fileStats['trace-id'], fileStats['hostname'],
                              fileStats['rank'])] = fileStats
        return newProcStats

    def openFiles(self, files):
        if not files:
            return

        jsonFiles = self._parseFiles(files)
        newProcs = [*jsonFiles]
        alreadyOpen = []
        for oldProc in self._procsModel.getProcs():
            for newProc in newProcs:
                if oldProc == newProc:
                    alreadyOpen.append(oldProc)
                    break
        if alreadyOpen:
            raise AlreadyOpenError(str(alreadyOpen))

        for proc, stat in jsonFiles.items():
            fstatsModel = FilestatsModel(stat['file statistics'])
            proxyFstatsModel = CheckboxRegexSortFilterProxyTableModel()
            proxyFstatsModel.setSourceModel(fstatsModel)
            self._filestatModels[proc] = proxyFstatsModel

            procRwBlocksModel = {}
            for filestat in stat['file statistics']:
                procRwBlocksModel[filestat['filename']] = \
                    RwBlocksModel(filestat)
            self._rwBlocksModels[proc] = procRwBlocksModel

            syscallsModel = SyscallsModel(stat['unmatched syscalls'])
            proxyScModel = RegexSortFilterProxyTableModel()
            proxyScModel.setSourceModel(syscallsModel)
            self._syscallModels[proc] = proxyScModel

        self._procsModel.insertProcs(newProcs, self._procsModel.rowCount())
        self._procsModel.insertRows(self._procsModel.rowCount(), len(newProcs))

    def removeProc(self, proc):
        self._procsModel.removeProc(proc)
        self._filestatModels.pop(proc)
        self._rwBlocksModels.pop(proc)
        self._syscallModels.pop(proc)

    def getProcsModel(self):
        return self._procsModel

    def getFilestatsModel(self, proc):
        return self._filestatModels[proc]

    def getRwBlocksModel(self, proc, filename):
        return self._rwBlocksModels[proc][filename]

    def getSyscallsModel(self, proc):
        return self._syscallModels[proc]


class AlreadyOpenError (Exception):
    pass


class CheckboxRegexSortFilterProxyTableModel (QSortFilterProxyModel):

    def __init__(self, parent=None):
        QSortFilterProxyModel.__init__(self, parent)
        self._checkboxState = {}

    def filterAcceptsColumn(self, column, parent):
        return True

    def _fileCheckboxFiltered(self, fname):
        for prefix, flag in self._checkboxState.items():
            if flag and (fname.startswith(prefix) or
                         fname.startswith('/' + prefix)):
                return True
        return False

    def filterAcceptsRow(self, row, parent):
        regex = self.filterRegularExpression()
        name = self.sourceModel().headerData(row, Qt.Vertical, Qt.ToolTipRole)
        if name and regex.isValid() and not self._fileCheckboxFiltered(name):
            return regex.match(name).hasMatch()
        else:
            return False

    @Slot(dict)
    def setFilterCheckboxes(self, checkboxState):
        self._checkboxState = checkboxState
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
