import os
import sys

from . import globals
from . import helpers
from .constants import Constants


def supports_color():
    try:
        """
        from https://github.com/django/django/blob/master/django/core/management/color.py
        Return True if the running system's terminal supports color and False otherwise.
        """

        plat = sys.platform
        supported_platform = plat != 'Pocket PC' and (plat != 'win32' or 'ANSICON' in os.environ)

        # isatty is not always implemented, #6223.
        is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
        if not supported_platform or not is_a_tty:
            return False
        return True
    except Exception:
        return False


PREFIX_ERROR = '\x1B[1;31;49m[E]\x1B[0m'
PREFIX_INFO = '\x1B[1;32;49m[I]\x1B[0m'
PREFIX_WARN = '\x1B[1;33;49m[W]\x1B[0m'
PREFIX_BINFO = '\x1B[1;34;49m[I]\x1B[0m'
PRINT_SEP = '-' * 75
PRINT_TITLE = "PYINSTALIVE (SCRIPT V{:s} - PYTHON V{:s}) - {:s}".format(Constants.SCRIPT_VERSION, Constants.PYTHON_VERSION, helpers.strdatetime())
SUPP_COLOR = supports_color()
PRECONFIG_STR = ""


def info(log_str, force_plain=False, pre_config=False):
    if SUPP_COLOR and not force_plain:
        to_print = "{:s} {:s}".format(PREFIX_INFO, log_str)
    else:
        to_print = "[I] {:s}".format(log_str)
    if pre_config:
        global PRECONFIG_STR
        PRECONFIG_STR += "[I] {:s}".format(log_str) + "\n"
    print(to_print)
    if globals.config.log_to_file and not pre_config:
        _log_to_file(log_str)


def binfo(log_str, force_plain=False, pre_config=False):
    if SUPP_COLOR and not force_plain:
        to_print = "{:s} {:s}".format(PREFIX_BINFO, log_str)
    else:
        to_print = "[I] {:s}".format(log_str)
    if pre_config:
        global PRECONFIG_STR
        PRECONFIG_STR += "[I] {:s}".format(log_str) + "\n"
    print(to_print)

    if globals.config.log_to_file and not pre_config:
        _log_to_file(log_str)


def warn(log_str, force_plain=False, pre_config=False):
    if SUPP_COLOR and not force_plain:
        to_print = "{:s} {:s}".format(PREFIX_WARN, log_str)
    else:
        to_print = "[W] {:s}".format(log_str)
    if pre_config:
        global PRECONFIG_STR
        PRECONFIG_STR += "[W] {:s}".format(log_str) + "\n"
    print(to_print)
    if globals.config.log_to_file and not pre_config:
        _log_to_file(log_str)


def error(log_str, force_plain=False, pre_config=False):
    if SUPP_COLOR and not force_plain:
        to_print = "{:s} {:s}".format(PREFIX_ERROR, log_str)
    else:
        to_print = "[E] {:s}".format(log_str)
    if pre_config:
        global PRECONFIG_STR
        PRECONFIG_STR += "[E] {:s}".format(log_str) + "\n"
    print(to_print)
    if globals.config.log_to_file and not pre_config:
        _log_to_file(log_str)


def plain(log_str):
    print("{:s}".format(log_str))
    if globals.config.log_to_file:
        _log_to_file("{:s}".format(log_str))


def whiteline():
    print("")
    if globals.config.log_to_file:
        _log_to_file("")


def separator(pre_config=False):
    print(PRINT_SEP)
    if pre_config:
        global PRECONFIG_STR
        PRECONFIG_STR += PRINT_SEP + "\n"
    if globals.config.log_to_file and not pre_config:
        _log_to_file(PRINT_SEP)


def banner(log_only=False, no_log=False, pre_config=True):
    if pre_config:
        global PRECONFIG_STR
        PRECONFIG_STR += PRINT_SEP + "\n" + "[I] {:s}".format(PRINT_TITLE) + "\n" + PRINT_SEP + "\n"
    if no_log:
        print(PRINT_SEP)
        if SUPP_COLOR:
            to_print = "{:s} {:s}".format(PREFIX_BINFO, PRINT_TITLE)
        else:
            to_print = "[I] {:s}".format(PRINT_TITLE)
        print(to_print)
        print(PRINT_SEP)
    elif log_only:
        _log_to_file(PRINT_SEP)
        _log_to_file(PRINT_TITLE)
        _log_to_file(PRINT_SEP)
    else:
        separator()
        binfo(PRINT_TITLE)
        separator()


def _log_to_file(log_str, pre_config=False):
    if globals.config.log_to_file:
        if pre_config:
            global PRECONFIG_STR
            log_str = PRECONFIG_STR
        try:
            suffix = "default"
            try:
                if globals.download.download_user:
                    suffix = globals.download.download_user
            except AttributeError:
                pass
            with open("pyinstalive.{:s}.log".format(suffix), "a+") as f:
                f.write(log_str)
                if not pre_config:
                    f.write('\n')
                f.close()
        except Exception as e:
            print(e)
