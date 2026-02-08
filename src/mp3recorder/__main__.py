"""Entry point for running mp3recorder as a module or from Briefcase."""

import sys


def main():
    """Main entry point - launches menubar app."""
    from mp3recorder.menubar import main as menubar_main
    return menubar_main()


if __name__ == "__main__":
    sys.exit(main())
