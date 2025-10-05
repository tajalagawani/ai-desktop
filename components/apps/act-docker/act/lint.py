#!/usr/bin/env python3
import sys
from pathlib import Path

# Import your parser and custom exception
# Adjust this import path as needed for your project structure.
from actfile_parser import ActfileParser, ActfileParserError

def main(file_path: str):
    """
    Attempts to parse the given Actfile. If successful, we say "valid".
    Otherwise, report the error and exit non-zero.
    """
    try:
        parser = ActfileParser(file_path)
        parser.parse()  # Will raise ActfileParserError if invalid
        print("Actfile is valid!")
        sys.exit(0)
    except ActfileParserError as e:
        print(f"Lint error: {e}")
        sys.exit(1)
    except Exception as ex:
        print(f"Unexpected error: {ex}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python lint_actfile.py /Users/tajnoah/Desktop/langmvp/act_workflow/flow")
        sys.exit(1)
    main(sys.argv[1])
