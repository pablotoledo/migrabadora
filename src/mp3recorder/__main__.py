"""Entry point for running mp3recorder as a module."""

import sys

from mp3recorder.cli import main

if __name__ == "__main__":
    sys.exit(main())
