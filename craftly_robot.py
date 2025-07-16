import argparse
import json
import sys
from pathlib import Path

# --- Constants ---
BACKUP_DIR = Path('.backup')

def parse_args():
    """Parses command-line arguments."""
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


class FileOperator:
    """Performs atomic create/delete operations on files, folders, and lines."""

    def __init__(self, action: dict):
        self.action = action
        self.path = Path(action['path'])
        self.mode = action['mode']
        self.op = action['operation']

    def run(self):
        """
        Executes the specified operation and returns a tuple containing:
        (success_message, reverse_action_dictionary)
        """
        method = getattr(self, f"{self.op}_{self.mode}", None)
        if not method:
            raise ValueError(f"Unsupported operation: {self.op} {self.mode}")
        return method()

    # --- Folder ops ---
    def create_folder(self):
        if self.path.exists():
            raise FileExistsError(f"Folder exists: {self.path}")
        if not self.path.parent.exists():
            raise FileNotFoundError(f"Missing parent folder: {self.path.parent}")
        
        reverse_action = {'operation': 'delete', 'mode': 'folder', 'path': str(self.path)}
        self.path.mkdir()
        result_msg = f"created folder: {self.path}"
        return result_msg, reverse_action

    def delete_folder(self):
        if not self.path.is_dir():
            raise FileNotFoundError(f"No folder: {self.path}")
        if any(self.path.iterdir()):
            raise OSError(f"Folder not empty: {self.path}")

        reverse_action = {'operation': 'create', 'mode': 'folder', 'path': str(self.path)}
        self.path.rmdir()
        result_msg = f"deleted folder: {self.path}"
        return result_msg, reverse_action

    # --- File ops ---
    def create_file(self):
        if self.path.exists():
            raise FileExistsError(f"File exists: {self.path}")
        parent = self.path.parent
        if not parent.exists():
            raise FileNotFoundError(f"Missing parent folder: {parent}")

        reverse_action = {'operation': 'delete', 'mode': 'file', 'path': str(self.path)}
        content_to_write = self.action.get('content')
        if content_to_write is not None:
            self.path.write_text(content_to_write)
        else:
            self.path.touch()
        result_msg = f"created file: {self.path}"
        return result_msg, reverse_action

    def delete_file(self):
        if not self.path.is_file():
            raise FileNotFoundError(f"No file: {self.path}")

        file_content = self.path.read_text()
        reverse_action = {'operation': 'create', 'mode': 'file', 'path': str(self.path), 'content': file_content}
        self.path.unlink()
        result_msg = f"deleted file: {self.path}"
        return result_msg, reverse_action

    # --- Line ops ---
    def create_line(self):
        line_no = self.action['line']
        content = self.action.get('content', '') + '\n'
        lines = self._read_lines()
        if not (1 <= line_no <= len(lines) + 1):
            raise IndexError(f"Invalid line number: {line_no} for file {self.path}")
        
        reverse_action = {'operation': 'delete', 'mode': 'line', 'path': str(self.path), 'line': line_no}
        lines.insert(line_no - 1, content)
        self._write_lines(lines)
        result_msg = f"added line: {line_no} {content.strip()}"
        return result_msg, reverse_action

    def delete_line(self):
        line_no = self.action['line']
        lines = self._read_lines()
        if not (1 <= line_no <= len(lines)):
            raise IndexError(f"Invalid line number: {line_no} for file {self.path}")
        
        removed_line_content = lines[line_no - 1].rstrip('\n')
        reverse_action = {'operation': 'create', 'mode': 'line', 'path': str(self.path), 'line': line_no, 'content': removed_line_content}
        removed = lines.pop(line_no - 1).rstrip()
        self._write_lines(lines)
        result_msg = f"removed line: {line_no} {removed}"
        return result_msg, reverse_action

    # --- Internal helpers ---
    def _read_lines(self):
        if not self.path.is_file():
            raise FileNotFoundError(f"File not found: {self.path}")
        return self.path.read_text().splitlines(keepends=True)

    def _write_lines(self, lines):
        self.path.write_text(''.join(lines))


def save_backup(backup_file: Path, reverse_actions: list):
    """Saves the list of reverse actions to a backup file."""
    if not reverse_actions:
        return
    
    BACKUP_DIR.mkdir(exist_ok=True)
    reverse_actions.reverse()
    backup_file.write_text(json.dumps(reverse_actions, indent=4))

def main():
    args = parse_args()
    input_path = Path(args.input)
    backup_file = BACKUP_DIR / input_path.with_suffix('.bak').name

    # --- UNDO LOGIC ---
    if args.undo:
        if not backup_file.exists():
            print(f"✗ No backup file found at: {backup_file}", file=sys.stderr)
            sys.exit(1)
        
        try:
            instructions_to_undo = json.loads(backup_file.read_text())
        except Exception as e:
            print(f"✗ Error reading or parsing backup file {backup_file}: {e}", file=sys.stderr)
            sys.exit(1)
        
        for idx, instr in enumerate(instructions_to_undo, start=1):
            try:
                result, _ = FileOperator(instr).run()
                print(f"✓ [{idx}/{len(instructions_to_undo)}] UNDO: {result}")
            except Exception as e:
                print(f"✗ [{idx}/{len(instructions_to_undo)}] FATAL: Undo operation failed: {e}", file=sys.stderr)
                sys.exit(1)
        
        backup_file.unlink()
        sys.exit(0)

    # --- NORMAL EXECUTION LOGIC ---
    try:
        raw_instructions = input_path.read_text()
        instructions = json.loads(raw_instructions)
    except FileNotFoundError:
        print(f"✗ Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"✗ JSON syntax error in {input_path}: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(instructions, list):
        instructions = [instructions]
        
    completed_reverse_actions = []
    was_successful = True
    
    for idx, instr in enumerate(instructions, start=1):
        try:
            result, reverse_action = FileOperator(instr).run()
            print(f"✓ [{idx}/{len(instructions)}] {result}")
            completed_reverse_actions.append(reverse_action)
        except Exception as e:
            # THIS IS THE CORRECTED PART: Print the error and then stop.
            print(f"✗ [{idx}/{len(instructions)}] {e}", file=sys.stderr)
            was_successful = False
            break # Stop processing any more instructions
    
    # After the loop (whether it finished or broke), save a backup of what was done.
    save_backup(backup_file, completed_reverse_actions)
    
    # If any actions were completed (even on a partial failure), show the revert tip.
    if completed_reverse_actions:
        print(f"! To revert back, run: python3 craftly_robot.py -i {args.input} --undo", file=sys.stderr)
    
    if not was_successful:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == '__main__':
    main()
