---

# Craftly Robot

Craftly Robot is a lightweight command-line tool for managing codebases at scale. Need to set up project structure, or edit and modify files in a large codebase? Just describe it in a JSON file, and let Craftly Robot handle it for you.

---

## 📦 Installation

1.  **Clone the repository**

    ```bash
    git clone https://github.com/craftlyapp/craftly-robot.git
    cd craftly-robot
    ```
2.  **Ensure you have Python 3.6+**

    ```bash
    python3 --version
    ```

---

## 🚀 Quick Start

1.  **Prepare an instruction JSON**

    Craftly Robot operates based on a list of atomic instructions described in a JSON file. A sample is in the `instructions/` folder.

2.  **Run Craftly Robot**

    This command executes the instructions. On every run, it creates a hidden backup file of the completed steps.

    ```bash
    python3 craftly_robot.py -i instructions/sample.json
    ```

    **Output on Success:**
    ```bash
    ✓ [1/3] created folder: my_project
    ✓ [2/3] created file: my_project/hello.txt
    ✓ [3/3] added line: 1 Hello, Craftly Robot!
    ! To revert back, run: python3 craftly_robot.py -i instructions/sample.json --undo
    ```

3.  **Handling Failures**

    If an instruction fails, the robot stops and shows you exactly where the error occurred. It still creates a backup of the steps that succeeded, so you can easily clean up.

    **Output on Failure:**
    ```bash
    ✓ [1/3] created folder: my_project
    ✗ [2/3] Missing parent folder: non_existent_dir
    ! To revert back, run: python3 craftly_robot.py -i instructions/sample.json --undo
    ```

4.  **Undo the Changes**

    Whether the run was a full success or a partial failure, you can always revert the changes with the `--undo` flag.

    ```bash
    python3 craftly_robot.py -i instructions/sample.json --undo
    ```

---

## ⚙️ CLI Arguments

| Argument  | Alias | Required | Description                                |
| :-------- | :---- | :------- | :----------------------------------------- |
| `--input` | `-i`  | Yes      | Path to the JSON instruction file.         |
| `--undo`  |       | No       | Reverts the changes using the backup file. |

---

## 🛡️ Backup and Undo Feature

Craftly Robot is built to be safe and easily reversible.

*   **Automatic Backups**: The robot automatically creates a backup of all **completed** actions on every run. This allows you to undo the changes whether the entire run succeeded or failed midway.
*   **Hidden Backup Directory**: Backups are stored in a hidden `.backup/` directory. For an input file like `instructions/sample.json`, the backup will be saved as `.backup/sample.bak`.
*   **Reverting Changes**: The `--undo` flag reads the corresponding `.bak` file, executes the reverse actions, and restores your files to their previous state. After a successful undo, the backup file is automatically deleted.

---

## 🔧 Instruction Schema

Each instruction object must include three keys:

| Key         | Type     | Description                                  |
| :---------- | :------- | :------------------------------------------- |
| `operation` | `string` | The action to perform: `create` or `delete`. |
| `mode`      | `string` | The target type: `folder`, `file`, or `line`. |
| `path`      | `string` | The filesystem path for the operation.       |

**For line operations**, include these additional keys:

| Key       | Type     | Description                                           |
| :-------- | :------- | :---------------------------------------------------- |
| `line`    | `number` | The 1-based line number to insert or delete.          |
| `content` | `string` | *(Only for `create`)* The text to insert at the line. |

---

## ✅ Supported Operations

*   **Folder**
    *   `create_folder`: Requires the parent folder to exist.
    *   `delete_folder`: Only deletes empty directories.
*   **File**
    *   `create_file`: Requires the parent folder to exist.
    *   `delete_file`: Removes an existing file.
*   **Line** (inside text files)
    *   `create_line`: Inserts a new line of content.
    *   `delete_line`: Removes a specific line.

---

## ⚠️ Error Handling

*   Throws descriptive errors on:
    *   Missing parent directories
    *   Existing targets on `create`
    *   Non-empty folders on `delete_folder`
    *   Invalid line numbers
    *   JSON syntax issues
*   When an error occurs, the robot stops immediately after printing the error. It saves a backup of any steps that succeeded, allowing you to revert the partial changes easily.

---

## 🤝 Contributing

Contributions, feedback, and bug reports are welcome! Please fork the repo and open a pull request.

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
