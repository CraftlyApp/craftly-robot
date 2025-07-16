# filename: craftly_robot.py
import argparse
import json
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple, Callable, Iterator

BACKUP_DIR = Path('.backup')

def parse_args():
    parser = argparse.ArgumentParser(
        description="A reversible file and code operator."
    )
    parser.add_argument(
        '-i', '--input', required=True,
        help='Path to the JSON file containing one or more instructions'
    )
    parser.add_argument(
        '--undo', action='store_true',
        help='Revert the actions specified in the input file using its backup'
    )
    return parser.parse_args()

@dataclass
class FileOperator:
    action: Dict[str, Any]

    def __post_init__(self):
        self.op: str = self.action['operation']
        self.mode: str = self.action['mode']
        self.path: Path = Path(self.action['path'])
        self.OPERATIONS: Dict[Tuple[str, str], Callable] = {
            ('create', 'folder'): self._create_folder,
            ('delete', 'folder'): self._delete_folder,
            ('create', 'file'): self._create_file,
            ('delete', 'file'): self._delete_file,
            ('create', 'line'): self._create_line,
            ('delete', 'line'): self._delete_line,
        }

    def run(self) -> Tuple[str, Dict[str, Any]]:
        method = self.OPERATIONS.get((self.op, self.mode))
        if not method:
            raise ValueError(f"Unsupported operation: {self.op} {self.mode}")
        return method()

    def _create_folder(self) -> Tuple[str, dict]:
        if not self.path.parent.exists():
            raise FileNotFoundError(f"Missing parent folder: {self.path.parent}")
        self.path.mkdir(exist_ok=False)
        reverse = {'operation': 'delete', 'mode': 'folder', 'path': str(self.path)}
        return f"created folder: {self.path}", reverse

    def _delete_folder(self) -> Tuple[str, dict]:
        if not self.path.is_dir():
            raise FileNotFoundError(f"No such folder: {self.path}")
        if any(self.path.iterdir()):
            raise OSError(f"Folder not empty: {self.path}")
        self.path.rmdir()
        reverse = {'operation': 'create', 'mode': 'folder', 'path': str(self.path)}
        return f"deleted folder: {self.path}", reverse

    def _create_file(self) -> Tuple[str, dict]:
        if not self.path.parent.exists():
            raise FileNotFoundError(f"Missing parent folder: {self.path.parent}")
        content_for_undo = self.action.get('content')
        self.path.touch(exist_ok=False)
        message = f"created file: {self.path}"
        if content_for_undo is not None:
            self.path.write_text(content_for_undo)
            # The message for creating a file is always the same for consistency.
            # The 'content' is an internal detail for the undo system.
        reverse = {'operation': 'delete', 'mode': 'file', 'path': str(self.path)}
        return message, reverse

    def _delete_file(self) -> Tuple[str, dict]:
        if not self.path.is_file():
            raise FileNotFoundError(f"No such file: {self.path}")
        content = self.path.read_text()
        self.path.unlink()
        reverse = {'operation': 'create', 'mode': 'file', 'path': str(self.path), 'content': content}
        return f"deleted file: {self.path}", reverse

    def _create_line(self) -> Tuple[str, dict]:
        line_no = self.action['line']
        content = self.action.get('content', '') + '\n'
        lines = self._read_lines()
        if not (1 <= line_no <= len(lines) + 1):
            raise IndexError(f"Invalid line number: {line_no} for file {self.path}")
        lines.insert(line_no - 1, content)
        self._write_lines(lines)
        reverse = {'operation': 'delete', 'mode': 'line', 'path': str(self.path), 'line': line_no}
        return f"added line: {line_no} {content.strip()}", reverse

    def _delete_line(self) -> Tuple[str, dict]:
        line_no = self.action['line']
        lines = self._read_lines()
        if not (1 <= line_no <= len(lines)):
            raise IndexError(f"Invalid line number: {line_no} for file {self.path}")
        removed_content = lines.pop(line_no - 1)
        self._write_lines(lines)
        reverse = {'operation': 'create', 'mode': 'line', 'path': str(self.path), 'line': line_no, 'content': removed_content.rstrip('\n')}
        return f"removed line: {line_no} {removed_content.strip()}", reverse

    def _read_lines(self) -> List[str]:
        if not self.path.is_file():
            raise FileNotFoundError(f"File not found: {self.path}")
        return self.path.read_text().splitlines(keepends=True)

    def _write_lines(self, lines: List[str]):
        self.path.write_text(''.join(lines))

