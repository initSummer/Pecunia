import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel
from PySide6.QtGui import QScreen
from PySide6.QtCore import Qt

import json
from sortedcontainers import SortedDict

from src.cli import CliRepl
from src.gui import *
from src.financial import *
from src.util import *
from src.cli import *


def main_gui():
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

# def main_cli():
#     with open(DATA_FILE, "r")as file:
#         ledger_mng= LedgerManager.convert_from_json(json.load(file))
#
#     show_ledger_id = 0
#
#     cli = CliFunc()
#     cli.print_ledger(ledger_mng, show_ledger_id)
#
#
#     for k, v in ledger_mng.get_ledger(show_ledger_id).get_daily_return_line().items()[-7:]:
#         print(f"{k}: {v:.2f}")
#
#     cli.drawer(SortedDict(ledger_mng.get_ledger(show_ledger_id).get_daily_return_line().items()[-30:]), "bar")


if __name__ == '__main__':
    CliRepl().cmdloop()
