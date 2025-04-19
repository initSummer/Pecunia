import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel
from PySide6.QtGui import QScreen
from PySide6.QtCore import Qt

import json
from sortedcontainers import SortedDict

from cli import CliRepl
from gui import *
from financial import *
from util import *
from cli import *


def main_gui():
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    CliRepl().cmdloop()
