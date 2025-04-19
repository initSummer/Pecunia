from .financial_types import InvestmentActionType
import datetime
import json


class InvestmentAction:
    def __init__(self, time: datetime.datetime, investment_action_type: InvestmentActionType, value: float):
        self.time = time
        self.type = investment_action_type
        self.value = value

    def get_date(self) -> datetime.date:
        return self.time.date()

    def get_time(self) -> datetime.datetime:
        return self.time

    def get_value(self) -> float:
        return self.value

    def get_type(self) -> InvestmentActionType:
        return self.type

    def __repr__(self):
        return f"<{self.time} {self.type} {self.value}>"

    def __lt__(self, other):
        return self.time < other.time or (self.time == other.time and self.type < other.type) or (
                self.time == other.time and self.type == other.type and self.value < other.value)

    def convert_to_dict(self):
        return {"time": self.time.isoformat(), "type": self.type.value, "value": self.value}

    @staticmethod
    def convert_from_dict(json_dict):
        time = datetime.datetime.fromisoformat(json_dict["time"])
        type = InvestmentActionType(json_dict["type"])
        value = json_dict["value"]
        return InvestmentAction(time, type, value)


if __name__ == "__main__":
    ia_0 = InvestmentAction(datetime.datetime(2024, 12, 4, 5, 12, 32, 21), InvestmentActionType.UPDATE, 10)
    print(ia_0)
    dict = ia_0.convert_to_json()
    print(dict)
    print(InvestmentAction.convert_from_json(dict))
