# crepo

`crepo` gathers selected text files from a directory and places one clearly labelled bundle on the clipboard. It is useful when sharing a small, readable snapshot of source code without manually opening each file.

## Highlights

- Uses relative paths, so bundles do not expose machine-specific directory names.
- Produces files in a stable order for consistent output.
- Skips common generated folders, symbolic links, binary files, large files, and likely credential files.
- Supports a terminal-only `--stdout` mode for review and automation.

## Install

Requires Python 3.9 or later.

```bash
python -m pip install .
```

## Usage

Copy the default source-file set from the current project:

```bash
crepo .
```

Review a Python and Markdown bundle in the terminal instead of using the clipboard:

```bash
crepo . --include py,md --stdout
```

Exclude an additional directory or reduce the size limit for each file:

```bash
crepo . --exclude fixtures --max-file-size 200000
```

The default file types include common source, markup, data, and configuration formats. Supplying `--include` replaces that default set. The tool always excludes common build and dependency folders, including `.git`, `node_modules`, virtual environments, `build`, and `dist`.

## Development

Run the test suite with the Python standard library:

```bash
python -m unittest discover -s tests -v
```

## License

Released under the [MIT License](LICENSE).
