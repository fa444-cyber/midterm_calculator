"""Entry point for the enhanced calculator."""

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.calculator_repl import repl
from app.logger import Logger

if __name__ == "__main__":
    config = CalculatorConfig()
    logger = Logger(config)
    try:
        repl(Calculator(config))
    finally:
        logger.close()