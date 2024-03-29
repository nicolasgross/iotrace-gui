# Copyright (C) 2019 HLRS, University of Stuttgart
# <https://www.hlrs.de/>, <https://www.uni-stuttgart.de/>
#
# This file is part of iotrace-GUI.
#
# iotrace-GUI is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# iotrace-GUI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with iotrace-GUI.  If not, see <https://www.gnu.org/licenses/>.
#
# The following people contributed to the project (in alphabetic order
# by surname):
#
# - Nicolas Gross <https://github.com/nicolasgross>


from PySide2.QtCore import Qt, QAbstractTableModel, QModelIndex


class FilestatsModel (QAbstractTableModel):

    columnMapping = {
            **dict.fromkeys(range(0, 5), 'open'),
            **dict.fromkeys(range(5, 10), 'close'),
            **dict.fromkeys(range(10, 15), 'read'),
            **dict.fromkeys(range(15, 20), 'write')
        }

    columnNames = [
            'O Count (#)', 'O Total (ms)', 'O Avg (ms)', 'O Min (ms)',
            'O Max(ms)',
            'C Count (#)', 'C Total (ms)', 'C Avg (ms)', 'C Min (ms)',
            'C Max(ms)',
            'R Bytes', 'R Total (ms)', 'R Avg (MB/s)', 'R Min (MB/s)',
            'R Max (MB/s)',
            'W Bytes', 'W Total (ms)', 'W Avg (MB/s)', 'W Min (MB/s)',
            'W Max (MB/s)'
        ]

    columnTooltips = [
            'Count of all \'open\' calls',
            'Total time spent in all \'open\' calls',
            'Average time spent in a single \'open\' call',
            'Minimum time spent in a single \'open\' call',
            'Maximum time spent in a single \'open\' call',

            'Count of all \'close\' calls',
            'Total time spent in all \'close\' calls',
            'Average time spent in a single \'close\' call',
            'Minimum time spent in a single \'close\' call',
            'Maximum time spent in a single \'close\' call',

            'Total bytes read in all \'read\' calls',
            'Total time spent in all \'read\' calls',
            'Average read speed among all \'read\' calls',
            'Minimum read speed among all \'read\' calls',
            'Maximum read speed among all \'read\' calls',

            'Total bytes written in all \'write\' calls',
            'Total time spent in all \'write\' calls',
            'Average write speed among all \'write\' calls',
            'Minimum write speed among all \'write\' calls',
            'Maximum write speed among all \'write\' calls'
        ]

    def __init__(self, filestats, parent=None):
        super().__init__(parent)
        self._filestats = filestats

    def getFilestats(self):
        return self._filestats

    def rowCount(self, parent=QModelIndex()):
        return len(self._filestats)

    def columnCount(self, parent=QModelIndex()):
        return 20

    def data(self, index, role):
        if (not index.isValid() or index.column() >= self.columnCount() or
                index.row() >= self.rowCount()):
            return None
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignRight
        elif role == Qt.DisplayRole:
            fStat = self._filestats[index.row()]
            subStat = fStat[FilestatsModel.columnMapping[index.column()]]
            relativeColumn = index.column() % 5
            if relativeColumn == 0:
                return subStat[relativeColumn]
            elif relativeColumn == 1:
                return subStat[relativeColumn] / 1000000.0
            elif relativeColumn == 2:
                if index.column() < 10:
                    if subStat[0] == 0:
                        return 0
                    else:
                        return (subStat[1] / 1000000.0) / subStat[0]
                else:
                    if subStat[1] == 0:
                        return 0
                    else:
                        return (subStat[0] / 1000000.0) / \
                                (subStat[1] / 1000000000.0)
            elif relativeColumn > 2:
                return subStat[relativeColumn - 1] / 1000000.0
        else:
            return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.columnNames[section]
            else:
                fname = self._filestats[section]["filename"]
                if len(fname) > 43:
                    return fname[:20] + ' ... ' + fname[-20:]
                else:
                    return fname
        elif role == Qt.ToolTipRole:
            if orientation == Qt.Horizontal:
                return self.columnTooltips[section]
            else:
                return self._filestats[section]["filename"]
        else:
            return None
