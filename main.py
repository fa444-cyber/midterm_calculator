"""Entry point for the enhanced calculator."""

import logging

from app.calculator_repl import repl

if __name__ == "__main__":
    logging.basicConfig(
        filename="calculator.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    repl()