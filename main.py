"""Entry point for the enhanced calculator."""

from colorama import init as init_colors

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.calculator_repl import repl
from app.logger import Logger

if __name__ == "__main__":
    init_colors()
    config = CalculatorConfig()
    logger = Logger(config)
    try:
        repl(Calculator(config))
    finally:
        logger.close()