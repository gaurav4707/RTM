"""
Main UI Module (Presentation Layer)

This module contains the Tkinter-based graphical user interface
for the Requirement Traceability Matrix (RTM) Tool.

The UI uses a tabbed interface with four tabs:
1. Requirements - Add and view software requirements
2. Design Modules - Add and view design modules
3. Test Cases - Add and view test cases
4. Traceability Matrix - View the complete RTM and create mappings

ARCHITECTURE NOTE:
------------------
This is the UI LAYER (Presentation Layer) in our 3-tier architecture:
  UI Layer (this file) -> Service Layer -> Data Layer

This layer is responsible ONLY for:
  - Collecting user input from forms
  - Displaying data in tables/lists
  - Showing success/error messages to the user
  - Calling service layer methods

This layer does NOT:
  - Validate business rules (that's the service layer's job)
  - Access the database directly (that's the data layer's job)
  - Contain business logic
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
import sys
import os

# Add parent directory to path for imports when running as script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from service.trace_service import TraceService


class RTMApplication:
    """
    Main application class for the RTM Tool GUI.
    
    This class creates and manages the main window and all tabs
    of the application.
    
    Attributes:
        root (tk.Tk): The main Tkinter window
        service (TraceService): Business logic service instance
    """
    
    def __init__(self, root: tk.Tk, service: TraceService):
        """
        Initialize the RTM application.
        
        Args:
            root: The main Tkinter window
            service: TraceService instance for business logic
        """
        self.root = root
        self.service = service
        
        # Configure the main window
        self._setup_main_window()
        
        # Create the tabbed interface
        self._create_notebook()
        
        # Create each tab
        self._create_requirements_tab()
        self._create_design_modules_tab()
        self._create_test_cases_tab()
        self._create_traceability_tab()
    
    def _setup_main_window(self) -> None:
        """Configure the main application window."""
        self.root.title("Requirement Traceability Matrix Tool")
        self.root.geometry("900x600")
        self.root.resizable(False, False)
        
        # Configure style for consistent look
        style = ttk.Style()
        style.configure('TLabel', font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10))
        style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'))
    
    def _create_notebook(self) -> None:
        """Create the tabbed notebook interface."""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
    
    # ==================== REQUIREMENTS TAB ====================
    
    def _create_requirements_tab(self) -> None:
        """Create the Requirements tab with input form and list view."""
        # Create the tab frame
        self.req_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.req_tab, text='Requirements')
        
        # ----- Input Form Section -----
        form_frame = ttk.LabelFrame(self.req_tab, text="Add New Requirement", padding=10)
        form_frame.pack(fill='x', pady=(0, 10))
        
        # Requirement ID
        ttk.Label(form_frame, text="Requirement ID:").grid(row=0, column=0, sticky='w', pady=5)
        self.req_id_entry = ttk.Entry(form_frame, width=30)
        self.req_id_entry.grid(row=0, column=1, sticky='w', padx=(10, 20), pady=5)
        
        # Requirement Type
        ttk.Label(form_frame, text="Type:").grid(row=0, column=2, sticky='w', pady=5)
        self.req_type_var = tk.StringVar(value="Functional")
        self.req_type_combo = ttk.Combobox(
            form_frame, 
            textvariable=self.req_type_var,
            values=["Functional", "Non-Functional"],
            state="readonly",
            width=15
        )
        self.req_type_combo.grid(row=0, column=3, sticky='w', padx=10, pady=5)
        
        # Description
        ttk.Label(form_frame, text="Description:").grid(row=1, column=0, sticky='nw', pady=5)
        self.req_desc_text = tk.Text(form_frame, height=3, width=60)
        self.req_desc_text.grid(row=1, column=1, columnspan=3, sticky='w', padx=(10, 0), pady=5)
        
        # Add Button
        self.add_req_btn = ttk.Button(form_frame, text="Add Requirement", command=self._add_requirement)
        self.add_req_btn.grid(row=2, column=1, sticky='w', padx=(10, 0), pady=10)
        
        # ----- Table Section -----
        table_frame = ttk.LabelFrame(self.req_tab, text="Existing Requirements", padding=10)
        table_frame.pack(fill='both', expand=True)
        
        # Create Treeview for displaying requirements
        columns = ('ID', 'Description', 'Type')
        self.req_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=12)
        
        # Define column headings and widths
        self.req_tree.heading('ID', text='Requirement ID')
        self.req_tree.heading('Description', text='Description')
        self.req_tree.heading('Type', text='Type')
        
        self.req_tree.column('ID', width=120, minwidth=100)
        self.req_tree.column('Description', width=500, minwidth=300)
        self.req_tree.column('Type', width=120, minwidth=100)
        
        # Add scrollbar
        req_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.req_tree.yview)
        self.req_tree.configure(yscrollcommand=req_scrollbar.set)
        
        self.req_tree.pack(side='left', fill='both', expand=True)
        req_scrollbar.pack(side='right', fill='y')
        
        # Load existing data
        self._refresh_requirements_list()
    
    def _add_requirement(self) -> None:
        """Handle adding a new requirement."""
        # Get values from form
        req_id = self.req_id_entry.get().strip()
        req_type = self.req_type_var.get()
        description = self.req_desc_text.get("1.0", tk.END).strip()
        
        # Call service to add requirement
        success, message = self.service.add_requirement(req_id, description, req_type)
        
        if success:
            messagebox.showinfo("Success", message)
            # Clear the form
            self.req_id_entry.delete(0, tk.END)
            self.req_desc_text.delete("1.0", tk.END)
            # Refresh the list
            self._refresh_requirements_list()
            # Refresh dropdowns in traceability tab
            self._refresh_traceability_dropdowns()
        else:
            messagebox.showerror("Error", message)
    
    def _refresh_requirements_list(self) -> None:
        """Refresh the requirements table with current data."""
        # Clear existing items
        for item in self.req_tree.get_children():
            self.req_tree.delete(item)
        
        # Get and display all requirements
        requirements = self.service.get_all_requirements()
        for req in requirements:
            self.req_tree.insert('', tk.END, values=req)
    
    # ==================== DESIGN MODULES TAB ====================
    
    def _create_design_modules_tab(self) -> None:
        """Create the Design Modules tab with input form and list view."""
        # Create the tab frame
        self.dm_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.dm_tab, text='Design Modules')
        
        # ----- Input Form Section -----
        form_frame = ttk.LabelFrame(self.dm_tab, text="Add New Design Module", padding=10)
        form_frame.pack(fill='x', pady=(0, 10))
        
        # Module ID
        ttk.Label(form_frame, text="Module ID:").grid(row=0, column=0, sticky='w', pady=5)
        self.dm_id_entry = ttk.Entry(form_frame, width=30)
        self.dm_id_entry.grid(row=0, column=1, sticky='w', padx=(10, 20), pady=5)
        
        # Module Name
        ttk.Label(form_frame, text="Name:").grid(row=0, column=2, sticky='w', pady=5)
        self.dm_name_entry = ttk.Entry(form_frame, width=30)
        self.dm_name_entry.grid(row=0, column=3, sticky='w', padx=10, pady=5)
        
        # Description
        ttk.Label(form_frame, text="Description:").grid(row=1, column=0, sticky='nw', pady=5)
        self.dm_desc_text = tk.Text(form_frame, height=3, width=60)
        self.dm_desc_text.grid(row=1, column=1, columnspan=3, sticky='w', padx=(10, 0), pady=5)
        
        # Add Button
        self.add_dm_btn = ttk.Button(form_frame, text="Add Design Module", command=self._add_design_module)
        self.add_dm_btn.grid(row=2, column=1, sticky='w', padx=(10, 0), pady=10)
        
        # ----- Table Section -----
        table_frame = ttk.LabelFrame(self.dm_tab, text="Existing Design Modules", padding=10)
        table_frame.pack(fill='both', expand=True)
        
        # Create Treeview for displaying design modules
        columns = ('ID', 'Name', 'Description')
        self.dm_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=12)
        
        # Define column headings and widths
        self.dm_tree.heading('ID', text='Module ID')
        self.dm_tree.heading('Name', text='Name')
        self.dm_tree.heading('Description', text='Description')
        
        self.dm_tree.column('ID', width=120, minwidth=100)
        self.dm_tree.column('Name', width=200, minwidth=150)
        self.dm_tree.column('Description', width=420, minwidth=300)
        
        # Add scrollbar
        dm_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.dm_tree.yview)
        self.dm_tree.configure(yscrollcommand=dm_scrollbar.set)
        
        self.dm_tree.pack(side='left', fill='both', expand=True)
        dm_scrollbar.pack(side='right', fill='y')
        
        # Load existing data
        self._refresh_design_modules_list()
    
    def _add_design_module(self) -> None:
        """Handle adding a new design module."""
        # Get values from form
        module_id = self.dm_id_entry.get().strip()
        name = self.dm_name_entry.get().strip()
        description = self.dm_desc_text.get("1.0", tk.END).strip()
        
        # Call service to add design module
        success, message = self.service.add_design_module(module_id, name, description)
        
        if success:
            messagebox.showinfo("Success", message)
            # Clear the form
            self.dm_id_entry.delete(0, tk.END)
            self.dm_name_entry.delete(0, tk.END)
            self.dm_desc_text.delete("1.0", tk.END)
            # Refresh the list
            self._refresh_design_modules_list()
            # Refresh dropdowns in traceability tab
            self._refresh_traceability_dropdowns()
        else:
            messagebox.showerror("Error", message)
    
    def _refresh_design_modules_list(self) -> None:
        """Refresh the design modules table with current data."""
        # Clear existing items
        for item in self.dm_tree.get_children():
            self.dm_tree.delete(item)
        
        # Get and display all design modules
        modules = self.service.get_all_design_modules()
        for mod in modules:
            self.dm_tree.insert('', tk.END, values=mod)
    
    # ==================== TEST CASES TAB ====================
    
    def _create_test_cases_tab(self) -> None:
        """Create the Test Cases tab with input form and list view."""
        # Create the tab frame
        self.tc_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tc_tab, text='Test Cases')
        
        # ----- Input Form Section -----
        form_frame = ttk.LabelFrame(self.tc_tab, text="Add New Test Case", padding=10)
        form_frame.pack(fill='x', pady=(0, 10))
        
        # Test ID
        ttk.Label(form_frame, text="Test ID:").grid(row=0, column=0, sticky='w', pady=5)
        self.tc_id_entry = ttk.Entry(form_frame, width=30)
        self.tc_id_entry.grid(row=0, column=1, sticky='w', padx=(10, 0), pady=5)
        
        # Description
        ttk.Label(form_frame, text="Description:").grid(row=1, column=0, sticky='nw', pady=5)
        self.tc_desc_text = tk.Text(form_frame, height=2, width=60)
        self.tc_desc_text.grid(row=1, column=1, sticky='w', padx=(10, 0), pady=5)
        
        # Expected Result
        ttk.Label(form_frame, text="Expected Result:").grid(row=2, column=0, sticky='nw', pady=5)
        self.tc_result_text = tk.Text(form_frame, height=2, width=60)
        self.tc_result_text.grid(row=2, column=1, sticky='w', padx=(10, 0), pady=5)
        
        # Add Button
        self.add_tc_btn = ttk.Button(form_frame, text="Add Test Case", command=self._add_test_case)
        self.add_tc_btn.grid(row=3, column=1, sticky='w', padx=(10, 0), pady=10)
        
        # ----- Table Section -----
        table_frame = ttk.LabelFrame(self.tc_tab, text="Existing Test Cases", padding=10)
        table_frame.pack(fill='both', expand=True)
        
        # Create Treeview for displaying test cases
        columns = ('ID', 'Description', 'Expected Result')
        self.tc_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        
        # Define column headings and widths
        self.tc_tree.heading('ID', text='Test ID')
        self.tc_tree.heading('Description', text='Description')
        self.tc_tree.heading('Expected Result', text='Expected Result')
        
        self.tc_tree.column('ID', width=100, minwidth=80)
        self.tc_tree.column('Description', width=350, minwidth=250)
        self.tc_tree.column('Expected Result', width=290, minwidth=200)
        
        # Add scrollbar
        tc_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tc_tree.yview)
        self.tc_tree.configure(yscrollcommand=tc_scrollbar.set)
        
        self.tc_tree.pack(side='left', fill='both', expand=True)
        tc_scrollbar.pack(side='right', fill='y')
        
        # Load existing data
        self._refresh_test_cases_list()
    
    def _add_test_case(self) -> None:
        """Handle adding a new test case."""
        # Get values from form
        test_id = self.tc_id_entry.get().strip()
        description = self.tc_desc_text.get("1.0", tk.END).strip()
        expected_result = self.tc_result_text.get("1.0", tk.END).strip()
        
        # Call service to add test case
        success, message = self.service.add_test_case(test_id, description, expected_result)
        
        if success:
            messagebox.showinfo("Success", message)
            # Clear the form
            self.tc_id_entry.delete(0, tk.END)
            self.tc_desc_text.delete("1.0", tk.END)
            self.tc_result_text.delete("1.0", tk.END)
            # Refresh the list
            self._refresh_test_cases_list()
            # Refresh dropdowns in traceability tab
            self._refresh_traceability_dropdowns()
        else:
            messagebox.showerror("Error", message)
    
    def _refresh_test_cases_list(self) -> None:
        """Refresh the test cases table with current data."""
        # Clear existing items
        for item in self.tc_tree.get_children():
            self.tc_tree.delete(item)
        
        # Get and display all test cases
        test_cases = self.service.get_all_test_cases()
        for tc in test_cases:
            self.tc_tree.insert('', tk.END, values=tc)
    
    # ==================== TRACEABILITY MATRIX TAB ====================
    
    def _create_traceability_tab(self) -> None:
        """Create the Traceability Matrix tab with mapping forms and RTM display."""
        # Create the tab frame
        self.rtm_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.rtm_tab, text='Traceability Matrix')
        
        # ----- Mapping Section -----
        mapping_frame = ttk.LabelFrame(self.rtm_tab, text="Create Trace Links", padding=10)
        mapping_frame.pack(fill='x', pady=(0, 10))
        
        # Left side: Requirement to Design Module mapping
        left_frame = ttk.Frame(mapping_frame)
        left_frame.pack(side='left', fill='x', expand=True, padx=(0, 20))
        
        ttk.Label(left_frame, text="Link Requirement → Design Module", 
                  style='Header.TLabel').grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 10))
        
        ttk.Label(left_frame, text="Requirement:").grid(row=1, column=0, sticky='w', pady=5)
        self.rtm_req_dm_combo = ttk.Combobox(left_frame, width=20, state="readonly")
        self.rtm_req_dm_combo.grid(row=1, column=1, sticky='w', padx=10, pady=5)
        
        ttk.Label(left_frame, text="Design Module:").grid(row=2, column=0, sticky='w', pady=5)
        self.rtm_dm_combo = ttk.Combobox(left_frame, width=20, state="readonly")
        self.rtm_dm_combo.grid(row=2, column=1, sticky='w', padx=10, pady=5)
        
        self.link_dm_btn = ttk.Button(left_frame, text="Create Link", 
                                       command=self._link_requirement_to_design)
        self.link_dm_btn.grid(row=3, column=1, sticky='w', padx=10, pady=10)
        
        # Separator
        ttk.Separator(mapping_frame, orient='vertical').pack(side='left', fill='y', padx=10)
        
        # Right side: Requirement to Test Case mapping
        right_frame = ttk.Frame(mapping_frame)
        right_frame.pack(side='left', fill='x', expand=True, padx=(20, 0))
        
        ttk.Label(right_frame, text="Link Requirement → Test Case", 
                  style='Header.TLabel').grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 10))
        
        ttk.Label(right_frame, text="Requirement:").grid(row=1, column=0, sticky='w', pady=5)
        self.rtm_req_tc_combo = ttk.Combobox(right_frame, width=20, state="readonly")
        self.rtm_req_tc_combo.grid(row=1, column=1, sticky='w', padx=10, pady=5)
        
        ttk.Label(right_frame, text="Test Case:").grid(row=2, column=0, sticky='w', pady=5)
        self.rtm_tc_combo = ttk.Combobox(right_frame, width=20, state="readonly")
        self.rtm_tc_combo.grid(row=2, column=1, sticky='w', padx=10, pady=5)
        
        self.link_tc_btn = ttk.Button(right_frame, text="Create Link", 
                                       command=self._link_requirement_to_test)
        self.link_tc_btn.grid(row=3, column=1, sticky='w', padx=10, pady=10)
        
        # ----- RTM Table Section -----
        table_frame = ttk.LabelFrame(self.rtm_tab, text="Requirement Traceability Matrix", padding=10)
        table_frame.pack(fill='both', expand=True)
        
        # Refresh button
        refresh_btn = ttk.Button(table_frame, text="Refresh Matrix", command=self._refresh_rtm)
        refresh_btn.pack(anchor='e', pady=(0, 10))
        
        # Create Treeview for displaying RTM
        columns = ('Req ID', 'Description', 'Type', 'Design Modules', 'Test Cases')
        self.rtm_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        
        # Define column headings and widths
        self.rtm_tree.heading('Req ID', text='Req ID')
        self.rtm_tree.heading('Description', text='Description')
        self.rtm_tree.heading('Type', text='Type')
        self.rtm_tree.heading('Design Modules', text='Design Modules')
        self.rtm_tree.heading('Test Cases', text='Test Cases')
        
        self.rtm_tree.column('Req ID', width=80, minwidth=70)
        self.rtm_tree.column('Description', width=280, minwidth=200)
        self.rtm_tree.column('Type', width=100, minwidth=80)
        self.rtm_tree.column('Design Modules', width=150, minwidth=120)
        self.rtm_tree.column('Test Cases', width=150, minwidth=120)
        
        # Add scrollbar
        rtm_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.rtm_tree.yview)
        self.rtm_tree.configure(yscrollcommand=rtm_scrollbar.set)
        
        self.rtm_tree.pack(side='left', fill='both', expand=True)
        rtm_scrollbar.pack(side='right', fill='y')
        
        # Initialize dropdowns and table
        self._refresh_traceability_dropdowns()
        self._refresh_rtm()
    
    def _refresh_traceability_dropdowns(self) -> None:
        """Refresh all dropdown menus in the traceability tab."""
        # Get current data
        req_ids = self.service.get_requirement_ids()
        dm_ids = self.service.get_design_module_ids()
        tc_ids = self.service.get_test_case_ids()
        
        # Update requirement dropdowns
        self.rtm_req_dm_combo['values'] = req_ids
        self.rtm_req_tc_combo['values'] = req_ids
        
        # Update design module dropdown
        self.rtm_dm_combo['values'] = dm_ids
        
        # Update test case dropdown
        self.rtm_tc_combo['values'] = tc_ids
    
    def _link_requirement_to_design(self) -> None:
        """Handle creating a requirement to design module link."""
        req_id = self.rtm_req_dm_combo.get()
        module_id = self.rtm_dm_combo.get()
        
        if not req_id or not module_id:
            messagebox.showwarning("Warning", "Please select both a requirement and a design module")
            return
        
        success, message = self.service.link_requirement_to_design(req_id, module_id)
        
        if success:
            messagebox.showinfo("Success", message)
            self._refresh_rtm()
        else:
            messagebox.showerror("Error", message)
    
    def _link_requirement_to_test(self) -> None:
        """Handle creating a requirement to test case link."""
        req_id = self.rtm_req_tc_combo.get()
        test_id = self.rtm_tc_combo.get()
        
        if not req_id or not test_id:
            messagebox.showwarning("Warning", "Please select both a requirement and a test case")
            return
        
        success, message = self.service.link_requirement_to_test(req_id, test_id)
        
        if success:
            messagebox.showinfo("Success", message)
            self._refresh_rtm()
        else:
            messagebox.showerror("Error", message)
    
    def _refresh_rtm(self) -> None:
        """Refresh the RTM table with current traceability data."""
        # Clear existing items
        for item in self.rtm_tree.get_children():
            self.rtm_tree.delete(item)
        
        # Get and display RTM data
        rtm_data = self.service.get_traceability_matrix()
        for row in rtm_data:
            # row = (req_id, description, type, modules, tests)
            self.rtm_tree.insert('', tk.END, values=row)


def create_app(service: TraceService) -> tk.Tk:
    """
    Create and return the main application window.
    
    Args:
        service: TraceService instance for business logic
        
    Returns:
        Configured Tk root window
    """
    root = tk.Tk()
    app = RTMApplication(root, service)
    return root
