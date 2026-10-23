"""Color-coded terminal output, built on colorama."""

from colorama import Fore, Style


def paint(text, color):
    """Wrap text in a color code and switch the color off again afterwards."""
    return f"{color}{text}{Style.RESET_ALL}"


def success(text):
    """Green: a finished calculation."""
    return paint(text, Fore.GREEN)


def failure(text):
    """Red: something went wrong."""
    return paint(text, Fore.RED)


def warning(text):
    """Yellow: something the user should know about."""
    return paint(text, Fore.YELLOW)


def info(text):
    """Cyan: a confirmation or a friendly message."""
    return paint(text, Fore.CYAN)


def heading(text):
    """Bold cyan: titles and section headings."""
    return paint(text, Style.BRIGHT + Fore.CYAN)


def color_help(text):
    """Color the section headings of the help menu (lines like 'Operations:')."""
    lines = []
    for line in text.splitlines():
        if line.endswith(":") and not line.startswith(" "):
            lines.append(heading(line))
        else:
            lines.append(line)
    return "\n".join(lines)