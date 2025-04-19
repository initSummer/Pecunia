from typing import Callable, Optional
import datetime
from sortedcontainers import SortedDict


def cum_dict_accessors(*attributes: str) -> Callable:
    def cum_decorator(cls: type) -> type:
        for attr in attributes:
            def make_methods(attr_name: str) -> None:
                def get_sth(self, date: Optional[datetime.datetime] = None) -> float:
                    if date is None:
                        if len(getattr(self, attr_name)) == 0:
                            return 0
                        else:
                            return getattr(self, attr_name).values()[-1]
                    else:
                        if date < getattr(self, attr_name).keys()[0]:
                            return 0
                        elif date > getattr(self, attr_name).keys()[-1]:
                            return getattr(self, attr_name).values()[-1]
                        else:
                            return getattr(self, attr_name)[date]

                get_sth.__name__ = f"get{attr_name[:-5]}"

                def get_sth_line(self) -> SortedDict[datetime.datetime, float]:
                    return getattr(self, attr_name)

                get_sth_line.__name__ = f"get{attr_name}"

                setattr(cls, get_sth.__name__, get_sth)
                setattr(cls, get_sth_line.__name__, get_sth_line)

            make_methods(attr)

        return cls

    return cum_decorator


def daily_dict_accessors(*attributes: str) -> Callable:
    def daily_decorator(cls: type) -> type:
        for attr in attributes:
            def make_methods(attr_name: str) -> None:
                def get_sth(self, date: Optional[datetime.datetime] = None) -> float:
                    if date is None:
                        if len(getattr(self, attr_name)) == 0:
                            return 0
                        else:
                            return getattr(self, attr_name).values()[-1]
                    else:
                        if date not in getattr(self, attr_name):
                            return 0
                        else:
                            return getattr(self, attr_name)[date]

                get_sth.__name__ = f"get{attr_name[:-5]}"

                def get_sth_line(self) -> SortedDict[datetime.datetime, float]:
                    return getattr(self, attr_name)

                get_sth_line.__name__ = f"get{attr_name}"

                setattr(cls, get_sth.__name__, get_sth)
                setattr(cls, get_sth_line.__name__, get_sth_line)

            make_methods(attr)

        return cls

    return daily_decorator
