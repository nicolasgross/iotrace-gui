#!/usr/bin/env python3

import sys
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QFile


def initGui(window):
    window.actionQuit.triggered.connect(QApplication.closeAllWindows)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    uiFile = QFile("mainwindow.ui")
    uiFile.open(QFile.ReadOnly)

    window = QUiLoader().load(uiFile)
    uiFile.close()

    initGui(window)

    window.show()
    sys.exit(app.exec_())

