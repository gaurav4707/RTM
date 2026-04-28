"""
=============================================================================
REQUIREMENT TRACEABILITY MATRIX (RTM) TOOL
=============================================================================

ACADEMIC DISCLAIMER:
--------------------
This is a PROTOTYPE application developed for educational purposes.
The focus is on demonstrating:
  - Software Engineering principles (layered architecture)
  - Requirement traceability concepts
  - Basic CRUD operations with SQLite

This tool is NOT intended for enterprise or production use.
It prioritizes clarity and learning over scalability and performance.

PROJECT PURPOSE:
----------------
This application is a desktop-based Requirement Traceability Matrix (RTM) tool
designed to help software engineers track relationships between:
  - Software Requirements (Functional and Non-Functional)
  - Design Modules
  - Test Cases

The tool allows users to create trace links between requirements and their
corresponding design implementations and test cases, then view the complete
traceability matrix.

HOW TO RUN:
-----------
1. Ensure Python 3.x is installed on your system
2. Navigate to the rtm_tool directory in terminal/command prompt
3. Run: python main.py

The application will open a graphical window with tabs for managing
requirements, design modules, test cases, and viewing the traceability matrix.

FOLDER STRUCTURE:
-----------------
rtm_tool/
├── ui/
│   └── main_ui.py          # Tkinter-based graphical user interface
├── service/
│   └── trace_service.py    # Business logic and validation layer
├── data/
│   └── database.py         # SQLite database access layer
├── model/
│   ├── requirement.py      # Requirement data model
│   ├── design_module.py    # Design Module data model
│   └── test_case.py        # Test Case data model
├── tests/
│   └── test_traceability.py # Unit tests for the application
└── main.py                  # Application entry point (this file)

ARCHITECTURE:
-------------
This application follows a 3-layer architecture:
  1. UI Layer (ui/) - Handles user interaction via Tkinter
  2. Service Layer (service/) - Contains business logic and validation
  3. Data Layer (data/) - Manages SQLite database operations

Data flows from UI → Service → Data and back, ensuring separation of concerns.

DATABASE:
---------
The application uses SQLite for persistent storage. The database file
(rtm_database.db) is created automatically in the application directory.

RUNNING TESTS:
--------------
To run unit tests: python -m unittest tests.test_traceability -v

=============================================================================
"""

import sys
import os

# Add the parent directory to the path for proper module imports
# This ensures the package structure works correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from service.trace_service import TraceService
from ui.main_ui import create_app


def main():
    """
    Main entry point for the RTM Tool application.
    
    This function:
    1. Creates the TraceService instance (initializes database)
    2. Creates the main application window
    3. Starts the Tkinter event loop
    """
    # Print startup message to console
    print("=" * 60)
    print("  Requirement Traceability Matrix (RTM) Tool")
    print("  Starting application...")
    print("=" * 60)
    
    # Initialize the service layer (this also creates/connects to database)
    service = TraceService()
    
    # Create and configure the main application window
    root = create_app(service)
    
    # Print success message
    print("  Application started successfully!")
    print("  Close the window or press Ctrl+C to exit.")
    print("=" * 60)
    
    # Start the Tkinter event loop (runs until window is closed)
    root.mainloop()
    
    # Print exit message
    print("\nApplication closed. Goodbye!")


if __name__ == "__main__":
    # Execute main function when script is run directly
    main()
