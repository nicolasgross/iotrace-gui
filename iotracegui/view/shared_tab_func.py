from PySide2.QtCore import QRegularExpression


def validateRegex(pattern, lineEdit):
    regex = QRegularExpression(pattern)
    if regex.isValid():
        lineEdit.setStyleSheet("background-color: white;")
    else:
        lineEdit.setStyleSheet("background-color: red;")
