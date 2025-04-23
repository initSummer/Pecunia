import datetime
from sortedcontainers import SortedDict, SortedList
import json

from .financial_types import InvestType, InvestmentActionType
from .investment_action import InvestmentAction
from .dict_accessors import cum_dict_accessors, daily_dict_accessors
import src.util as util


@cum_dict_accessors('_value_line', '_return_line')
@daily_dict_accessors('_daily_return_line')
class Invest:
    def __init__(self, name: str):
        self._owner_ledger_id: int = -1
        self._id: int = -1
        self._name: str = name
        self._type: InvestType = InvestType.UNDEFINED
        self._actions: SortedDict[datetime.date, SortedList[float]] = SortedDict()
        self._archiving: bool = False

        self._value_line: SortedDict[datetime.date, float] = SortedDict()
        self._return_line: SortedDict[datetime.date, float] = SortedDict()
        self._daily_return_line: SortedDict[datetime.date, float] = SortedDict()
        self._cashflow: SortedDict[datetime.date, float] = SortedDict()

    def set_owner_ledger_id(self, invest_owner_ledger_id: int):
        self._owner_ledger_id = invest_owner_ledger_id

    def get_owner_ledger_id(self) -> int:
        return self._owner_ledger_id

    def set_id(self, invest_id: int):
        self._id = invest_id

    def get_id(self) -> int:
        return self._id

    def set_name(self, name: str) -> None:
        self._name = name

    def get_name(self) -> str:
        return self._name

    def set_type(self, invest_type: InvestType) -> None:
        self._type = invest_type

    def get_type(self) -> InvestType:
        return self._type

    def set_archiving(self, archiving: bool) -> None:
        self._archiving = archiving

    def get_archiving(self) -> bool:
        return self._archiving

    def get_cashflow(self) -> SortedDict[datetime.date, float]:
        return self._cashflow

    def add_action(self,
                   year: int, month: int, day: int,
                   investment_action_type: InvestmentActionType,
                   value: float) -> None:
        date = datetime.date(year, month, day)
        if date not in self._actions:
            self._actions[date] = SortedList()
            max_microsecond = 0
        else:
            max_microsecond = self._actions[date][-1].get_time().microsecond + 1

        time = datetime.datetime(date.year, date.month, date.day, 0, 0, 0, max_microsecond)
        action = InvestmentAction(time, investment_action_type, value)
        self._actions[date].add(action)

    def delete_last_action(self):
        last_day = self._actions.keys()[-1]
        self._actions[last_day].pop(-1)

    def update(self) -> None:
        if len(self._actions) == 0:
            return

        self._value_line.clear()
        self._return_line.clear()
        self._daily_return_line.clear()
        self._cashflow.clear()

        dates = self._actions.keys()
        start_date = dates[0]
        end_date = dates[-1]
        delta = end_date - start_date
        all_dates = [start_date + datetime.timedelta(days=i) for i in range(delta.days + 1)]
        current_value: float = 0
        current_principal: float = 0

        for date in all_dates:
            last_day = date - datetime.timedelta(days=1)
            if date in self._actions:
                for action in self._actions[date]:

                    if date not in self._cashflow:
                        self._cashflow[date] = 0.0

                    if action.type == InvestmentActionType.DEPOSIT:
                        current_value += action.value
                        current_principal += action.value
                        self._cashflow[date] -= action.value
                    elif action.type == InvestmentActionType.WITHDRAW:
                        current_value -= action.value
                        current_principal -= action.value
                        self._cashflow[date] += action.value
                    elif action.type == InvestmentActionType.UPDATE:
                        current_value = action.value
                    else:
                        raise Exception(f"Unknown action: {action}")
            self._value_line[date] = current_value
            self._return_line[date] = current_value - current_principal
            self._daily_return_line[date] = \
                (self._return_line[date] - (self._return_line[last_day] if last_day in self._daily_return_line else 0))

        self._cashflow[last_day + datetime.timedelta(days=1)] += self.get_value()

    def debug_print(self):
        print(f"{self._id}-{self._name}")
        print(f"ACTION:")
        for date, actions in self._actions.items():
            for action in actions:
                print(f"{date} {action}")
        print(f"VALUE LINE:")
        for date, value in self._value_line.items():
            print(f"{date} {value}")

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

        return util.xirr(cashflow)

    def print(self) -> None:
        print(f"{self.get_owner_ledger_id()}-{self.get_id()}-{self.get_name()}")
        print(f"{"date":10s}{"value":>15s}{"return":>15s}{"daily_return":>15s}")
        for date in self.get_value_line().keys():
            print(
                f"{date}{self.get_value(date):>15.2f}{self.get_return(date):>15.2f}{self.get_daily_return(date):>15.2f}")

    def convert_to_dict(self):
        action_list = []
        for actions in self._actions.values():
            for action in actions:
                action_list.append(action.convert_to_dict())
        actions = json.dumps(action_list)
        return {
            "name": self.get_name(),
            "type": self.get_type().value,
            "archiving": self.get_archiving(),
            "actions": actions
        }

    @staticmethod
    def convert_from_dict(json_dict):
        name = json_dict["name"]
        type = InvestType(json_dict["type"])
        archiving = json_dict["archiving"]

        invest = Invest(name)
        invest.set_archiving(archiving)
        invest.set_type(type)

        action_list = json.loads(json_dict["actions"])
        for action_json in action_list:
            action = InvestmentAction.convert_from_dict(action_json)
            invest.add_action(action.get_date().year, action.get_date().month, action.get_date().day,
                              action.get_type(), action.get_value())
        return invest
