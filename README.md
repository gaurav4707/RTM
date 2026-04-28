<h1 align="center">📊 RTM Tool</h1>

<p align="center"><i>A lightweight desktop Requirement Traceability Matrix application for software engineering</i></p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8%2B-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/UI-Tkinter-green.svg" alt="Tkinter UI">
  <img src="https://img.shields.io/badge/database-SQLite-lightgrey.svg" alt="SQLite Database">
  <img src="https://img.shields.io/badge/architecture-3--layer-orange.svg" alt="3-Layer Architecture">
</p>

---

## 🚀 Overview

The RTM Tool is a prototype desktop application designed to manage software engineering requirements, synchronize them with design modules, and link them to test cases. It solves the complex problem of tracking requirement coverage by automatically generating a bidirectional Requirement Traceability Matrix (RTM). Built with a clean 3-layer architecture, it ensures that no requirement is overlooked during the design and testing phases while serving as a robust reference for learning desktop application design.

---

## ✨ Key Highlights

- **Full Traceability**: Link requirements to both design modules and test cases seamlessly across a unified matrix.
- **Relational Integrity**: Built-in SQLite database mapped with cascading deletes to prevent orphaned records.
- **Clean Architecture**: Strict separation of concerns enforcing UI, business logic (Service), and Data layers.
- **Zero Dependencies**: Relies entirely on the Python standard library, requiring no external package managers or virtual environments.

---

## 📋 Features

### Frontend Features
- 📝 **Tabbed Navigation**: Dedicated, intuitive workspaces for Requirements, Design Modules, Test Cases, and Traceability mapping.
- 🔄 **Real-Time Matrix View**: Instantly visualize mapped relationships and coverage gaps in a consolidated data grid.
- 🛡️ **Graceful Error Handling**: User-friendly popups and descriptive validation messages instead of hard process crashes.

### Backend Features
- 🗄️ **Relational Persistence**: Automatic local database generation (`rtm_database.db`) utilizing junction tables for many-to-many relationships.
- 🧠 **Service Validation**: Business logic layer enforces unique constraints and validates record existence prior to linking.
- 🗑️ **Cascading Operations**: Deleting a root requirement automatically severs associated trace links at the database level.

---

## 🛠️ Tech Stack

### Frontend
- **[Tkinter](https://docs.python.org/3/library/tkinter.html)**: Standard GUI library for a native desktop experience

### Backend
- **[Python 3.x](https://www.python.org/)**: Core application logic and execution
- **[SQLite3](https://docs.python.org/3/library/sqlite3.html)**: Embedded relational database engine

### DevOps / Tools
- **[Unittest](https://docs.python.org/3/library/unittest.html)**: Built-in Python testing framework for business logic validation

---

## 📦 Installation

### Prerequisites
- **Python 3.8+** installed on your system
- **Tkinter** support enabled (included by default with standard Python installations)

### Setup Steps
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd rtm_tool
   ```
2. **Install dependencies**:
   *(No external dependencies required. All modules are part of the Python standard library.)*
3. **Setup environment variables**:
   Create a `.env` file in the project root (optional, for future extensibility):
   ```env
   APP_ENV=development
   DB_PATH=rtm_database.db
   ```
4. **Run the project locally**:
   Ensure you are in the project root directory so the database initializes correctly:
   ```bash
   python main.py
   ```

---

## 📖 Usage Guide

**Step 1: Populate Entities**
1. Navigate to the `Requirements` tab. Enter a unique ID (e.g., `REQ-01`) and a description, then click Add.
2. Repeat this process in the `Design Modules` and `Test Cases` tabs to build your project inventory.

**Step 2: Establish Traceability Links**
1. Switch to the `Traceability` tab.
2. Link a Requirement to a Design Module by entering their respective IDs and clicking **Link Requirement to Design**.
3. Link a Requirement to a Test Case by entering the IDs and clicking **Link Requirement to Test**.

**Step 3: Analyze Coverage**
1. Switch back to the matrix view to inspect generated traceability links.
2. Review linked IDs to verify each requirement is connected to design and testing artifacts.

---

## 📁 Project Structure

```text
rtm_tool/
├── main.py                  # Application entry point
├── ui/
│   └── main_ui.py           # Tkinter GUI, tabs, and event bindings
├── service/
│   └── trace_service.py     # Business logic, validation, and link management
├── data/
│   └── database.py          # SQLite schema, queries, and junction tables
├── model/
│   ├── requirement.py       # Requirement data class
│   ├── design_module.py     # Design module data class
│   └── test_case.py         # Test case data class
└── tests/
    └── test_traceability.py # Automated unit tests for central logic
```

---

## 🧪 Development

**Run Tests**
Execute the test suite to verify core traceability operations:
```bash
python -m unittest tests.test_traceability -v
```

**Build Project**
No separate build step is required for this Python desktop application.

**Local Development Notes**
- Always run `main.py` from the workspace root. Running from a subdirectory will create a separate DB file.
- The `tests` module validates `trace_service.py` behavior against SQLite-backed data operations.

**Docker**
Docker support is not currently configured for this prototype.

---

## 📄 License

This project is open-source and available under the MIT License.
