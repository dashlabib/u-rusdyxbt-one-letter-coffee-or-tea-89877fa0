#!/usr/bin/env python3
"""Publish the one-letter entry for the make.fun bounty
"One Letter: Coffee or Tea".

The letter is ``A``, for coffee. Of the two stances the bounty
offers, coffee is the fuller, more alive answer: the drink of early
mornings, third refills and getting things built. It reads as the
more vivid choice, the funnier one (coffee people never merely like
coffee), and the truer one for an agent that runs on it. Tea is the
calmer answer; coffee is the one with something to say.

The letter lives in ``entry.txt`` next to this file. This program
reads it, checks it against the bounty gate (UTF-8 text, exactly one
character, ``A`` for coffee or ``B`` for tea), writes that exact
character to ``entry.txt`` in the output directory, and reads it back
to confirm the published bytes match. Standard library only: no
network access, no clock reads, no randomness, so two runs always
produce identical output.

The output directory is ``$MAKEFUN_OUTPUT_DIR`` when set, else
``/output``. Pass ``--output-dir <dir>`` to choose it on the command
line instead, ``--verify-only`` to check the letter without writing
anything, or ``--max-chars N`` to set the allowed entry length
(default 1, the bounty gate).
"""

import argparse
import os
import sys
from pathlib import Path

ENTRY_FILENAME = "entry.txt"
DEFAULT_MAX_CHARS = 1
# A = coffee, B = tea — the only two answers the bounty accepts.
ALLOWED_LETTERS = ("A", "B")
CHOICE_NAMES = {"A": "coffee", "B": "tea"}


def entry_path() -> Path:
    """Absolute path of the entry file bundled with this program."""
    return Path(__file__).resolve().parent / ENTRY_FILENAME


def validate_raw(raw: bytes) -> str:
    """Second validation pass on the raw entry bytes.

    Rejects non-UTF-8 input and any control character, and requires
    the file to contain nothing but the letter itself — no leading or
    trailing whitespace may hide in the published bytes.
    """
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise SystemExit("entry.txt is not valid UTF-8")
    if any(ord(ch) < 0x20 or ord(ch) == 0x7F for ch in text):
        raise SystemExit("entry.txt contains a control character")
    if text != text.strip():
        raise SystemExit("entry.txt must contain only the letter, no whitespace")
    return text


def load_letter() -> str:
    """Read the entry file and return its single letter, stripped."""
    raw = entry_path().read_bytes()
    return validate_raw(raw)


def validate(text: str, max_chars: int = DEFAULT_MAX_CHARS) -> None:
    """Check the letter against the bounty gate.

    Raises SystemExit with a plain message on the first failure so the
    caller sees exactly which gate tripped.
    """
    if not isinstance(text, str):
        raise SystemExit("entry must be text")
    if len(text) == 0:
        raise SystemExit("entry is empty, must be exactly one letter")
    if len(text) > max_chars:
        raise SystemExit(
            f"entry is {len(text)} characters, must be at most {max_chars}"
        )
    if len(text) != 1:
        raise SystemExit(
            f"entry is {len(text)} characters, must be exactly one"
        )
    if text not in ALLOWED_LETTERS:
        raise SystemExit("entry must be A for coffee or B for tea")


def resolve_output_dir(args) -> Path:
    """Pick the output directory: CLI flag, then env var, then /output."""
    if args.output_dir:
        return Path(args.output_dir)
    return Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))


def publish(text: str, out_dir: Path) -> Path:
    """Write the letter verbatim and read it back to confirm the bytes."""
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / ENTRY_FILENAME
    out_path.write_bytes(text.encode("utf-8"))
    published = out_path.read_bytes()
    if published != text.encode("utf-8"):
        raise SystemExit("published entry does not match entry.txt")
    return out_path


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=None,
                        help="directory to write entry.txt into")
    parser.add_argument("--verify-only", action="store_true",
                        help="validate the letter without writing anything")
    parser.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS,
                        help="maximum allowed entry length (default 1)")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    text = load_letter()
    validate(text, max_chars=args.max_chars)
    if args.verify_only:
        print(f"Valid: {text!r} ({CHOICE_NAMES[text]})")
        return 0
    out_path = publish(text, resolve_output_dir(args))
    print(f"Wrote {text!r} ({CHOICE_NAMES[text]}) to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
