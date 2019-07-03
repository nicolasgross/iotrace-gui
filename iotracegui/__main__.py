import sys
from PySide2.QtWidgets import QApplication

from iotracegui.mainwindow import MainWindow
from iotracegui.model import Model


if __name__ == "__main__":
    app = QApplication(sys.argv)
    model = Model([])
    window = MainWindow(app, model)
    window.show()
    sys.exit(app.exec_())
