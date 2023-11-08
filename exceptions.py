from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon
import func


def error_message(title):
    error = QMessageBox()
    error.setWindowIcon(QIcon(func.resource_path("img/warning.png")))
    error.setWindowTitle("Fail")
    error.setText(title)
    error.setIcon(QMessageBox.Warning)
    error.setStandardButtons(QMessageBox.Ok)

    # какую кнопку подсвечивать
    error.setDefaultButton(QMessageBox.Ok)
    error.exec_()
