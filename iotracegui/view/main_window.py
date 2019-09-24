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


import os
from PySide2.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QAction
from PySide2.QtCore import Slot, QItemSelection, Qt

from iotracegui.view.ui_main_window import Ui_MainWindow
from iotracegui.view.filestats_tab import FilestatsTab
from iotracegui.view.syscalls_tab import SyscallsTab
from iotracegui.model.model import AlreadyOpenError


class MainWindow (QMainWindow, Ui_MainWindow):

    def __init__(self, model):
        super().__init__()
        self.setupUi(self)
        self._model = model
        self._initMenu()
        self._initTabs()
        self._initProcTreeView()

    def _initMenu(self):
        self.actionQuit.triggered.connect(self.close)
        self.actionOpen.triggered.connect(self._menuFileOpen)
        self.actionAbout.triggered.connect(self._menuHelpAbout)
        self.actionAboutQt.triggered.connect(self._menuHelpAboutQt)

    def _initProcTreeView(self):
        self._removeAction = QAction("Remove", self)
        self._removeAction.setEnabled(False)
        self._removeAction.triggered.connect(self._removeProcs)
        self._mergeAction = QAction("Merge", self)
        self._mergeAction.setEnabled(False)
        self._mergeAction.triggered.connect(self._mergeProcs)
        self.processesTreeView.addAction(self._removeAction)
        self.processesTreeView.addAction(self._mergeAction)
        self.processesTreeView.setModel(self._model.getProcsModel())
        self.processesTreeView.selectionModel().selectionChanged. \
            connect(self._filestatsTab.showSelectedProc)
        self.processesTreeView.selectionModel().selectionChanged. \
            connect(self._syscallsTab.showSelectedProc)
        self.processesTreeView.selectionModel().selectionChanged. \
            connect(self._updateContextMenuState)

    @Slot()
    def _removeProcs(self):
        selectedIndexes = self.processesTreeView.selectedIndexes()
        indexedProcs = []
        for index in selectedIndexes:
            procItem = self._model.getProcsModel().data(index, Qt.ItemDataRole)
            indexedProcs.append((index, procItem))
        self.processesTreeView.clearSelection()
        self._model.removeProcs(indexedProcs)

    @Slot()
    def _mergeProcs(self):
        selectedIndexes = self.processesTreeView.selectedIndexes()
        selectedProcs = []
        for index in selectedIndexes:
            selectedProcs.append(self._model.getProcsModel().data(
                index, Qt.ItemDataRole))
        merge_index = 0
        trace_id = selectedProcs[0].proc[0]
        hostname = selectedProcs[0].proc[1]
        merge_proc = (trace_id + '_MERGE_' + str(merge_index), hostname,
                      'NULL')
        procList = (p.proc for p in self._model.getProcsModel().getProcs())
        while merge_proc in procList:
            merge_index += 1
            merge_proc = (trace_id + '_MERGE_' + str(merge_index), hostname,
                          'NULL')
        self._model.mergeAndAdd(merge_proc, selectedProcs, selectedIndexes)

    def _containsParentOrChild(self, selectedIndexes):
        for index in selectedIndexes:
            procItem = index.internalPointer()
            if procItem.parent or procItem.children:
                return True
        return False

    def _containsChild(self, selectedIndexes):
        for index in selectedIndexes:
            procItem = index.internalPointer()
            if procItem.parent:
                return True
        return False

    @Slot(QItemSelection, QItemSelection)
    def _updateContextMenuState(self, selected, deselected):
        selectedIndexes = self.processesTreeView.selectedIndexes()
        hasSelection = self.processesTreeView.selectionModel().hasSelection()

        removeEnabled = hasSelection and not \
            self._containsChild(selectedIndexes)
        self._removeAction.setEnabled(removeEnabled)

        mergeEnabled = len(selectedIndexes) > 1 and not \
            self._containsParentOrChild(selectedIndexes)
        self._mergeAction.setEnabled(mergeEnabled)

    def _initTabs(self):
        self._filestatsTab = FilestatsTab(self, self._model)
        self._syscallsTab = SyscallsTab(self, self._model)

    def closeEvent(self, event):
        result = QMessageBox.question(
                self, 'Confirm Quit', 'Are you sure you want to quit?',
                QMessageBox.Yes | QMessageBox.No)
        if result == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def _menuFileOpen(self):
        files = QFileDialog.getOpenFileNames(self, "Open iotrace files", "",
                                             "iotrace JSON files (*.json)")
        if files[0]:
            try:
                self._model.openFiles(files[0])
            except (KeyError, ValueError, TypeError) as e:
                QMessageBox.warning(
                        self, "Warning", "The selected JSON file is not "
                        "compatible with iotrace-GUI:" + os.linesep +
                        os.linesep + str(e))
            except AlreadyOpenError as e:
                QMessageBox.warning(
                        self, "Warning", "Some files are already loaded:" +
                        os.linesep + os.linesep + str(e))

    def _menuHelpAbout(self):
        # TODO add text from README
        # TODO add links
        # TODO add copyright holder
        # TODO add license
        QMessageBox.about(self, "About", "<h3 align=center>iotrace-GUI</h3>" +
                "<p align=center>TODO</p>" +
                "<p align=center>" +
                "<a href=https://github.com/nicolasgross/iotrace-gui>" +
                "iotrace-GUI</a><br>" +
                "<a href=https://github.com/nicolasgross/iotrace>iotrace</a>" +
                "</p>" +
                "<p align=center>Copyright © 2019 HLRS</p>" +
                "<p align=center>This program comes with absolutely no " +
                "warranty. See the <a href=https://www.gnu.org/licenses/" +
                "gpl-3.0-standalone.html>GNU General Public License, " +
                "version 3</a> for details.</p>")

    def _menuHelpAboutQt(self):
        QMessageBox.aboutQt(self, "About Qt")
