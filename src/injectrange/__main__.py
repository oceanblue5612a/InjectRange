"""Module entry point so `python -m injectrange` works."""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
