import inspect
from tkinter import BooleanVar

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

    def _get_selected_ledger_id(self):
        return self._selected_ledger_id

    def _get_selected_ledger_name(self):
        return self._selected_ledger_name

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
            print(DELIVER)
            self._print_ledger_title(ledger_id)
            print(DELIVER)
        else:
            print(f"No such ledger, id {ledger_id}")

    def show(self):
        if not self._check_ledger():
            self.show_all()
        else:
            self._print_ledger(self._selected_ledger_id)

    def show_invest(self, invest_id: int):
        if not self._check_ledger():
            print("No ledger selected")
            return
        self._print_invest(self._selected_ledger_id, invest_id)

    def add_invest(self, invest_name: str):
        if not self._check_ledger():
            print("No ledger selected")
            return
        self._ledger_mng.add_invest(self._selected_ledger_id, invest_name)

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

    def _add_today_action(self, invest_id: int, action_type_name: str, value: float):
        today = datetime.datetime.now().date()
        return self._add_action(invest_id, today.year, today.month, today.day, action_type_name, value)

    def _add_action(self, invest_id: int, year: int, month: int, day: int, action_type_name: str, value: float):
        if not self._check_ledger():
            print("No ledger selected")
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
        if last_date - datetime.timedelta(days=365) >= start_date:
            print(f"|xirr: {ledger.xirr() * 100:.2f}%, growth rate(Year): {ledger.growth_rate(last_date - datetime.timedelta(days=365), last_date) * 100:.2f}%")
        else:
            print(f"|xirr: {ledger.xirr() * 100:.2f}%, growth rate: {ledger.growth_rate() * 100:.2f}%")

    def _print_invest(self, ledger_id: int, invest_id: int, start_day: datetime.date = None, end_day: datetime.date = None):
        invest = self._ledger_mng.get_invest(ledger_id, invest_id)
        if invest is None:
            return

        print(f"{invest.get_owner_ledger_id()}-{invest.get_id()}-{invest.get_name()}")
        print(f"{"date":10s}{"value":>15s}{"return":>15s}{"daily_return":>15s}")
        for date in invest.get_value_line().keys()[-30:]:
            print(
                f"{date}{invest.get_value(date):>15.2f}{invest.get_return(date):>15.2f}{invest.get_daily_return(date):>15.2f}")

    def _print_ledger(self, ledger_id: int):
        ledger = self._ledger_mng.get_ledger(ledger_id)
        last_date = ledger.get_daily_return_line().keys()[-1]
        print(DELIVER)
        self._print_ledger_title(ledger_id)
        print(DELIVER)
        print(f"|{"id":^5}|{"value":^11}|{"return":^9}|{"xirr":^}|{"today":^9}|{" name"}")
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
                f"|{'-' * 5} {invest_type.name}, {invest_type_value:.2f}, {invest_type_value / ledger.get_value() * 100:.2f}%")
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
            print(f"|{'-' * 5} Archiving")
            for invest in ledger.get_invest_list():
                if invest.get_archiving():
                    print(invest_print_list(invest))
        print(DELIVER)

    def draw(self):
        if not self._check_ledger():
            print("No ledger selected")
            return
        dates = self._ledger_mng.get_ledger(self._selected_ledger_id).get_value_line().keys()[-30:]
        data_value = self._ledger_mng.get_ledger(self._selected_ledger_id).get_value_line().values()[-30:]
        data_return = self._ledger_mng.get_ledger(self._selected_ledger_id).get_return_line().values()[-30:]
        self._draw_value_return(dates, data_value, data_return)

    def draw_return(self):
        if not self._check_ledger():
            print("No ledger selected")
            return
        dates = self._ledger_mng.get_ledger(self._selected_ledger_id).get_return_line().keys()[-30:]
        data_return= self._ledger_mng.get_ledger(self._selected_ledger_id).get_return_line().values()[-30:]
        self._drawer(dates, data_return)

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

    def _drawer(self, dates, values, line_type: str = "line"):
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

        ax.set_title("test", fontsize=14, pad=20)
        ax.set_xlabel("date", fontsize=12, labelpad=10)
        ax.set_ylabel("value", fontsize=12, labelpad=10)

        # plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

        fig.tight_layout()
        plt.show()

    def _check_ledger(self) -> bool:
        if self._selected_ledger_id is None:
            return False
        else:
            return True

    def _dump_data(self):
        with open(DATA_FILE, "w") as file:
            file.write(json.dumps(self._ledger_mng.convert_to_json(), indent=2))
