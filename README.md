# Craftly Robot

Craftly Robot is a lightweight command-line tool for managing codebases at scale. Need to set up project structure, edit or modify files in a large codebase? Just describe it in an instructions.json, and let Craftly Robot handle it for you.

---

## 📦 Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/craftlyapp/craftly-robot.git
   cd craftly-robot
   ```
2. **Ensure you have Python 3.6+**

   ```bash
   python3 --version
   ```

---

## 🚀 Quick Start

1. **Prepare an instruction JSON**

   Craftly Robot operates based on a list of atomic instructions described in a JSON file.
   A sample file is already available in the `instructions/` folder.

2. **Run Craftly Robot**

   ```bash
   python3 craftly_robot.py -i instructions/sample.json
   ```

3. **Observe the output**

   ```bash
   ✓ [1/3] Created folder: my_project
   ✓ [2/3] Created file: my_project/hello.txt
   ✓ [3/3] added line: 1 Hello, Craftly Robot!
   ```

---
## 🔧 Instruction Schema

Each instruction object must include three keys:

| Key         | Type     | Description                                        |
| ----------- | -------- | -------------------------------------------------- |
| `operation` | `string` | The action to perform: `create` or `delete`.       |
| `mode`      | `string` | The target type: `folder`, `file`, or `line`.      |
| `path`      | `string` | The filesystem path for folder or file operations. |

**For line operations** (inserting or deleting lines within a file), include:

| Key       | Type     | Description                                           |
| --------- | -------- | ----------------------------------------------------- |
| `line`    | `number` | The 1-based line number to insert or delete.          |
| `content` | `string` | *(Only for creation)* The text to insert at the line. |

---

## ✅ Supported Operations

* **Folder**

  * `create_folder`: Requires the parent folder to exist.
  * `delete_folder`: Only deletes empty directories.

* **File**

  * `create_file`: Requires the parent folder to exist.
  * `delete_file`: Removes an existing file.

* **Line** (inside text files)

  * `create_line`: Inserts a new line of content.
  * `delete_line`: Removes a specific line.

---

## ⚠️ Error Handling

* Throws descriptive errors on:

  * Missing parent directories
  * Existing targets on `create`
  * Non-empty folders on `delete_folder`
  * Invalid line numbers in text files
  * JSON syntax issues

On encountering an error, Craftly Robot prints a failure message and exits immediately.

---

## 🤝 Contributing

Contributions, feedback, and bug reports are welcome! Please fork the repo and open a pull request.

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
