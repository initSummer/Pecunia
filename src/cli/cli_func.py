import inspect

from src.financial import *
from src.financial import ledger_mng
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


class CliFunc:
    def __init__(self):
        self.ledger_mng = None

    def print_hello(self):
        print("hello world")
        return "Return hello world"

    def _print_hello(self):
        print("Error, should not show")

    def add_invest(self, invest_name: str):
        pass

    def print_invest(self, ledger_mng: LedgerManager, ledger_id: int, invest_id: int):
        invest = ledger_mng.get_invest(ledger_id, invest_id)
        print(f"{invest.get_owner_ledger_id()}-{invest.get_id()}-{invest.get_name()}")
        print(f"{"date":10s}{"value":>15s}{"return":>15s}{"daily_return":>15s}{"daily_return_rate":>20s}")
        print(f"{invest.get_value_line().keys()}")
        for date in invest.get_value_line().keys():
            print(
                f"{date}{invest.get_value(date):>15.2f}{invest.get_return(date):>15.2f}{invest.get_daily_return(date):>15.2f}")

    def print_ledger(self, ledger_mng: LedgerManager, ledger_id: int):
        ledger = ledger_mng.get_ledger(ledger_id)
        last_date = ledger.get_daily_return_line().keys()[-1]
        print(f"|{'-' * 80}")
        print(f"|Ledger: {ledger.get_name()}, ledger_id: {ledger.get_id()}")
        print(f"|today: {last_date}, daily_return: {ledger.get_daily_return():.2f}")
        print(f"|value: {ledger.get_value():.2f}, return: {ledger.get_return():.2f}")
        print(f"|xirr: {ledger.xirr() * 100:.2f}%, growth rate: {ledger.growth_rate(None, None) * 100:.2f}%")
        print(f"|{'-' * 80}")
        print(f"|{"id":^5}|{"value":^11}|{"return":^9}|{"xirr":^}|{"today":^9}|{" name"}")
        print(f"|{'-' * 80}")

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
        print(f"|{'-' * 80}")

    def draw_ledger(self, ledger_mng: LedgerManager, ledger_id: int):
        pass

    def draw_value_return(self, data_value, data_return):
        draw_number = 10
        dates = list(data_value.keys())[-draw_number:]
        values = list(data_value.values())[-draw_number:]
        returns = list(data_return.values())[-draw_number:]

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

        ax.set_title("test", fontsize=14, pad=20)
        ax.set_xlabel("date", fontsize=12, labelpad=10)
        ax.set_ylabel("value", fontsize=12, labelpad=10)

        # plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

        fig.tight_layout()
        plt.show()

    def drawer(self, data: SortedDict[datetime.date, float], line_type: str):
        dates = list(data.keys())
        values = list(data.values())

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