def save_backup(backup_file: Path, reverse_actions: List[dict]):
    if not reverse_actions:
        return
    BACKUP_DIR.mkdir(exist_ok=True)
    reverse_actions.reverse()
    backup_file.write_text(json.dumps(reverse_actions, indent=4))

def expand_instructions(raw_instructions: List[dict]) -> Iterator[dict]:
    for instr in raw_instructions:
        op = instr['operation']
        mode = instr['mode']
        if 'path' not in instr:
            raise KeyError(f"Instruction is missing required 'path' key.")
        for p in instr['path']:
            if mode in ['file', 'folder']:
                yield {'operation': op, 'mode': mode, 'path': p}
            elif mode == 'line':
                content_data = instr.get('content', {})
                if op == 'create':
                    sorted_items = sorted(content_data.items(), key=lambda item: int(item[0]))
                    for line_num_str, content_str in sorted_items:
                        yield {'operation': op, 'mode': mode, 'path': p, 'line': int(line_num_str), 'content': content_str}
                elif op == 'delete':
                    sorted_lines = sorted(content_data, reverse=True)
                    for line_num in sorted_lines:
                        yield {'operation': op, 'mode': mode, 'path': p, 'line': line_num}

def main():
    args = parse_args()
    input_path = Path(args.input)
    backup_file = BACKUP_DIR / input_path.with_suffix('.bak').name

    if args.undo:
        if not backup_file.exists():
            print(f"✗ No backup file found at: {backup_file}", file=sys.stderr)
            sys.exit(1)
        try:
            instructions_to_undo = json.loads(backup_file.read_text())
            for idx, instr in enumerate(instructions_to_undo, 1):
                result, _ = FileOperator(instr).run()
                print(f"✓ [{idx}/{len(instructions_to_undo)}] UNDO: {result}")
            backup_file.unlink()
            sys.exit(0)
        except Exception as e:
            print(f"✗ [{idx}/{len(instructions_to_undo)}] FATAL: Undo operation failed: {e}", file=sys.stderr)
            sys.exit(1)

    try:
        raw_instructions = json.loads(input_path.read_text())
    except FileNotFoundError:
        print(f"✗ Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"✗ JSON syntax error in {input_path}: {e}", file=sys.stderr)
        sys.exit(1)
    
    raw_list = raw_instructions if isinstance(raw_instructions, list) else [raw_instructions]
    instructions = list(expand_instructions(raw_list))
    
    if not instructions:
        sys.exit(0)

    completed_reverse_actions = []
    was_successful = True
    for idx, instr in enumerate(instructions, 1):
        try:
            result, reverse_action = FileOperator(instr).run()
            print(f"✓ [{idx}/{len(instructions)}] {result}")
            completed_reverse_actions.append(reverse_action)
        except Exception as e:
            print(f"✗ [{idx}/{len(instructions)}] {e}", file=sys.stderr)
            was_successful = False
            break
    
    save_backup(backup_file, completed_reverse_actions)
    if completed_reverse_actions:
        print(f"! To revert back, run: python3 {Path(sys.argv[0]).name} -i {args.input} --undo", file=sys.stderr)
    
    if not was_successful:
        sys.exit(1)
    sys.exit(0)

if __name__ == '__main__':
    main()
