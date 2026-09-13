"""Command-line entry point: `python -m isbn_tidy [identifiers...]`.

With no arguments, reads one identifier per line from stdin - handy for
piping a column pulled out of a spreadsheet export.
"""

import sys

from .formatter import format_identifier


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args:
        lines = args
    else:
        lines = [line.rstrip("\n") for line in sys.stdin if line.strip()]

    exit_code = 0
    for raw in lines:
        result = format_identifier(raw)
        if result.valid:
            print(f"{result.kind:8} {result.formatted}")
        else:
            print(f"{result.kind:8} INVALID  {raw!r} -> {result.message}")
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
