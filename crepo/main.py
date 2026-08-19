"""Command-line interface for collecting a repository text bundle."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Iterable, Sequence


DEFAULT_EXTENSIONS = frozenset(
    {
        ".c",
        ".css",
        ".csv",
        ".go",
        ".h",
        ".html",
        ".java",
        ".js",
        ".json",
        ".jsx",
        ".md",
        ".php",
        ".py",
        ".rb",
        ".rs",
        ".sh",
        ".sql",
        ".svg",
        ".toml",
        ".ts",
        ".tsx",
        ".txt",
        ".xml",
        ".yaml",
        ".yml",
    }
)
DEFAULT_EXCLUDED_DIRECTORIES = frozenset(
    {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".venv",
        "__pycache__",
        "build",
        "coverage",
        "dist",
        "node_modules",
        "venv",
    }
)
DEFAULT_EXCLUDED_FILENAMES = frozenset(
    {
        ".env",
        ".npmrc",
        "credentials.json",
        "secrets.json",
        "service-account.json",
    }
)


def normalize_extensions(values: Iterable[str]) -> frozenset[str]:
    """Return lowercase extensions with a leading period."""
    normalized = set()
    for value in values:
        for extension in value.split(","):
            extension = extension.strip().lower()
            if extension:
                normalized.add(extension if extension.startswith(".") else f".{extension}")
    return frozenset(normalized)


def is_text_file(path: Path, extensions: frozenset[str]) -> bool:
    """Check an allowlisted extension before attempting to read a file."""
    return path.suffix.lower() in extensions


def iter_text_files(
    directory: Path,
    extensions: frozenset[str],
    excluded_directories: frozenset[str],
    excluded_filenames: frozenset[str] = DEFAULT_EXCLUDED_FILENAMES,
) -> Iterable[Path]:
    """Yield eligible files in a stable order without following symbolic links."""
    for root, directory_names, file_names in os.walk(directory):
        root_path = Path(root)
        directory_names[:] = sorted(
            name
            for name in directory_names
            if name not in excluded_directories and not (root_path / name).is_symlink()
        )
        for name in sorted(file_names):
            path = root_path / name
            if path.is_symlink() or name in excluded_filenames:
                continue
            if is_text_file(path, extensions):
                yield path


def read_text_file(path: Path, max_file_size: int) -> str | None:
    """Read UTF-8 text files, skipping binary or unusually large files."""
    if path.stat().st_size > max_file_size:
        return None

    contents = path.read_bytes()
    if b"\x00" in contents:
        return None

    try:
        return contents.decode("utf-8")
    except UnicodeDecodeError:
        return None


def build_clipboard_payload(
    directory: Path,
    extensions: frozenset[str] = DEFAULT_EXTENSIONS,
    excluded_directories: frozenset[str] = DEFAULT_EXCLUDED_DIRECTORIES,
    max_file_size: int = 1_000_000,
) -> tuple[str, int]:
    """Build a shareable text bundle using paths relative to *directory*."""
    sections = []
    copied_files = 0

    for path in iter_text_files(directory, extensions, excluded_directories):
        contents = read_text_file(path, max_file_size)
        if contents is None:
            continue

        relative_path = path.relative_to(directory).as_posix()
        sections.append(f"--- {relative_path} ---\n\n{contents.rstrip()}\n")
        copied_files += 1

    return "\n".join(sections), copied_files


def copy_directory_contents_to_clipboard(
    directory: Path,
    extensions: frozenset[str] = DEFAULT_EXTENSIONS,
    excluded_directories: frozenset[str] = DEFAULT_EXCLUDED_DIRECTORIES,
    max_file_size: int = 1_000_000,
) -> int:
    """Copy a directory's eligible source files and return the number copied."""
    payload, copied_files = build_clipboard_payload(
        directory, extensions, excluded_directories, max_file_size
    )
    if not payload:
        raise ValueError("No eligible text files were found.")

    try:
        import pyperclip

        pyperclip.copy(payload)
    except ImportError as error:
        raise RuntimeError("Clipboard support is unavailable. Install pyperclip first.") from error
    except pyperclip.PyperclipException as error:
        raise RuntimeError("No clipboard mechanism is available on this system.") from error

    return copied_files


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Copy selected text files from a directory to the clipboard."
    )
    parser.add_argument("directory", type=Path, help="Directory to collect from")
    parser.add_argument(
        "--include",
        action="append",
        default=[],
        metavar="EXTENSIONS",
        help="Comma-separated extensions to include instead of the defaults (for example: py,md)",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="DIRECTORY",
        help="Directory name to exclude; can be supplied more than once",
    )
    parser.add_argument(
        "--max-file-size",
        type=int,
        default=1_000_000,
        metavar="BYTES",
        help="Skip files larger than this value (default: 1000000)",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print the bundle instead of placing it on the clipboard",
    )
    args = parser.parse_args(argv)

    directory = args.directory.expanduser().resolve()
    if not directory.is_dir():
        parser.error(f"directory does not exist: {directory}")
    if args.max_file_size <= 0:
        parser.error("--max-file-size must be greater than zero")

    extensions = normalize_extensions(args.include) if args.include else DEFAULT_EXTENSIONS
    excluded_directories = DEFAULT_EXCLUDED_DIRECTORIES | frozenset(args.exclude)
    payload, copied_files = build_clipboard_payload(
        directory, extensions, excluded_directories, args.max_file_size
    )
    if not payload:
        parser.error("no eligible text files were found")

    if args.stdout:
        print(payload, end="")
        return 0

    try:
        import pyperclip

        pyperclip.copy(payload)
    except ImportError:
        parser.error("clipboard support is unavailable; install pyperclip or use --stdout")
    except pyperclip.PyperclipException:
        parser.error("no clipboard mechanism is available; use --stdout")

    print(f"Copied {copied_files} file{'s' if copied_files != 1 else ''} to the clipboard.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
