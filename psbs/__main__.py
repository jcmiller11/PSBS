"""
PuzzleScript Build System (__main__)

This module serves as the entry point for the PuzzleScript Build System (PSBS).
When executed as the main script, it invokes the _main() function from the
psbs module to start the build process for PuzzleScript games.

Usage:
    python -m psbs
    psbs

Note:
    PSBS is a command-line tool for automating the build process of
    PuzzleScript games. It reads configuration files and templates, processes
    game source files, and generates HTML output for playable games. For
    detailed usage instructions, refer to the project documentation.
"""

from .psbs import _main

_main()
