from enum import Enum


class InvestType(Enum):
    UNDEFINED = "UNDEFINED"
    STABLE = "STABLE"
    CASH = "CASH"
    VOLATILE = "VOLATILE"

    def __lt__(self, other):
        return self.value < other.value


class InvestmentActionType(Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"
    UPDATE = "UPDATE"

    def __lt__(self, other):
        return self.value < other.value
