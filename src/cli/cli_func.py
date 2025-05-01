import inspect
from tkinter import BooleanVar

import matplotlib

from src.financial import *
from src.financial import ledger_mng, InvestmentAction
from src.financial.ledger_mng import LedgerManager
from sortedcontainers import SortedDict
from src.util import *

import datetime
import json
import cmd
import shlex
import sys
from functools import wraps
from typing import Callable

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, AutoDateLocator

DELIVER = "-" * 80


class CliFunc:
    def __init__(self):
        with open(DATA_FILE, "r") as file:
            self._ledger_mng = LedgerManager.convert_from_json(json.load(file))

        self._selected_ledger_id = None
        self._selected_ledger_name = None

        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']

    def exit(self):
        exit(0)

    def show_all(self) -> None:
        for ledger_id in self._ledger_mng.get_ledgers().keys():
            print(DELIVER)
            self._print_ledger_title(ledger_id)
        print(DELIVER)

    def select(self, ledger_id: int) -> None:
        if ledger_id in self._ledger_mng.get_ledgers():
            self._selected_ledger_id = ledger_id
            self._selected_ledger_name = self._ledger_mng.get_ledger(ledger_id).get_name()
            print(f"Selected ledger <{self._selected_ledger_name}>")
            self._print_ledger(ledger_id)
        else:
            print(f"No such ledger, id {ledger_id}")

    def show(self):
        if not self._check_ledger():
            self.show_all()
        else:
            self._print_ledger(self._selected_ledger_id)

    def show_invest(self, invest_id: int, log_num: int = None):
        if not self._check_ledger():
            print("No ledger selected")
            return
        self._print_invest(self._selected_ledger_id, invest_id, log_num=log_num)

    def show_invest_action(self, invest_id: int, log_num: int = None):
        if not self._check_ledger():
            print("No ledger selected")
            return
        self._print_invest_action(self._selected_ledger_id, invest_id, log_num=log_num)

    def add_ledger(self, ledger_name: str):
        self._ledger_mng.add_ledger(ledger_name)

    def add_invest(self, invest_name: str, invest_type_name: str):
        if not self._check_ledger():
            print("No ledger selected")
            return
        self._ledger_mng.add_invest(self._selected_ledger_id, invest_name, invest_type_name)

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
        data_value = ledger.get_value_line().values()[-point_num:]
        self._drawer(f"{ledger.get_name()} value", dates, data_value)

    def draw_return(self, point_num: int = None):
        if not self._check_ledger():
            print("No ledger selected")
            return
        if point_num is None:
            point_num = 30
        ledger = self._ledger_mng.get_ledger(self._selected_ledger_id)
        dates = ledger.get_return_line().keys()[-point_num:]
        data_return = ledger.get_return_line().values()[-point_num:]
        self._drawer(f"{ledger.get_name()} return", dates, data_return)

    def draw_daily_return(self, point_num: int = None):
        if not self._check_ledger():
            print("No ledger selected")
            return
        if point_num is None:
            point_num = 30
        ledger = self._ledger_mng.get_ledger(self._selected_ledger_id)
        dates = ledger.get_daily_return_line().keys()[-point_num:]
        data_return = ledger.get_daily_return_line().values()[
                      -point_num:]
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
        data_values[self._selected_ledger_name] = ledger.get_value_line().values()[-point_num:]
        for invest in ledger.get_invest_list():
            # if invest.get_archiving():
            #     continue
            invest_name = invest.get_name()
            invest_value_line = {}
            for date in dates:
                invest_value_line[date] = invest.get_value(date)
            data_values[invest_name] = invest_value_line.values()
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
        data_values[self._selected_ledger_name] = ledger.get_return_line().values()[-point_num:]
        for invest in ledger.get_invest_list():
            # if invest.get_archiving():
            #     continue
            invest_name = invest.get_name()
            invest_value_line = {}
            for date in dates:
                invest_value_line[date] = invest.get_return(date)
            data_values[invest_name] = invest_value_line.values()
        self._draw_all(f"{ledger.get_name()} return", dates, data_values)

    def draw_invest(self, invest_num: int, point_num: int = None):
        if not self._check_ledger():
            print("No ledger selected")
        if point_num is None:
            point_num = 30
        invest = self._ledger_mng.get_ledger(self._selected_ledger_id).get_invest(invest_num)
        if invest is None:
            print("No invest found")
            return

        dates = invest.get_value_line().keys()[-point_num:]
        data_value = invest.get_value_line().values()[-point_num:]
        self._drawer(f"{invest.get_name()} value", dates, data_value)

    def draw_invest_return(self, invest_num: int, point_num: int = None):
        if not self._check_ledger():
            print("No ledger selected")
        if point_num is None:
            point_num = 30
        invest = self._ledger_mng.get_ledger(self._selected_ledger_id).get_invest(invest_num)
        if invest is None:
            print("No invest found")
            return

        dates = invest.get_return_line().keys()[-point_num:]
        data_return = invest.get_return_line().returns()[-point_num:]
        self._drawer(f"{invest.get_name()} return", dates, data_return)

    def draw_invest_daily_return(self, invest_num: int, point_num: int = None):
        if not self._check_ledger():
            print("No ledger selected")
        if point_num is None:
            point_num = 30
        invest = self._ledger_mng.get_ledger(self._selected_ledger_id).get_invest(invest_num)
        if invest is None:
            print("No invest found")
            return

        dates = invest.get_daily_return_line().keys()[-point_num:]
        data_daily_return = invest.get_daily_return_line().daily_returns()[-point_num:]
        self._drawer(f"{invest.get_name()} daily return", dates, data_daily_return)

    def _get_selected_ledger_id(self):
        return self._selected_ledger_id

    def _get_selected_ledger_name(self):
        return self._selected_ledger_name

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
        self._ledger_mng.add_investment_action(self._selected_ledger_id, invest_id,
                                               year, month, day,
                                               action_type, value)
        self._ledger_mng.update()
        self._dump_data()

    def _print_ledger_title(self, ledger_id: int):
        ledger = self._ledger_mng.get_ledger(ledger_id)
        start_date = ledger.get_start_date()
        last_date = ledger.get_end_date()
        print(f"|Ledger: {ledger.get_name()}, ledger_id: {ledger.get_id()}")
        print(f"|today: {last_date}, daily_return: {ledger.get_daily_return():.2f}")
        print(f"|value: {ledger.get_value():.2f}, return: {ledger.get_return():.2f}")
        xirr = f"|xirr: {ledger.xirr() * 100:.2f}%\n"
        xirr += f"|    week: {ledger.xirr(last_date - datetime.timedelta(days=7), last_date) * 100:.2f}%, "
        xirr += f"month: {ledger.xirr(last_date - datetime.timedelta(days=30), last_date) * 100:.2f}%, "
        xirr += f"year: {ledger.xirr(last_date - datetime.timedelta(days=365), last_date) * 100:.2f}%"
        print(xirr)
        tagr = f"|tagr: {ledger.tagr() * 100:.2f}%\n"
        tagr += f"|    week: {ledger.tagr(last_date - datetime.timedelta(days=7), last_date) * 100:.2f}%, "
        tagr += f"month: {ledger.tagr(last_date - datetime.timedelta(days=30), last_date) * 100:.2f}%, "
        tagr += f"year: {ledger.tagr(last_date - datetime.timedelta(days=365), last_date) * 100:.2f}%"
        print(tagr)

    def _print_invest(self, ledger_id: int, invest_id: int, log_num: int = None,
                      start_day: datetime.date = None, end_day: datetime.date = None):
        invest = self._ledger_mng.get_invest(ledger_id, invest_id)
        if invest is None:
            return

        end_day = invest.get_value_line().keys()[-1]
        print(
            f"<{self._ledger_mng.get_ledger(invest.get_owner_ledger_id()).get_name()}-{invest.get_id()}> {invest.get_name()}")
        xirr_str = f"xirr: {invest.xirr() * 100:.2f}%\n"
        xirr_str += f"    week: {invest.xirr(end_day - datetime.timedelta(days=7), end_day) * 100:.3f}%"
        xirr_str += f", month: {invest.xirr(end_day - datetime.timedelta(days=30), end_day) * 100:.3f}%"
        xirr_str += f", year: {invest.xirr(end_day - datetime.timedelta(days=365), end_day) * 100:.3f}%"
        print(f"{xirr_str}")
        print(f"{"date":10s}{"value":>15s}{"return":>15s}{"daily_return":>15s}")
        if log_num is None:
            log_num = 7
        for date in invest.get_value_line().keys()[-log_num:]:
            print(
                f"{date}{invest.get_value(date):>15.2f}{invest.get_return(date):>15.2f}{invest.get_daily_return(date):>15.2f}")
        print(f"{DELIVER}")

    def _print_invest_action(self, ledger_id: int, invest_id: int, log_num: int = None):
        invest = self._ledger_mng.get_invest(ledger_id, invest_id)
        if invest is None:
            return

        print(
            f"<{self._ledger_mng.get_ledger(invest.get_owner_ledger_id()).get_name()}-{invest.get_id()}> {invest.get_name()}")
        if log_num is None:
            log_num = 30
        i = 0
        action_str = ""
        for date, actions in reversed(invest._actions.items()):
            for action in reversed(actions):
                action_str = f"{date}, {action.type.value:>7}, {action.value:>10}" + action_str
                i += 1
                if i >= log_num:
                    break
                action_str = "\n" + action_str
            if i >= log_num:
                break
        print(action_str)

    def _print_ledger(self, ledger_id: int):
        ledger = self._ledger_mng.get_ledger(ledger_id)
        last_date = ledger.get_daily_return_line().keys()[-1]
        print(DELIVER)
        self._print_ledger_title(ledger_id)
        print(DELIVER)
        print(f"|{"id":^5}|{"value":^11}|{"return":^9}|{"xirr":^9}|{"today":^9}|{" name"}")
        print(DELIVER)

        def invest_print_list(invest) -> str:
            print_list = f"|{invest.get_id():^5}|{invest.get_value():>11.2f}"
            print_list += f"|{invest.get_return():>9.2f}|{f"{invest.xirr() * 100:.2f}%":>9}"
            print_list += f"|{invest.get_daily_return(last_date):9.2f}| {invest.get_name()}"
            return print_list

        for invest_type in InvestType:
            invest_type_value = 0
            for invest in ledger.get_invest_list():
                if invest.get_type() == invest_type and not invest.get_archiving():
                    invest_type_value += invest.get_value()
            if invest_type_value == 0:
                continue
            print(
                f"|{'-' * 5} {invest_type.name:>10}, {invest_type_value:>11.2f}, {invest_type_value / ledger.get_value() * 100:>7.2f}%")
            for invest in ledger.get_invest_list():
                if invest.get_type() not in InvestType:
                    raise (ValueError, "Invest type unknown")
                if invest.get_type() == invest_type and not invest.get_archiving():
                    print(invest_print_list(invest))

        has_archiving = False
        for invest in ledger.get_invest_list():
            if invest.get_archiving():
                has_archiving = True
        if has_archiving:
            print(f"|{'-' * 5} {"Archiving":>10}")
            for invest in ledger.get_invest_list():
                if invest.get_archiving():
                    print(invest_print_list(invest))
        print(DELIVER)

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
