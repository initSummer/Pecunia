from sortedcontainers import SortedList, SortedDict
import datetime

from bisect import bisect_left

def get_index(sorted_dict: SortedDict, tar_date: datetime.date):
    dates = list(sorted_dict.keys())

    if not dates:
        return None

    pos = bisect_left(dates, tar_date)

    if pos < len(dates and dates[pos] == tar_date):
        return pos

    return None


def sorted_dict_to_std_dict(sorted_dict: SortedDict) -> dict:
    pass


def std_dict_to_sorted_dict(std_dict: dict) -> SortedDict:
    pass


def sorted_list_to_std_list(sorted_list: SortedList) -> list:
    pass


def std_list_to_sorted_list(std_list: list) -> SortedList:
    pass

def calc_anonymous_float(total: float, part: float, anaoymous: bool) -> float:
    if total == 0 or part == 0:
         return 0
    if anaoymous:
        return part / total * 100
    else:
        return  part
