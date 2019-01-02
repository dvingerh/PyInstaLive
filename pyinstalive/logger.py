import os
import sys

try:
    import pil
    import helpers
    from constants import Constants
except ImportError:
    from . import pil
    from . import helpers
    from .constants import Constants


def supports_color():
    try:
        """
        from https://github.com/django/django/blob/master/django/core/management/color.py
        Return True if the running system's terminal supports color,
        and False otherwise.
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


PREFIX_ERROR = '\x1B[1;31;40m[E]\x1B[0m'
PREFIX_INFO = '\x1B[1;32;40m[I]\x1B[0m'
PREFIX_WARN = '\x1B[1;33;40m[W]\x1B[0m'
PREFIX_BINFO = '\x1B[1;34;40m[I]\x1B[0m'
PRINT_SEP = '-' * 75
SUPP_COLOR = supports_color()


def info(log_str, force_plain=False):
    if SUPP_COLOR and not force_plain:
        to_print = "{:s} {:s}".format(PREFIX_INFO, log_str)
    else:
        to_print = "[I] {:s}".format(log_str)
    print(to_print)
    if pil.log_to_file:
        _log_to_file(log_str)


def binfo(log_str, force_plain=False):
    if SUPP_COLOR and not force_plain:
        to_print = "{:s} {:s}".format(PREFIX_BINFO, log_str)
    else:
        to_print = "[I] {:s}".format(log_str)
    print(to_print)
    if pil.log_to_file:
        _log_to_file(log_str)


def warn(log_str, force_plain=False):
    if SUPP_COLOR and not force_plain:
        to_print = "{:s} {:s}".format(PREFIX_WARN, log_str)
    else:
        to_print = "[W] {:s}".format(log_str)
    print(to_print)
    if pil.log_to_file:
        _log_to_file(log_str)


def error(log_str, force_plain=False):
    if SUPP_COLOR and not force_plain:
        to_print = "{:s} {:s}".format(PREFIX_ERROR, log_str)
    else:
        to_print = "[E] {:s}".format(log_str)
    print(to_print)
    if pil.log_to_file:
        _log_to_file(log_str)


def plain(log_str):
    print("{:s}".format(log_str))
    if pil.log_to_file:
        _log_to_file("{:s}".format(log_str))


def whiteline():
    print("")
    if pil.log_to_file:
        _log_to_file("")


def separator():
    print(PRINT_SEP)
    if pil.log_to_file:
        _log_to_file(PRINT_SEP)


def banner():
    separator()
    binfo("PYINSTALIVE (SCRIPT V{:s} - PYTHON V{:s}) - {:s}".format(Constants.SCRIPT_VER, Constants.PYTHON_VER,
                                                                    helpers.strdatetime()))
    separator()


def _log_to_file(log_str):
    try:
        with open("pyinstalive{:s}.log".format(
                "_" + pil.dl_user if len(pil.dl_user) > 0 else ".default"), "a+") as f:
            f.write(log_str + '\n')
            f.close()
    except Exception:
        pass
