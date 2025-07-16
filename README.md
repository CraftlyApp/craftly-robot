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

    Craftly Robot operates based on a set of instructions described in a JSON file. A sample is in the [instructions](instructions) folder.

2.  **Run Craftly Robot**

    This command executes the instructions.

    ```bash
    python3 craftly_robot.py -i instructions/sample.json
    ```

    **Output on Success:**
    ```bash
    ✓ [1/11] created folder: my_project
    ✓ [2/11] created folder: trash_dir
    ✓ [3/11] deleted folder: trash_dir
    ✓ [4/11] created file: my_project/hello.py
    ✓ [5/11] added line: 1 #!/usr/bin/env python3
    ✓ [6/11] added line: 2 def main():
    ✓ [7/11] added line: 3 print("Hello, World!")
    ✓ [8/11] added line: 4 
    ✓ [9/11] added line: 5 if __name__ == "__main__":
    ✓ [10/11] added line: 6 main()
    ✓ [11/11] removed line: 4 
    ! To revert back, run: python3 craftly_robot.py -i instructions/sample.json --undo
    ```

---

## ⚙️ CLI Arguments

| Argument  | Alias | Required | Description                                |
| :-------- | :---- | :------- | :----------------------------------------- |
| `--input` | `-i`  | Yes      | Path to the JSON instruction file.         |
| `--undo`  |       | No       | Reverts the changes using the backup file. |

---

## 🔧 Instruction Schema

Each instruction is a single JSON object with the following keys:

| Key         | Type                          | Description                                                                                             |
| :---------- | :---------------------------- | :------------------------------------------------------------------------------------------------------ |
| `operation` | `string`                      | The action to perform: `create` or `delete`.                                                            |
| `mode`      | `string`                      | The target type: `folder`, `file`, or `line`.                                                           |
| `path`      | `array of strings`            | A list of one or more target paths for the operation.                                                   |
| `content`   | `dictionary` or `array` | Data for `line` operations (dictionary to create, array to delete). **Required only when `mode` is "line".** |

---

## ⚠️ Error Handling

*   Throws descriptive errors on:
    *   Missing parent directories
    *   Existing targets on `create`
    *   Non-empty folders on `delete_folder`
    *   Invalid line numbers
    *   JSON syntax issues
    
---

## 🤝 Contributing

Contributions, feedback, and bug reports are welcome! Please fork the repo and open a pull request.

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
