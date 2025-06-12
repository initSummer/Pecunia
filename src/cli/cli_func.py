import matplotlib

import src.util
from src.financial import *
# from src.financial import ledger_mng, InvestmentAction
from src.financial.ledger_mng import LedgerManager
# from sortedcontainers import SortedDict
from src.util import *

import datetime
import json
# from typing import Callable

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, AutoDateLocator

DELIVER = "|" + "-" * 80

ID_LENGTH = 3
NAME_LENGTH = 40
VALUE_LENGTH = 11
RETURN_LENGTH = 10
XIRR_LENGTH = 8
TAGR_LENGTH = 8

DEFAULT_VALUE_LOG_NUM = 15
DEFAULT_ACTION_LOG_NUM = 16


class CliFunc:
    def __init__(self):
        with open(DATA_FILE, "r") as file:
            self._ledger_mng = LedgerManager.convert_from_json(json.load(file))

        self._selected_ledger_id = None
        self._selected_ledger_name = None

        self._selected_invest_id = None
        self._selected_invest_name = None

        self._anony = False

        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']

    def anonymous(self):
        self._anony = not self._anony
        print(f"Anonymous mode: {self._anony}")

    def _caf(self, total: float, part: float) -> float:
        return calc_anonymous_float(total, part, self._anony)

    def l(self, dir_name: str = None):
        self.ll(dir_name)

    def ll(self, dir_name: str = None):
        if dir_name is None or dir_name == "." or dir_name == "./":
            if self._selected_ledger_id is not None and self._selected_invest_id is not None:
                pass
            elif self._selected_ledger_id is not None and self._selected_invest_id is None:
                self._ll_level_1(self._selected_ledger_id)
            elif self._selected_ledger_id is None and self._selected_invest_id is None:
                self._ll_level_0()
            else:
                raise Exception("Error, select invest but not select ledger")
            return
        elif dir_name == "../" or dir_name == "..":
            if self._selected_ledger_id is not None and self._selected_invest_id is not None:
                self._ll_level_1(self._selected_ledger_id)
            elif self._selected_ledger_id is not None and self._selected_invest_id is None:
                self._ll_level_0()
            elif self._selected_ledger_id is None and self._selected_invest_id is None:
                pass
            else:
                raise Exception("Error, select invest but not select ledger")
            return
        else:
            item_id = self._tran_to_int(dir_name)
            if item_id is not None:
                if self._selected_ledger_id is not None and self._selected_invest_id is not None:
                    print("Error, already selected invest")
                elif self._selected_ledger_id is not None and self._selected_invest_id is None:
                    pass
                elif self._selected_ledger_id is None and self._selected_invest_id is None:
                    self._ll_level_1(item_id)
                else:
                    raise Exception("Error, select invest but not select ledger")
                return
            else:
                print("Error, no such directory")
                return

    def _ll_level_0(self):
        title = self._get_oneline_title()
        print(f"|{"-" * (len(title) - 2)}|")
        print(f"{title}")
        print(f"|{"-" * (len(title) - 2)}|")
        for ledger in self._ledger_mng.get_ledgers().values():
            print(self._get_oneline(ledger, ledger.get_value()))
        print(f"|{"-" * (len(title) - 2)}|")

    def _ll_level_1(self, ledger_id):
        ledger = self._ledger_mng.get_ledger(ledger_id)
        if ledger is not None:
            title = self._get_oneline_title()
            print(f"|{"-" * (len(title) - 2)}|")
            for invest in ledger.get_invest().values():
                print(self._get_oneline(invest, ledger.get_value()))
            print(f"|{"-" * (len(title) - 2)}|")

    def cd(self, dir_name: str):
        dir_name.strip()
        dirs = dir_name.split("/")
        for dir in dirs:
            if dir is None or dir == "":
                pass
            else:
                self._cd_single(dir)

    def _cd_single(self, dir_name: str):
        item_id = self._tran_to_int(dir_name)
        if item_id is not None:
            if self._selected_ledger_id is None and self._selected_invest_id is None:
                if item_id in self._ledger_mng.get_ledgers().keys():
                    self._selected_ledger_id = item_id
                    self._selected_ledger_name = self._ledger_mng.get_ledger(item_id).get_name()
                else:
                    print("Error, no such ledger")
            elif self._selected_ledger_id is not None and self._selected_invest_id is None:
                if self._ledger_mng.get_ledger(self._selected_ledger_id).get_invest(item_id) is not None:
                    self._selected_invest_id = item_id
                    self._selected_invest_name = self._ledger_mng.get_invest(self._selected_ledger_id, self._selected_invest_id).get_name()
                else:
                    print("Error, no such invest")
            else:
                print("Error, no bllower")
        elif dir_name == ".." or dir_name == "../":
            if self._selected_ledger_id is None and self._selected_invest_id is None:
                print("Error, no upper")
            elif self._selected_ledger_id is not None and self._selected_invest_id is None:
                self._selected_ledger_id = None
                self._selected_ledger_name = None
            elif self._selected_ledger_id is not None and self._selected_invest_id is not None:
                self._selected_invest_id = None
                self._selected_invest_name = None
            elif self._selected_ledger_id is None and self._selected_invest_id is not None:
                raise (AssertionError("Program Error!"))
        elif dir_name == "." or dir_name == "./":
            pass
        else:
            print("Error, unknown dir name")

    def exit(self):
        exit(0)

    def show(self, arg1=None, arg2=None, arg3=None):
        if arg1 is None:
            if self._selected_ledger_id is not None and self._selected_invest_id is not None:
                self._print_invest_detail(self._selected_ledger_id, self._selected_invest_id)
            elif self._selected_ledger_id is not None and self._selected_invest_id is None:
                self._print_ledger_detail(self._selected_ledger_id)
            elif self._selected_ledger_id is None and self._selected_invest_id is None:
                self.ll()
            else:
                raise Exception("Error, select invest but not select ledger")
        elif arg1 is not None and arg2 is None:
            if self._selected_ledger_id is not None and self._selected_invest_id is not None:
                if arg1 == "value":
                    self._print_invest_value(self._selected_ledger_id, self._selected_invest_id)
                elif arg1 == "action":
                    self._print_invest_action(self._selected_ledger_id, self._selected_invest_id)
                else:
                    print("Error, unknown arguments.")
            elif self._selected_ledger_id is not None and self._selected_invest_id is None:
                item_id = self._tran_to_int(arg1)
                if item_id is not None:
                    self._print_invest_detail(self._selected_ledger_id, item_id)
                else:
                    print("Error, unknown arguments.")
            elif self._selected_ledger_id is None and self._selected_invest_id is None:
                item_id = self._tran_to_int(arg1)
                if item_id is not None:
                    self._print_ledger_detail(item_id)
                else:
                    print("Error, unknown arguments.")
            else:
                raise Exception("Error, select invest but not select ledger")
        elif arg1 is not None and arg2 is not None and arg3 is None:
            if self._selected_ledger_id is not None and self._selected_invest_id is None:
                show_type = arg1
                invest_id = self._tran_to_int(arg2)
                if invest_id is not None:
                    if show_type == "value":
                        self._print_invest_value(self._selected_ledger_id, invest_id)
                    elif show_type == "action":
                        self._print_invest_action(self._selected_ledger_id, invest_id)
                    else:
                        print("Error, unknown arguments.")
                else:
                    print("Error")
            elif self._selected_ledger_id is not None and self._selected_invest_id is not None:
                show_type = arg1
                log_num = self._tran_to_int(arg2)
                if log_num is not None:
                    if show_type == "value":
                        self._print_invest_value(self._selected_ledger_id, self._selected_invest_id, log_num)
                    elif show_type == "action":
                        self._print_invest_action(self._selected_ledger_id, self._selected_invest_id, log_num)
                    else:
                        print("Error, unknown arguments.")
                else:
                    print("Error, unknown arguments.")
            else:
                print("Error, unknown arguments.")
        elif arg1 is not None and arg2 is not None and arg3 is not None:
            show_type = arg1
            invest_id = self._tran_to_int(arg2)
            log_num = self._tran_to_int(arg3)
            if self._selected_ledger_id is not None and self._selected_invest_id is None:
                if invest_id is not None and log_num is not None:
                    if show_type == "value":
                        self._print_invest_value(self._selected_ledger_id, invest_id, log_num)
                    elif show_type == "action":
                        self._print_invest_action(self._selected_ledger_id, invest_id, log_num)
                    else:
                        print("Error, unknown arguments.")
                else:
                    print("Error")
            else:
                print("Error, unknown arguments.")
        else:
            print("Error, unknown arguments.")

    def mkdir(self, obj_name: str, obj_type: str = None):
        if self._selected_ledger_id is not None and self._selected_invest_id is not None:
            print("Error, cannot create a new object.")
        elif self._selected_ledger_id is not None and self._selected_invest_id is None:
            if obj_type is not None:
                self._add_invest(obj_name, obj_type)
            else:
                print("Error, unknown arguments.")
        elif self._selected_ledger_id is None and self._selected_invest_id is None:
            if obj_type is not None:
                print("Error, unknown arguments.")
            else:
                self._add_ledger(obj_name)
        else:
            raise Exception("Error, select invest but not select ledger")

    def _add_ledger(self, ledger_name: str):
        if format_cn(ledger_name, NAME_LENGTH) is None:
            print(f"Error, name max length {NAME_LENGTH}")
            return
        self._ledger_mng.add_ledger(ledger_name)
        self._ledger_mng.update()
        self._dump_data()

    def _add_invest(self, invest_name: str, invest_type_name: str):
        if format_cn(invest_name, NAME_LENGTH) is None:
            print(f"Error, name max length {NAME_LENGTH}")
            return
        if not self._check_ledger():
            print("No ledger selected")
            return
        self._ledger_mng.add_invest(self._selected_ledger_id, invest_name, invest_type_name)
        self._ledger_mng.update()
        self._dump_data()

    def update(self, invest_id: int, value: float):
        self._add_today_action(invest_id, "UPDATE", value)

    def deposit(self, invest_id: int, value: float):
        self._add_today_action(invest_id, "DEPOSIT", value)

    def withdraw(self, invest_id: int, value: float):
        self._add_today_action(invest_id, "WITHDRAW", value)

    def update_s(self, year: int, month: int, day: int, invest_id: int, value: float):
        self._add_action(invest_id, year, month, day, "UPDATE", value)

    def deposit_s(self, year: int, month: int, day: int, invest_id: int, value: float):
        self._add_action(invest_id, year, month, day, "DEPOSIT", value)

    def withdraw_s(self, year: int, month: int, day: int, invest_id: int, value: float):
        self._add_action(invest_id, year, month, day, "WITHDRAW", value)

    def undo(self, invest_id: int):
        if not self._check_ledger():
            print("No ledger selected")
            return
        self._ledger_mng.delete_last_action(self._selected_ledger_id, invest_id)
        self._ledger_mng.update()
        self._dump_data()

    def draw(self, point_num: int = None):
        if not self._check_ledger():
            print("No ledger selected")
            return
        if point_num is None:
            point_num = 30
        ledger = self._ledger_mng.get_ledger(self._selected_ledger_id)
        dates = ledger.get_value_line().keys()[-point_num:]
        data_value = [self._caf(ledger.get_value(), i) for i in ledger.get_value_line().values()[-point_num:]]
        self._drawer(f"{ledger.get_name()} value", dates, data_value)

    def draw_return(self, point_num: int = None):
        if not self._check_ledger():
            print("No ledger selected")
            return
        if point_num is None:
            point_num = 30
        ledger = self._ledger_mng.get_ledger(self._selected_ledger_id)
        dates = ledger.get_return_line().keys()[-point_num:]
        data_return = [self._caf(ledger.get_value(), i) for i in ledger.get_return_line().values()[-point_num:]]
        self._drawer(f"{ledger.get_name()} return", dates, data_return)

    def draw_daily_return(self, point_num: int = None):
        if not self._check_ledger():
            print("No ledger selected")
            return
        if point_num is None:
            point_num = 30
        ledger = self._ledger_mng.get_ledger(self._selected_ledger_id)
        dates = ledger.get_daily_return_line().keys()[-point_num:]
        data_return = [self._caf(ledger.get_value(), i) for i in ledger.get_daily_return_line().values()[-point_num:]]
        self._drawer(f"{ledger.get_name()} daily return", dates, data_return, "bar")

    def draw_all(self, point_num: int = None):
        if not self._check_ledger():
            print("No ledger selected")
            return

        if point_num is None:
            point_num = 30

        ledger = self._ledger_mng.get_ledger(self._selected_ledger_id)
        dates = ledger.get_value_line().keys()[-point_num:]
        data_values = {}
        data_values[self._selected_ledger_name] = [self._caf(ledger.get_value(), i) for i in ledger.get_value_line().values()[-point_num:]]
        for invest in ledger.get_invest_list():
            # if invest.get_archiving():
            #     continue
            invest_name = invest.get_name()
            invest_value_line = {}
            for date in dates:
                invest_value_line[date] = invest.get_value(date)
            data_values[invest_name] = [self._caf(ledger.get_value(), i) for i in invest_value_line.values()]
        self._draw_all(f"{ledger.get_name()} value", dates, data_values)

    def draw_all_return(self, point_num: int = None):
        if not self._check_ledger():
            print("No ledger selected")
            return

        if point_num is None:
            point_num = 30

        ledger = self._ledger_mng.get_ledger(self._selected_ledger_id)
        dates = ledger.get_value_line().keys()[-point_num:]
        data_values = {}
        data_values[self._selected_ledger_name] = [self._caf(ledger.get_value(), i) for i in ledger.get_return_line().values()[-point_num:]]
        for invest in ledger.get_invest_list():
            # if invest.get_archiving():
            #     continue
            invest_name = invest.get_name()
            invest_value_line = {}
            for date in dates:
                invest_value_line[date] = invest.get_return(date)
            data_values[invest_name] = [self._caf(ledger.get_value(), i) for i in invest_value_line.values()]
        self._draw_all(f"{ledger.get_name()} return", dates, data_values)

    def draw_invest(self, invest_num: int, point_num: int = None):
        if not self._check_ledger():
            print("No ledger selected")
            return
        ledger = self._ledger_mng.get_ledger(self._selected_ledger_id)
        invest = ledger.get_invest(invest_num)
        if invest is None:
            print("No invest found")
            return

        if point_num is None:
            point_num = 30

        dates = invest.get_value_line().keys()[-point_num:]
        data_value = [self._caf(ledger.get_value(), i) for i in invest.get_value_line().values()[-point_num:]]
        self._drawer(f"{invest.get_name()} value", dates, data_value)

    def draw_invest_return(self, invest_num: int, point_num: int = None):
        if not self._check_ledger():
            print("No ledger selected")
        if point_num is None:
            point_num = 30
        ledger = self._ledger_mng.get_ledger(self._selected_ledger_id)
        invest = ledger.get_invest(invest_num)
        if invest is None:
            print("No invest found")
            return

        dates = invest.get_return_line().keys()[-point_num:]
        data_return = [self._caf(ledger.get_value(), i) for i in invest.get_return_line().values()[-point_num:]]
        self._drawer(f"{invest.get_name()} return", dates, data_return)

    def draw_invest_daily_return(self, invest_num: int, point_num: int = None):
        if not self._check_ledger():
            print("No ledger selected")
        if point_num is None:
            point_num = 30
        ledger = self._ledger_mng.get_ledger(self._selected_ledger_id)
        invest = ledger.get_invest(invest_num)
        if invest is None:
            print("No invest found")
            return

        dates = invest.get_daily_return_line().keys()[-point_num:]
        data_daily_return = [self._caf(ledger.get_value(), i) for i in invest.get_daily_return_line().values()[-point_num:]]
        self._drawer(f"{invest.get_name()} daily return", dates, data_daily_return)

    def _get_selected_ledger_id(self):
        return self._selected_ledger_id

    def _get_selected_ledger_name(self):
        return self._selected_ledger_name

    def _get_selected_invest_id(self):
        return self._selected_invest_id

    def _get_selected_invest_name(self):
        return self._selected_invest_name

    def _add_today_action(self, invest_id: int, action_type_name: str, value: float):
        today = datetime.datetime.now().date()
        return self._add_action(invest_id, today.year, today.month, today.day, action_type_name, value)

    def _add_action(self, invest_id: int, year: int, month: int, day: int, action_type_name: str, value: float):
        if not self._check_ledger():
            print("No ledger selected")
            return
        if self._ledger_mng.get_ledger(self._selected_ledger_id).get_invest(invest_id) is None:
            print("No invest found")
            return
        action_type = InvestmentActionType(action_type_name)
        try:
            value = float(value)
        except ValueError:
            print(f"Invalid value {value}")
            return
        self._ledger_mng.add_investment_action(self._selected_ledger_id, invest_id,
                                               year, month, day,
                                               action_type, value)
        self._ledger_mng.update()
        self._dump_data()

    def _get_oneline_title(self):
        line = f"|{"id":^{ID_LENGTH}}"
        line += f"|{"name":^{NAME_LENGTH}}"
        line += f"|{"value":^{VALUE_LENGTH}}"
        line += f"|{"return":^{RETURN_LENGTH}}"
        line += f"|{"xirr":^{XIRR_LENGTH}}"
        line += f"|"
        return line

    def _get_oneline(self, obj, total) -> str:
        line = f"|{obj.get_id():^{ID_LENGTH}}"
        line += f"|{format_cn(obj.get_name(), NAME_LENGTH, "^")}"
        line += f"|{self._caf(total, obj.get_value()):>{VALUE_LENGTH}.2f}"
        line += f"|{self._caf(total, obj.get_return()):>{RETURN_LENGTH}.2f}"
        line += f"|{f"{obj.xirr() * 100:.2f}%":>{XIRR_LENGTH}}"
        line += f"|"
        return line

    def _print_invest_detail(self, ledger_id: int, invest_id: int):
        self._print_invest_value(ledger_id, invest_id)

    def _print_invest_sth(self, ledger_id: int, invest_id: int, log_num: int = None):
        pass

    def _print_invest_value(self, ledger_id: int, invest_id: int, log_num: int = None):
        invest = self._ledger_mng.get_invest(ledger_id, invest_id)
        ledger = self._ledger_mng.get_ledger(invest.get_owner_ledger_id())
        if invest is None:
            print("Error, no such invest.")
            return

        end_day = invest.get_value_line().keys()[-1]
        print(f"<{ledger.get_name()}-{invest.get_id()}> {invest.get_name()}")
        xirr_str = f"xirr: {invest.xirr() * 100:.2f}%\n"
        xirr_str += f"    week: {invest.xirr(end_day - datetime.timedelta(days=7), end_day) * 100:.3f}%"
        xirr_str += f", month: {invest.xirr(end_day - datetime.timedelta(days=30), end_day) * 100:.3f}%"
        xirr_str += f", year: {invest.xirr(end_day - datetime.timedelta(days=365), end_day) * 100:.3f}%"
        print(f"{xirr_str}")
        print(f"{"date":10s}{"value":>15s}{"return":>15s}{"daily_return":>15s}")
        if log_num is None:
            log_num = DEFAULT_VALUE_LOG_NUM
        for date in invest.get_value_line().keys()[-log_num:]:
            string = f"{date.strftime("%Y-%m-%d"):<10s}"
            string += f"{self._caf(ledger.get_value(), invest.get_value(date)):>15.2f}"
            string += f"{self._caf(ledger.get_value(), invest.get_return(date)):>15.2f}"
            string += f"{self._caf(ledger.get_value(), invest.get_daily_return(date)):>15.2f}"
            print(string)
        print(f"{DELIVER}")

    def _print_invest_action(self, ledger_id: int, invest_id: int, log_num: int = None):
        invest = self._ledger_mng.get_invest(ledger_id, invest_id)
        ledger = self._ledger_mng.get_ledger(invest.get_owner_ledger_id())
        if invest is None:
            return

        print(f"<{ledger.get_name()}-{invest.get_id()} {invest.get_name()}>")
        if log_num is None:
            log_num = DEFAULT_ACTION_LOG_NUM
        i = 0
        action_str = ""
        for date, actions in reversed(invest._actions.items()):
            for action in reversed(actions):
                action_str = f"{date}, {action.type.value:>8}, {self._caf(ledger.get_value(), action.value):>10}" + action_str
                i += 1
                if i >= log_num:
                    break
                action_str = "\n" + action_str
            if i >= log_num:
                break
        print(action_str)

    def _print_ledger_detail(self, ledger_id: int):
        ledger = self._ledger_mng.get_ledger(ledger_id)
        if ledger is None:
            print("Error, no such ledger.")
        ledger_value = ledger.get_value()
        last_date = ledger.get_daily_return_line().keys()[-1]

        line = f"|{"id":^{ID_LENGTH}}"
        line += f"|{"name":^{NAME_LENGTH}}"
        line += f"|{"value":^{VALUE_LENGTH}}"
        line += f"|{"return":^{RETURN_LENGTH}}"
        line += f"|{"xirr":^{XIRR_LENGTH}}"
        line += f"|{"daily":^{RETURN_LENGTH}}"
        line += f"|"

        print(f"|{"-" * (len(line) - 2)}|")
        temp = f"|Ledger: {ledger.get_name()}, ledger_id: {ledger.get_id()}"
        temp += f"{" " * (len(line) - len(temp) - 1)}|"
        print(temp)
        temp = f"|today: {last_date}, daily_return: {self._caf(ledger_value, ledger.get_daily_return()):.2f}"
        temp += f"{" " * (len(line) - len(temp) - 1)}|"
        print(temp)
        temp = f"|value: {self._caf(ledger_value, ledger.get_value()):.2f}, return: {self._caf(ledger_value, ledger.get_return()):.2f}"
        temp += f"{" " * (len(line) - len(temp) - 1)}|"
        print(temp)
        xirr = f"|xirr: {ledger.xirr() * 100:.2f}%"
        xirr += f"{" " * (len(line) - len(xirr) - 1)}|"
        print(xirr)
        xirr = f"|    week: {ledger.xirr(last_date - datetime.timedelta(days=7), last_date) * 100:.2f}%, "
        xirr += f"month: {ledger.xirr(last_date - datetime.timedelta(days=30), last_date) * 100:.2f}%, "
        xirr += f"year: {ledger.xirr(last_date - datetime.timedelta(days=365), last_date) * 100:.2f}%"
        xirr += f"{" " * (len(line) - len(xirr) - 1)}|"
        print(xirr)
        tagr = f"|tagr: {ledger.tagr() * 100:.2f}%"
        tagr += f"{" " * (len(line) - len(tagr) - 1)}|"
        print(tagr)
        tagr = f"|    year: {ledger.tagr(last_date - datetime.timedelta(days=365), last_date) * 100:.2f}%, "
        tagr += f"3year: {ledger.tagr(last_date - datetime.timedelta(days=(365*3)), last_date) * 100:.2f}%, "
        tagr += f"5year: {ledger.tagr(last_date - datetime.timedelta(days=(365*5)), last_date) * 100:.2f}%"
        tagr += f"{" " * (len(line) - len(tagr) - 1)}|"
        print(tagr)

        print(f"|{"-" * (len(line) - 2)}|")
        print(f"{line}")
        print(f"|{"-" * (len(line) - 2)}|")

        def invest_print_list(invest) -> str:
            print_list = f"|{invest.get_id():^{ID_LENGTH}}"
            print_list += f"|{format_cn(invest.get_name(), NAME_LENGTH, "^")}"
            print_list += f"|{self._caf(ledger_value, invest.get_value()):>{VALUE_LENGTH}.2f}"
            print_list += f"|{self._caf(ledger_value, invest.get_return()):>{RETURN_LENGTH}.2f}"
            print_list += f"|{f"{invest.xirr() * 100:.2f}%":>{XIRR_LENGTH}}"
            print_list += f"|{self._caf(ledger_value, invest.get_daily_return(last_date)):{RETURN_LENGTH}.2f}"
            print_list += f"|"
            return print_list

        for invest_type in InvestType:
            invest_type_value = 0
            for invest in ledger.get_invest_list():
                if invest.get_type() == invest_type and not invest.get_archiving():
                    invest_type_value += invest.get_value()
            if invest_type_value == 0:
                continue
            invest_type_value = self._caf(ledger_value, invest_type_value)
            type_line = f"|Type: {invest_type.name: >10}"
            type_line += f", {invest_type_value:>11.2f}"
            type_line += f", {invest_type_value / self._caf(ledger_value, ledger.get_value()) * 100:>7.2f}%"
            type_line += f"{" " * (len(line) - len(type_line) - 1)}|"
            print(type_line)
            for invest in ledger.get_invest_list():
                if invest.get_type() not in InvestType:
                    raise (ValueError, "Invest type unknown")
                if invest.get_type() == invest_type and not invest.get_archiving():
                    print(invest_print_list(invest))
            print(f"|{"-" * (len(line) - 2)}|")

        has_archiving = False
        for invest in ledger.get_invest_list():
            if invest.get_archiving():
                has_archiving = True
        if has_archiving:
            archiving_line = f"| Archiving "
            archiving_line += f"{" " * (len(line) - len(archiving_line) - 1)}|"
            print(f"{archiving_line}")
            for invest in ledger.get_invest_list():
                if invest.get_archiving():
                    print(invest_print_list(invest))
            print(f"|{"-" * (len(line) - 2)}|")

    def _draw_value_return(self, dates, values, returns):
        fig, ax = plt.subplots(figsize=(12, 6))

        ax.plot(dates, values,
                color='#2c7fb9',
                linewidth=1)
        ax.plot(dates, returns,
                color='#00ffff',
                linewidth=1)

        date_format = DateFormatter("%Y-%m-%d")
        ax.xaxis.set_major_formatter(date_format)
        ax.xaxis.set_major_locator(AutoDateLocator())

        ax.grid(True, linestyle='--', alpha=0.3, color='#636363')

        ax.set_title("", fontsize=14, pad=20)
        ax.set_xlabel("date", fontsize=12, labelpad=10)
        ax.set_ylabel("value/return", fontsize=12, labelpad=10)

        # plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

        fig.tight_layout()
        plt.show()

    def _drawer(self, name: str, dates, values, line_type: str = "line"):
        fig, ax = plt.subplots(figsize=(12, 6))

        if line_type == "line":
            ax.plot(dates, values,
                    color='#2c7fb9',
                    linewidth=1)
        elif line_type == "bar":
            ax.bar(dates, values, color='#2c7fb9', width=0.7)
        # linewidth=2,
        # marker='o',
        # markersize=6,
        # markeredgecolor='#d7191c',
        # markerfacecolor='white')

        date_format = DateFormatter("%Y-%m-%d")
        ax.xaxis.set_major_formatter(date_format)
        ax.xaxis.set_major_locator(AutoDateLocator())

        ax.grid(True, linestyle='--', alpha=0.3, color='#636363')

        ax.set_title(name, fontsize=14, pad=20)
        ax.set_xlabel("date", fontsize=12, labelpad=10)
        ax.set_ylabel("value", fontsize=12, labelpad=10)

        # plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

        fig.tight_layout()
        plt.show()

    def _draw_all(self, name: str, dates, value_line_map):
        if len(dates) == 0:
            return
        for name, values in value_line_map.items():
            if len(values) != len(dates):
                raise ValueError(f"Series'{name}' len error")

        fig, ax = plt.subplots(figsize=(12, 6))

        color_cycle = plt.cm.get_cmap('tab20', len(value_line_map))

        for idx, (series_name, values) in enumerate(value_line_map.items()):
            ax.plot(dates,
                    values,
                    label=series_name,
                    color=color_cycle(idx),
                    linewidth=1,
                    alpha=0.8,
                    # marker='o' if len(dates) < 30 else None
                    )

        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%Y-%m-%d"))
        ax.xaxis.set_major_locator(matplotlib.dates.AutoDateLocator())
        # fig.autofmt_xdate()

        ax.legend(loc='upper left',
                  bbox_to_anchor=(1.02, 1),
                  borderaxespad=0.,
                  frameon=False,
                  title=None,
                  title_fontsize='large'
                  )
        plt.subplots_adjust(left=0.1,
                            right=0.8,
                            bottom=0.1,
                            top=0.9)

        ax.set_xlabel("date", fontsize=12, labelpad=10)
        ax.set_ylabel("value", fontsize=12, labelpad=10)

        ax.grid(True, linestyle='--', alpha=0.6)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        ax.autoscale(enable=True, axis='both', tight=True)

        plt.show()

    def _check_ledger(self) -> bool:
        if self._selected_ledger_id is None:
            return False
        else:
            return True

    def _check_invest(self, invest_id) -> bool:
        if self._selected_ledger_id is None:
            return False
        elif self._ledger_mng.get_invest(self._selected_ledger_id, invest_id) is None:
            return False
        else:
            return True

    def _dump_data(self):
        with open(DATA_FILE, "w") as file:
            file.write(json.dumps(self._ledger_mng.convert_to_json(), indent=2))

    def _tran_to_int(self, s: str):
        try:
            i = int(s.strip())
            return i
        except ValueError:
            return None
