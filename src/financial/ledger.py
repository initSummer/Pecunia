from .invest import Invest
from .investment_action import InvestmentActionType
from .dict_accessors import cum_dict_accessors, daily_dict_accessors
import src.util
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

    def get_invest(self, invest_id: int = None):
        if invest_id is None:
            return self._invests
        else:
            return self._invests.get(invest_id)

    def get_invest_list(self):
        return self._invests.values()

    def get_invest_xirr(self, invest_id: int) -> float:
        return self.get_invest(invest_id).xirr()

    def add_invest(self, invest_name: str) -> int:
        invest = Invest(invest_name)
        invest_id = 0
        while invest_id in self._invests.keys():
            invest_id += 1
        self._invests[invest_id] = invest
        self._invests[invest_id].set_id(invest_id)
        self._invests[invest_id].set_owner_ledger_id(self._id)

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

    def update(self) -> None:
        # step 1: get daily return
        #         get cashflow
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

    def xirr(self) -> float:
        return src.util.xirr(self._cashflow)

    def growth_rate(self, start_time: datetime.date, end_time: datetime.date) -> float:
        if start_time is None and end_time is None:
            origin_value = self._value_line.values()[0]
            delta_value = self._value_line.values()[-1] - self._value_line.values()[0]
            delta_years = (self._value_line.keys()[-1] - self._value_line.keys()[0]).days / 365.0
            return delta_value / origin_value / delta_years
        elif start_time is not None and end_time is not None:
            if start_time not in self._value_line or end_time not in self._value_line:
                raise KeyError
            origin_value = self._value_line[start_time]
            delta_value = self._value_line[end_time] - self._value_line[start_time]
            delta_years = (end_time - start_time).days / 365.0
            return delta_value / origin_value / delta_years
        else:
            raise KeyError

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
