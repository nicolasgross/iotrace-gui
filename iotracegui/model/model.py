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

    def _createModels(self, proc, stat):
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
            self._createModels(proc, stat)

        self._procsModel.insertProcs(newProcs, self._procsModel.rowCount())
        self._procsModel.insertRows(self._procsModel.rowCount(), len(newProcs))

    def removeProc(self, proc):
        self._procsModel.removeProc(proc)
        self._filestatModels.pop(proc)
        self._rwBlocksModels.pop(proc)
        self._syscallModels.pop(proc)

    def _mergeSubFstat(self, mergeDict, statIndex, key, otherFstat):
        mergeDict['file statistics'][statIndex][key][0] += otherFstat[key][0]
        mergeDict['file statistics'][statIndex][key][1] += otherFstat[key][1]
        if (mergeDict['file statistics'][statIndex][key][2] >
                otherFstat[key][2]):
            mergeDict['file statistics'][statIndex][key][2] = \
                otherFstat[key][2]
        if (mergeDict['file statistics'][statIndex][key][3] <
                otherFstat[key][3]):
            mergeDict['file statistics'][statIndex][key][3] = \
                otherFstat[key][3]

    def _mergeBlockstats(self, mergeDict, statIndex, key, otherFstat):
        blkStatIndex = -1
        for blockstat in otherFstat[key]:
            for i, mergeBlockstat in enumerate(
                    mergeDict['file statistics'][statIndex][key]):
                if blockstat[0] == mergeBlockstat[0]:
                    blkStatIndex = i
                    break

            if blkStatIndex == -1:
                mergeDict['file statistics'][statIndex][key].append(
                        [blockstat[0], 0])
            mergeDict['file statistics'][statIndex][key][blkStatIndex][1] += \
                blockstat[1]
            blkStatIndex = -1

    def _mergeFilestats(self, mergeDict, otherFilestats):
        statIndex = -1
        for otherFstat in otherFilestats:
            for i, mergeFstat in enumerate(mergeDict['file statistics']):
                if otherFstat['filename'] == mergeFstat['filename']:
                    statIndex = i
                    break

            if statIndex == -1:
                mergeDict['file statistics'].append({})
                mergeDict['file statistics'][statIndex]['filename'] = \
                    otherFstat['filename']
                mergeDict['file statistics'][statIndex]['open'] = \
                    [0, 0, 9999999999999, 0]
                mergeDict['file statistics'][statIndex]['close'] = \
                    [0, 0, 9999999999999, 0]
                mergeDict['file statistics'][statIndex]['read'] = \
                    [0, 0, 9999999999999.0, 0.0]
                mergeDict['file statistics'][statIndex]['read-blocks'] = []
                mergeDict['file statistics'][statIndex]['write'] = \
                    [0, 0, 9999999999999.0, 0.0]
                mergeDict['file statistics'][statIndex]['write-blocks'] = []

            self._mergeSubFstat(mergeDict, statIndex, 'open', otherFstat)
            self._mergeSubFstat(mergeDict, statIndex, 'close', otherFstat)
            self._mergeSubFstat(mergeDict, statIndex, 'read', otherFstat)
            self._mergeBlockstats(mergeDict, statIndex, 'read-blocks',
                                  otherFstat)
            self._mergeSubFstat(mergeDict, statIndex, 'write', otherFstat)
            self._mergeBlockstats(mergeDict, statIndex, 'write-blocks',
                                  otherFstat)
            statIndex = -1

    def _mergeSyscallstats(self, mergeDict, otherSyscalls):
        scStatIndex = -1
        for otherScStat in otherSyscalls:
            for i, mergeScStat in enumerate(mergeDict['unmatched syscalls']):
                if otherScStat['syscall'] == mergeScStat['syscall']:
                    scStatIndex = i
                    break

            if scStatIndex == -1:
                mergeDict['unmatched syscalls'].append({})
                mergeDict['unmatched syscalls'][scStatIndex]['syscall'] = \
                    otherScStat['syscall']
                mergeDict['unmatched syscalls'][scStatIndex]['count'] = 0
                mergeDict['unmatched syscalls'][scStatIndex]['total ns'] = 0
            mergeDict['unmatched syscalls'][scStatIndex]['count'] += \
                otherScStat['count']
            mergeDict['unmatched syscalls'][scStatIndex]['total ns'] += \
                otherScStat['total ns']
            scStatIndex = -1

    def mergeAndAdd(self, mergeProc, procs):
        mergeDict = {}
        mergeDict['trace-id'] = mergeProc[0]
        mergeDict['hostname'] = mergeProc[1]
        mergeDict['rank'] = mergeProc[2]
        mergeDict['file statistics'] = []
        mergeDict['unmatched syscalls'] = []
        for proc in procs:
            otherFilestatsModel = self.getFilestatsModel(proc)
            otherFilestats = otherFilestatsModel.sourceModel().getFilestats()
            otherSyscallModel = self.getSyscallsModel(proc)
            otherSyscalls = otherSyscallModel.sourceModel().getSyscalls()
            self._mergeFilestats(mergeDict, otherFilestats)
            self._mergeSyscallstats(mergeDict, otherSyscalls)
        self._createModels(mergeProc, mergeDict)
        self._procsModel.insertProcs([mergeProc], self._procsModel.rowCount())
        self._procsModel.insertRows(self._procsModel.rowCount(), 1)

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
        super().__init__(parent)
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
        super().__init__(parent)

    def filterAcceptsColumn(self, column, parent):
        return True

    def filterAcceptsRow(self, row, parent):
        regex = self.filterRegularExpression()
        name = self.sourceModel().headerData(row, Qt.Vertical, Qt.DisplayRole)
        if name and regex.isValid():
            return regex.match(name).hasMatch()
        else:
            return False
