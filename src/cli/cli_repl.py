import cmd
import inspect
import shlex
import sys
from functools import wraps
from typing import Callable, List, Dict
from enum import Enum

from .cli_func import CliFunc
from src.util import *

CLI_HISTORY_FILE = "./data/cli_history"


class CliRepl(cmd.Cmd):
    # prompt = f"{PROJECT_NAME} > "

    def __init__(self):
        super().__init__()
        self.instance = CliFunc()
        self.available_commands = self._get_commands()
        print(PROJECT_INFO)

    @property
    def prompt(self)->str:
        if self.instance._get_selected_ledger_id() is None:
            repl_prompt = f"{PROJECT_NAME} $ "
        else:
            repl_prompt = f"{PROJECT_NAME} <{self.instance._get_selected_ledger_id()}-{self.instance._get_selected_ledger_name()}> $ "
        return repl_prompt

    def _get_commands(self) -> List[str]:
        return [
            m for m in dir(self.instance)
            if callable(getattr(self.instance, m)) and not m.startswith("_")
        ]

    def _command_wrapper(fn: Callable):
        @wraps(fn)
        def wrapper(self, line):
            try:
                return fn(self, line)
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)

        return wrapper

    @_command_wrapper
    def do_help(self, line):
        if line:
            method = getattr(self.instance, line, None)
            if method and callable(method):
                print(f"{line}: {inspect.getdoc(method) or "No Docs"}")
                print("Params: ")
                sig = inspect.signature(method)
                for name, param in sig.parameters.items():
                    if name != 'self':
                        print(f" {name}: {param.annotation}")
            else:
                print("Unknown command")
        else:
            print("Command list: ")
            for command in self.available_commands:
                print(f" {command}")

    def default(self, line):
        parts = shlex.split(line)
        if not parts:
            return

        cmd_name = parts[0]
        if cmd_name in self.available_commands:
            method = getattr(self.instance, cmd_name)
            # try:
            args = self._parse_args(method, parts[1:])
            result = method(**args)
            # except Exception as e:
            #     print(f"Params Error: {e}")
        else:
            print(f"Unknown command: {cmd_name}")

    def _parse_args(self, method, raw_args):
        sig = inspect.signature(method)
        params = list(sig.parameters.values())
        args = {}

        for param, value in zip(params, raw_args):
            try:
                args[param.name] = param.annotation(value)
            except ValueError:
                raise TypeError(f"Argument {param.name} must be of type {param.annotation}")
        return args
