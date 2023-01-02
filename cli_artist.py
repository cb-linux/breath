import tty, sys, termios, atexit
from enum import Enum
from inspect import cleandoc
from itertools import zip_longest
from typing import Union


class CliColors(str, Enum):
    QUESTION = '\033[92m'
    WARNING = '\033[93m'
    STATUS = '\033[94m'
    HEADER = '\033[95m'
    ENDCH = '\033[0m'   

class KeyGetter():
    def arm(self):
        self.old_term = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin)
        
        atexit.register(self.disarm)

    def disarm(self):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_term)

    def getch(self):
        self.arm()
        ch = sys.stdin.read(1)[0]
        self.disarm()
        return ch


def _show_interactive_choice(options: list, flags: list = None, print_selection: bool = True):
    __UNPOINTED = " "
    __POINTED = ">"
    __INDEX = 0
    __LENGTH = len(options)
    __ARROWS = __UP, _ = 65, 66
    __ENTER = 10

    if flags is None:
        flags = []

    def _choices_print():
        for i, (option, flag) in enumerate(zip_longest(options, flags, fillvalue='')):
            if i == __INDEX:
                print(f" {__POINTED} {option} {flag}")
            else:
                print(f" {__UNPOINTED} {option} {flag}")     

    def _choices_clear():
        print(f"\033[{__LENGTH}A\033[J", end='')

    def _move_pointer(ch_ord: int):
        nonlocal __INDEX
        __INDEX = max(0, __INDEX-1) if ch_ord == __UP else min(__INDEX+1, __LENGTH-1)

    def _main_loop():
        kg = KeyGetter()
        _choices_print()
        while True:
            key = ord(kg.getch())
            if key in __ARROWS:
                _move_pointer(key)
            _choices_clear()
            _choices_print()
            if key == __ENTER:
                _choices_clear()
                if print_selection:
                    print(f"Selected: {options[__INDEX]}")
                break 

    _main_loop()
    return options[__INDEX]

def _print_message(clicolor: CliColors, *args, **kwargs) -> None:
    message = cleandoc(' '.join(map(str, args)))
    print(f"{clicolor}{message}{CliColors.ENDCH}", **kwargs)

def print_header(*args, **kwargs) -> None:  
    _print_message(CliColors.HEADER, *args, **kwargs)

def print_warning(*args, **kwargs) -> None:
    _print_message(CliColors.WARNING, *args, **kwargs)

def print_status(*args, **kwargs) -> None:
    _print_message(CliColors.STATUS, *args, **kwargs)

def print_question(*args, options: list = None, flags: list = None, print_selection: bool = True, **kwargs) -> Union[str, None]:
    _print_message(CliColors.QUESTION, *args, **kwargs)
    if options is not None:
        return _show_interactive_choice(options, flags, print_selection)
