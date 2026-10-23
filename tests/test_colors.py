"""Tests for the color helpers."""

import pytest
from colorama import Fore, Style

from app.colors import color_help, failure, heading, info, paint, success, warning
from app.help_menu import build_help_menu


def test_paint_wraps_the_text_and_resets_the_color():
    assert paint("hi", Fore.RED) == f"{Fore.RED}hi{Style.RESET_ALL}"


@pytest.mark.parametrize("function, color", [
    (success, Fore.GREEN),
    (failure, Fore.RED),
    (warning, Fore.YELLOW),
    (info, Fore.CYAN),
])
def test_each_helper_uses_its_color(function, color):
    assert function("message") == f"{color}message{Style.RESET_ALL}"


def test_heading_is_bold_cyan():
    expected = f"{Style.BRIGHT}{Fore.CYAN}Title{Style.RESET_ALL}"
    assert heading("Title") == expected


def test_color_help_colors_only_the_section_headings():
    colored = color_help(build_help_menu().render())
    assert heading("Operations:") in colored
    assert heading("Commands:") in colored
    assert "Usage: <operation>" in colored
    assert colored.count(Style.BRIGHT) == 2


def test_color_help_leaves_plain_text_alone():
    assert color_help("nothing to color here") == "nothing to color here"