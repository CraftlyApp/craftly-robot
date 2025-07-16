import argparse
import json
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Operate on one or more atomic file/folder/line instructions in JSON"
    )
    parser.add_argument(
        '-i', '--input', required=True,
        help='Path to the JSON file containing one or more instructions'
    )
    return parser.parse_args()


class FileOperator:
    """Performs atomic create/delete operations on files, folders, and lines."""

    def __init__(self, action: dict):
        self.action = action
        self.path = Path(action['path'])
        self.mode = action['mode']
        self.op = action['operation']

    def run(self):
        method = getattr(self, f"{self.op}_{self.mode}", None)
        if not method:
            raise ValueError(f"Unsupported operation: {self.op} {self.mode}")
        return method()

    # Folder ops
    def create_folder(self):
        if self.path.exists():
            raise FileExistsError(f"Folder exists: {self.path}")
        if not self.path.parent.exists():
            raise FileNotFoundError(f"Missing parent folder: {self.path.parent}")
        self.path.mkdir()
        return f"created folder: {self.path}"

    def delete_folder(self):
        if not self.path.is_dir():
            raise FileNotFoundError(f"No folder: {self.path}")
        if any(self.path.iterdir()):
            raise OSError(f"Folder not empty: {self.path}")
        self.path.rmdir()
        return f"deleted folder: {self.path}"

    # File ops
    def create_file(self):
        if self.path.exists():
            raise FileExistsError(f"File exists: {self.path}")
        parent = self.path.parent
        if not parent.exists():
            raise FileNotFoundError(f"Missing parent folder: {parent}")
        self.path.touch()
        return f"created file: {self.path}"

    def delete_file(self):
        if not self.path.is_file():
            raise FileNotFoundError(f"No file: {self.path}")
        self.path.unlink()
        return f"deleted file: {self.path}"

    # Line ops
    def create_line(self):
        line_no = self.action['line']
        content = self.action.get('content', '') + '\n'
        lines = self._read_lines()
        if not (1 <= line_no <= len(lines) + 1):
            raise IndexError(f"Invalid line: {line_no}")
        lines.insert(line_no - 1, content)
        self._write_lines(lines)
        return f"added line: {line_no} {content.strip()}"

    def delete_line(self):
        line_no = self.action['line']
        lines = self._read_lines()
        if not (1 <= line_no <= len(lines)):
            raise IndexError(f"Invalid line: {line_no}")
        removed = lines.pop(line_no - 1).rstrip()
        self._write_lines(lines)
        return f"removed line: {line_no} {removed}"

    # Internal helpers
    def _read_lines(self):
        if not self.path.exists():
            raise FileNotFoundError(f"File not found: {self.path}")
        return self.path.read_text().splitlines(keepends=True)

    def _write_lines(self, lines):
        self.path.write_text(''.join(lines))


def main():
    args = parse_args()

    try:
        raw = Path(args.input).read_text()
    except Exception as e:
        print(f"✗ Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"✗ JSON syntax error: {e}", file=sys.stderr)
        sys.exit(1)

    # Normalize to list of instructions
    instructions = data if isinstance(data, list) else [data]

    # Execute each instruction sequentially
    for idx, instr in enumerate(instructions, start=1):
        try:
            result = FileOperator(instr).run()
            print(f"✓ [{idx}/{len(instructions)}] {result}")
        except Exception as e:
            print(f"✗ [{idx}/{len(instructions)}] {e}", file=sys.stderr)
            sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()

