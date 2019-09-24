import json
from PySide2.QtCore import Qt, QSortFilterProxyModel, Slot

from iotracegui.model.processes_model import ProcessesModel
from iotracegui.model.filestats_model import FilestatsModel
from iotracegui.model.rw_blocks_model import RwBlocksModel
from iotracegui.model.syscalls_model import SyscallsModel


class Model:

    def __init__(self, files):
        self._procsModel = ProcessesModel()
        self._filestatModels = {}   # (id, host, rank) -> filestatModel
        self._rwBlocksModels = {}   # (id, host, rank) -> files -> blocksModel
        self._syscallModels = {}    # (id, host, rank) -> syscallModel

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
        for oldProcItem in self._procsModel.getProcs():
            for newProc in newProcs:
                if oldProcItem.proc == newProc:
                    alreadyOpen.append(oldProcItem.proc)
                    break
        if alreadyOpen:
            raise AlreadyOpenError(str(alreadyOpen))

        for proc, stat in jsonFiles.items():
            self._createModels(proc, stat)
        self._procsModel.insertRows(self._procsModel.rowCount(), newProcs)

    def removeProcs(self, indexedProcs):
        indexedProcs.sort(reverse=True)
        for index, procItem in indexedProcs:
            childrenBackup = list(procItem.children)
            parentIndex = self._procsModel.parent(index)
            rowCount = self._procsModel.rowCount(index)
            if rowCount > 0:
                self._procsModel.removeRows(0, rowCount, index)  # children
            self._procsModel.removeRows(index.row(), 1, parentIndex)  # parent
            self._filestatModels.pop(procItem.proc)
            self._rwBlocksModels.pop(procItem.proc)
            self._syscallModels.pop(procItem.proc)
            if childrenBackup:
                procs = [p.proc for p in childrenBackup]
                self._procsModel.insertRows(self._procsModel.rowCount(), procs)

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

    def mergeAndAdd(self, mergeProc, procs, indexes):
        mergeDict = {}
        mergeDict['trace-id'] = mergeProc[0]
        mergeDict['hostname'] = mergeProc[1]
        mergeDict['rank'] = mergeProc[2]
        mergeDict['file statistics'] = []
        mergeDict['unmatched syscalls'] = []
        for procItem in procs:
            otherFilestatsModel = self.getFilestatsModel(procItem.proc)
            otherFilestats = otherFilestatsModel.sourceModel().getFilestats()
            otherSyscallModel = self.getSyscallsModel(procItem.proc)
            otherSyscalls = otherSyscallModel.sourceModel().getSyscalls()
            self._mergeFilestats(mergeDict, otherFilestats)
            self._mergeSyscallstats(mergeDict, otherSyscalls)
        self._createModels(mergeProc, mergeDict)
        self._procsModel.insertRows(self._procsModel.rowCount(), [mergeProc])
        indexes.sort(reverse=True)
        for index in indexes:
            self._procsModel.removeRows(index.row(), 1)
        procs = [p.proc for p in procs]
        parIndex = self._procsModel.index(self._procsModel.rowCount() - 1, 0)
        self._procsModel.insertRows(self._procsModel.rowCount(parIndex), procs,
                                    parIndex)

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
            if not flag and (fname.startswith(prefix) or
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
