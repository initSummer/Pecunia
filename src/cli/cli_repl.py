import cmd
import inspect
import shlex
import sys
import datetime
from functools import wraps
from typing import Callable, List, Dict
import os
from enum import Enum

from .cli_func import CliFunc
from .terminal_color import TerminalColor
from src.util import *

CLI_HISTORY_FILE = "./data/cli_history"
CLI_LOG_FILE = "./log/cli_log.txt"


class CliRepl(cmd.Cmd):
    def __init__(self):
        super().__init__()
        self.logfile = CLI_LOG_FILE
        self.instance = CliFunc()
        self.available_commands = self._get_commands()
        self._dump_log(f"------ CLI STARTED {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ------")
        print(PROJECT_INFO)

    @property
    def prompt(self) -> str:
        repl_prompt = f"{TerminalColor.GREEN}{PROJECT_NAME}{TerminalColor.RESET}"
        if self.instance._get_selected_ledger_id() is not None:
            repl_prompt += f" <{self.instance._get_selected_ledger_id()}-{self.instance._get_selected_ledger_name()}"
        if self.instance._get_selected_invest_id() is not None:
            repl_prompt += f"/{self.instance._get_selected_invest_id()}-{self.instance._get_selected_invest_name()}"
        repl_prompt += "> $ "
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
        self._dump_log(line)
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
                if param.annotation != inspect.Parameter.empty:
                    args[param.name] = param.annotation(value)
                else:
                    args[param.name] = value
            except ValueError:
                raise TypeError(f"Argument {param.name} must be of type {param.annotation}")
        return args

    def _dump_log(self, line):
        log_dir = os.path.dirname(self.logfile)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} | {line}\n"
        try:
            with open(self.logfile, "a") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Error, failed to log command: {e}")

