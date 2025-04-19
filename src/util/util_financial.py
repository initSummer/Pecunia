import datetime
import pyxirr
from sortedcontainers import SortedDict


def xirr(cashflows: SortedDict[datetime.date, float]) -> float:
    amounts = [cf for cf in cashflows.values()]
    dates = [cf for cf in cashflows.keys()]
    try:
        rate = pyxirr.xirr(dates, amounts)
    except Exception as e:
        rate = 0

    return rate
