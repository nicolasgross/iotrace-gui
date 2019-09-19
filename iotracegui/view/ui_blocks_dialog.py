# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_blocks_dialog.ui',
# licensing of 'ui_blocks_dialog.ui' applies.
#
# Created: Thu Sep 19 23:38:43 2019
#      by: pyside2-uic  running on PySide2 5.13.1
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_BlocksDialog(object):
    def setupUi(self, BlocksDialog):
        BlocksDialog.setObjectName("BlocksDialog")
        BlocksDialog.resize(525, 400)
        BlocksDialog.setMinimumSize(QtCore.QSize(511, 0))
        BlocksDialog.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.horizontalLayout = QtWidgets.QHBoxLayout(BlocksDialog)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.blocksTableView = QtWidgets.QTableView(BlocksDialog)
        self.blocksTableView.setMinimumSize(QtCore.QSize(404, 0))
        self.blocksTableView.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.blocksTableView.setSortingEnabled(True)
        self.blocksTableView.setObjectName("blocksTableView")
        self.horizontalLayout.addWidget(self.blocksTableView)

        self.retranslateUi(BlocksDialog)
        QtCore.QMetaObject.connectSlotsByName(BlocksDialog)

    def retranslateUi(self, BlocksDialog):
        BlocksDialog.setWindowTitle(QtWidgets.QApplication.translate("BlocksDialog", "Dialog", None, -1))

