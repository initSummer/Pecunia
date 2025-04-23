from .invest import Invest
from .investment_action import InvestmentActionType
from .dict_accessors import cum_dict_accessors, daily_dict_accessors
from .financial_types import InvestType
import src.util as util
from sortedcontainers import SortedDict, SortedList
import datetime
import json


@cum_dict_accessors('_value_line', '_return_line')
@daily_dict_accessors('_daily_return_line', '_daily_return_rate_line')
class Ledger:
    def __init__(self, name: str):
        self._id = -1
        self._name = name
        self._invests: dict[int, Invest] = {}

        self._value_line: SortedDict[datetime.date, float] = SortedDict()
        self._return_line: SortedDict[datetime.date, float] = SortedDict()
        self._daily_return_line: SortedDict[datetime.date, float] = SortedDict()

        self._cashflow: SortedDict[datetime.date, float] = SortedDict()

    def get_id(self) -> int:
        return self._id

    def set_id(self, id: int) -> None:
        self._id = id

    def get_name(self) -> str:
        return self._name

    def set_name(self, name: str):
        self._name = name

    def get_start_date(self):
        return self._value_line.keys()[0]

    def get_end_date(self):
        return self._value_line.keys()[-1]

    def get_invest(self, invest_id: int = None):
        if invest_id is None:
            return self._invests
        else:
            return self._invests.get(invest_id)

    def get_invest_list(self):
        return self._invests.values()

    def get_invest_xirr(self, invest_id: int, start_day: datetime = None, end_day: datetime = None) -> float:
        return self.get_invest(invest_id).xirr(start_day, end_day)

    def add_invest(self, invest_name: str, invest_type_name: str) -> int:
        try:
            invest_type = InvestType(invest_type_name)
        except ValueError as e:
            print(f"Error: {e}")
            return -1
        invest = Invest(invest_name)
        invest_id = 0
        while invest_id in self._invests.keys():
            invest_id += 1
        self._invests[invest_id] = invest
        self._invests[invest_id].set_id(invest_id)
        self._invests[invest_id].set_owner_ledger_id(self._id)
        self._invests[invest_id].set_type(invest_type)

        self.update()

        return invest_id

    def add_exist_invest(self, invest: Invest) -> int:
        invest_id = 0
        while invest_id in self._invests.keys():
            invest_id += 1
        self._invests[invest_id] = invest
        self._invests[invest_id].set_id(invest_id)
        self._invests[invest_id].set_owner_ledger_id(self._id)

    def add_investment_action(self,
                              invest_id: int,
                              year: int, month: int, day: int,
                              investment_action_type: InvestmentActionType,
                              value: float) -> None:
        self._invests[invest_id].add_action(year, month, day, investment_action_type, value)

    def delete_last_action(self, invest_id: int) -> None:
        self._invests[invest_id].delete_last_action()

    def update(self) -> None:
        for invest in self._invests.values():
            invest.set_owner_ledger_id(self._id)
        # sort invest
        temp_invests = list(self._invests.values())
        self._invests.clear()
        sort_type = {}
        for invest_type in InvestType:
            sort_type[invest_type] = []
            for invest in temp_invests:
                if invest.get_type() == invest_type and not invest.get_archiving():
                    sort_type[invest_type].append(invest)
        archiving_invests = []
        for invest in temp_invests:
            if invest.get_archiving():
                archiving_invests.append(invest)

        id_counter = 0
        for invest_type in InvestType:
            sort_type[invest_type] = sorted(sort_type[invest_type], key=lambda invest: invest.get_value(), reverse=True)
            for invest in sort_type[invest_type]:
                self._invests[id_counter] = invest
                self._invests[id_counter].set_id(id_counter)
                id_counter += 1
        archiving_invests = sorted(archiving_invests, key=lambda invest: invest.get_value(), reverse=True)
        for invest in archiving_invests:
            self._invests[id_counter] = invest
            self._invests[id_counter].set_id(id_counter)
            id_counter += 1

        # step 1: get daily return
        #         get cashflow
        self._daily_return_line.clear()
        self._cashflow.clear()
        self._value_line.clear()
        self._return_line.clear()
        for invest in self._invests.values():
            for date, value in invest.get_daily_return_line().items():
                if not date in self._daily_return_line:
                    self._daily_return_line[date] = 0.0
                self._daily_return_line[date] += value

            for date, value in invest.get_cashflow().items():
                if not date in self._cashflow:
                    self._cashflow[date] = 0.0
                self._cashflow[date] += value

        # step 2: get value
        for date in self._daily_return_line.keys():
            for invest in self._invests.values():
                if not date in self._value_line:
                    self._value_line[date] = 0
                self._value_line[date] += invest.get_value(date)

        # step 3: calculate return
        ledger_return = 0
        for date in self._daily_return_line.keys():
            ledger_return += self._daily_return_line[date]
            self._return_line[date] = ledger_return

    def xirr(self, start_day: datetime.date = None, end_day: datetime.date = None) -> float:
        if start_day and end_day and start_day >= end_day:
            return float('nan')

        cashflow = self._cashflow
        if start_day is not None:
            if start_day < self._value_line.keys()[0] or start_day > self._value_line.keys()[-1]:
                return float('nan')
            else:
                cashflow = SortedDict({k: cashflow[k] for k in cashflow.keys() if k >= start_day})
                if start_day not in cashflow:
                    cashflow[start_day] = 0.0
                cashflow[start_day] = -self.get_value(start_day)
        if end_day is not None:
            if end_day > self._value_line.keys()[-1] or end_day < self._value_line.keys()[0]:
                return float('nan')
            else:
                cashflow = SortedDict({k: cashflow[k] for k in cashflow.keys() if k <= end_day})
                if end_day not in cashflow:
                    cashflow[end_day] = 0.0
                if end_day != self._value_line.keys()[-1]:
                    cashflow[end_day] = self.get_value(end_day)
        # if end_day and start_day:
        #     if (end_day - start_day).days <= 7:
        #         print(start_day, end_day)
        #         for date, value in cashflow.items():
        #             print(date, value)

        return util.xirr(cashflow)

    def tagr(self, start_day: datetime.date = None, end_day: datetime.date = None) -> float:
        if start_day is not None:
            if start_day < self._value_line.keys()[0] or start_day > self._value_line.keys()[-1]:
                return float('nan')
        else:
            start_day = self._value_line.keys()[0]

        if end_day is not None:
            if end_day > self._value_line.keys()[-1] or end_day < self._value_line.keys()[0]:
                return float('nan')
        else:
            end_day = self._value_line.keys()[-1]

        if end_day < start_day:
            return float('nan')

        tagr = (self._value_line[end_day] - self._value_line[start_day]) / self._value_line[start_day] / (
                end_day - start_day).days * 365

        return tagr

    def daily_return_rate(self, date: datetime.date = None) -> float:
        if date is None:
            date = self._value_line.keys()[-1]
        elif date <= self._value_line.keys()[0] or date > self._value_line.keys()[-1]:
            return 0

        daily_return_rate = self._daily_return_line[date] / self._value_line[date - datetime.timedelta(days=1)]

    def growth_rate(self, start_time: datetime.date = None, end_time: datetime.date = None) -> float:
        if start_time is None and end_time is None:
            start_time = self._value_line.keys()[0]
            end_time = self._value_line.keys()[-1]
        elif start_time is not None and end_time is not None:
            if start_time not in self._value_line:
                start_time = self.get_start_date()
            if end_time not in self._value_line:
                end_time = self.get_end_date()
        else:
            raise KeyError

        origin_value = self._value_line[start_time]
        delta_value = self._value_line[end_time] - self._value_line[start_time]
        delta_years = (end_time - start_time).days / 365.0
        return delta_value / origin_value / delta_years

    def convert_to_json(self):
        invests = json.dumps([invest.convert_to_dict() for invest in self._invests.values()])
        json_dict = {
            "name": self._name,
            "invests": invests
        }
        return json_dict

    @staticmethod
    def convert_from_json(json_dict: dict):
        name = json_dict["name"]

        ledger = Ledger(name)
        for invest_json in json.loads(json_dict["invests"]):
            ledger.add_exist_invest(Invest.convert_from_dict(invest_json))
        return ledger
