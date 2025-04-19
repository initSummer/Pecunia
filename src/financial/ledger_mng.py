from sortedcontainers import SortedDict

from .financial_types import InvestType, InvestmentActionType
from .ledger import Ledger
from .invest import Invest


class LedgerManager:
    def __init__(self):
        self._ledgers = SortedDict()

    def add_ledger(self, ledger_name: str) -> int:
        id = 0
        while id in self._ledgers.keys():
            id += 1
        self._ledgers[id] = Ledger(ledger_name)
        self._ledgers[id].set_id(id)
        return id

    def add_existed_ledger(self, ledger: Ledger):
        id = 0
        while id in self._ledgers.keys():
            id += 1
        self._ledgers[id] = ledger
        ledger.set_id(id)
        return id

    def get_ledger(self, ledger_id: int) -> Ledger:
        if ledger_id not in self._ledgers.keys():
            raise KeyError("Ledger id {} not found".format(ledger_id))
        return self._ledgers[ledger_id]

    def get_ledgers(self) -> SortedDict[Ledger]:
        return self._ledgers

    def add_invest(self, ledger_id: int, invest_name: str) -> int:
        if ledger_id not in self._ledgers.keys():
            raise KeyError("Ledger id {} not found".format(ledger_id))
        return self._ledgers[ledger_id].add_invest(invest_name)

    def get_invest(self, ledger_id: int, invest_id: int):
        if ledger_id not in self._ledgers.keys():
            print(f"Ledger id {ledger_id} not found")
            return None
        if invest_id not in self.get_ledger(ledger_id).get_invest().keys():
            print(f"Invest id {invest_id} not found")
            return None

        return self.get_ledger(ledger_id).get_invest(invest_id)

    def add_investment_action(self,
                              ledger_id: int,
                              invest_id: int,
                              year: int, month: int, day: int,
                              investment_action_type: InvestmentActionType,
                              value: float) -> None:
        if ledger_id not in self._ledgers.keys():
            raise KeyError("Ledger id {} not found".format(ledger_id))
        return self._ledgers[ledger_id].add_investment_action(invest_id,
                                                              year, month, day,
                                                              investment_action_type, value)

    def delete_last_action(self,ledger_id:int, invest_id: int) -> None:
        self._ledgers[ledger_id].delete_last_action(invest_id)

    def set_invest_archiving(self, ledger_id: int, invest_id: int, archiving: bool) -> None:
        if ledger_id not in self._ledgers.keys():
            raise KeyError("Ledger id {} not found".format(ledger_id))
        self._ledgers[ledger_id].get_invest(invest_id).set_archiving(archiving)

    def set_invest_type(self, ledger_id: int, invest_id: int, invest_type: InvestType) -> None:
        self.get_ledger(ledger_id).get_invest(invest_id).set_type(invest_type)

    def get_invest_xirr(self, ledger_id: int, invest_id: int) -> float:
        return self.get_ledger(ledger_id).get_invest_xirr(invest_id)


    def update(self) -> None:
        for ledger in self._ledgers.values():
            for invest in ledger.get_invest_list():
                invest.update()
            ledger.update()

    def convert_to_json(self):
        ledger_list = [ledger.convert_to_json() for ledger in self._ledgers.values()]
        return {
            "ledgers": ledger_list
        }

    @staticmethod
    def convert_from_json(json_dict):
        ledger_list = json_dict["ledgers"]
        ledger_manager = LedgerManager()
        for ledger_json in ledger_list:
            ledger_manager.add_existed_ledger(Ledger.convert_from_json(ledger_json))
        ledger_manager.update()
        return ledger_manager
