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
from tkinter import ttk, messagebox, filedialog
from typing import Optional
import sys
import os

from service.trace_service import TraceService
from ui.visualization import GraphVisualizer


class RTMApplication:

    """
    Main application class for the RTM Tool GUI.
    This class creates and manages the main window and all tabs of the application.
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
        self._create_impact_tab()
        self._create_traceability_tab()
        self._create_dashboard_tab()

    def _create_dashboard_tab(self) -> None:
        """Create the Dashboard tab with coverage, traceability, and risk summary."""
        self.dashboard_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.dashboard_tab, text='Dashboard')

        # Coverage Section
        coverage_frame = ttk.LabelFrame(self.dashboard_tab, text="Coverage Metrics", padding=10)
        coverage_frame.pack(fill='x', pady=8)
        self.coverage_labels = {}
        for i, (label, key) in enumerate([
            ("Total Requirements", "total"),
            ("Design Coverage", "design_coverage"),
            ("Test Coverage", "test_coverage")]):
            ttk.Label(coverage_frame, text=label+":").grid(row=i, column=0, sticky='w', pady=2)
            val = ttk.Label(coverage_frame, text="-")
            val.grid(row=i, column=1, sticky='w', pady=2)
            self.coverage_labels[key] = val

        # Traceability Section
        trace_frame = ttk.LabelFrame(self.dashboard_tab, text="Traceability Breakdown", padding=10)
        trace_frame.pack(fill='x', pady=8)
        self.trace_labels = {}
        for i, (label, key) in enumerate([
            ("Fully Traced", "fully_traced"),
            ("Partially Traced", "partially_traced"),
            ("Untraced", "untraced")]):
            ttk.Label(trace_frame, text=label+":").grid(row=i, column=0, sticky='w', pady=2)
            val = ttk.Label(trace_frame, text="-")
            val.grid(row=i, column=1, sticky='w', pady=2)
            self.trace_labels[key] = val

        # Risk Summary Section
        risk_frame = ttk.LabelFrame(self.dashboard_tab, text="Risk Summary", padding=10)
        risk_frame.pack(fill='x', pady=8)
        self.risk_labels = {}
        for i, (label, key, color) in enumerate([
            ("HIGH Risk", "HIGH", "red"),
            ("MEDIUM Risk", "MEDIUM", "orange"),
            ("LOW Risk", "LOW", "green")]):
            ttk.Label(risk_frame, text=label+":").grid(row=i, column=0, sticky='w', pady=2)
            val = ttk.Label(risk_frame, text="-", foreground=color, font=('Segoe UI', 10, 'bold'))
            val.grid(row=i, column=1, sticky='w', pady=2)
            self.risk_labels[key] = val


        # Dashboard Buttons
        btn_frame = ttk.Frame(self.dashboard_tab)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Refresh Dashboard", command=self._refresh_dashboard_metrics).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="System Health Check", command=self._run_system_validation).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Detect Duplicates (AI)", command=self._run_duplicate_detection).pack(side='left', padx=5)

        # PDF Export Section
        export_frame = ttk.LabelFrame(self.dashboard_tab, text="Reporting", padding=10)
        export_frame.pack(fill='x', pady=8)
        
        ttk.Button(export_frame, text="Export Report...", command=self._show_export_options).pack(side='left', padx=10, pady=5)

        # Initial load
        self._refresh_dashboard_metrics()

    def _show_export_options(self) -> None:
        """Show a popup menu with different report export options."""
        popup = tk.Toplevel(self.root)
        popup.title("Export PDF Report")
        popup.geometry("300x250")
        popup.grab_set() # Make it modal
        
        ttk.Label(popup, text="Select Report Type:", font=('Segoe UI', 10, 'bold')).pack(pady=15)
        
        ttk.Button(popup, text="Traceability Matrix Report", 
                   command=lambda: [popup.destroy(), self._export_rtm_pdf()]).pack(fill='x', padx=30, pady=5)
        
        ttk.Button(popup, text="Coverage Analysis Report", 
                   command=lambda: [popup.destroy(), self._export_coverage_pdf()]).pack(fill='x', padx=30, pady=5)
        
        ttk.Button(popup, text="Risk Assessment Report", 
                   command=lambda: [popup.destroy(), self._export_risk_pdf()]).pack(fill='x', padx=30, pady=5)
        
        ttk.Button(popup, text="Cancel", command=popup.destroy).pack(pady=20)
    
    def _export_rtm_pdf(self) -> None:
        """Export Traceability Matrix to PDF with file dialog."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile="traceability_report.pdf",
            title="Save Traceability Report"
        )
        if not filename: return # User cancelled
        
        if self.service.export_traceability_report(filename):
            messagebox.showinfo("Export Successful", f"Traceability report saved successfully.")
        else:
            messagebox.showerror("Export Failed", "Failed to generate traceability report.")

    def _export_coverage_pdf(self) -> None:
        """Export Coverage Metrics to PDF with file dialog."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile="coverage_report.pdf",
            title="Save Coverage Report"
        )
        if not filename: return
        
        if self.service.export_coverage_report(filename):
            messagebox.showinfo("Export Successful", f"Coverage report saved successfully.")
        else:
            messagebox.showerror("Export Failed", "Failed to generate coverage report.")

    def _export_risk_pdf(self) -> None:
        """Export Risk Assessment to PDF with file dialog."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile="risk_report.pdf",
            title="Save Risk Report"
        )
        if not filename: return
        
        if self.service.export_risk_report(filename):
            messagebox.showinfo("Export Successful", f"Risk assessment report saved successfully.")
        else:
            messagebox.showerror("Export Failed", "Failed to generate risk assessment report.")

    def _run_duplicate_detection(self) -> None:
        """Run AI-based duplicate detection and show results."""
        duplicates = self.service.detect_duplicates()
        if not duplicates:
            messagebox.showinfo("Duplicate Detection", "No duplicate requirements detected.")
            return
            
        popup = tk.Toplevel(self.root)
        popup.title("AI Duplicate Requirement Report")
        popup.geometry("650x400")
        
        ttk.Label(popup, text="Potential Duplicate Requirements:", font=('Segoe UI', 11, 'bold')).pack(pady=10)
        
        frame = ttk.Frame(popup)
        frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ('Requirement A', 'Requirement B', 'Similarity Score')
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200)
        
        tree.pack(fill='both', expand=True)
        
        for d in duplicates:
            tree.insert('', 'end', values=(d['similar_to'], d['req_id'], f"{d['score']*100:.1f}%"))

    def _run_system_validation(self) -> None:
        """Run full system validation and show results."""
        results = self.service.validate_system()
        issues = results['issues']
        violations = results['rule_violations']
        
        if not issues and not violations:
            messagebox.showinfo("System Health", "System is healthy! No issues or rule violations detected.")
            return
            
        popup = tk.Toplevel(self.root)
        popup.title("System Health Report")
        popup.geometry("800x550")
        
        notebook = ttk.Notebook(popup)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Consistency Issues
        issues_tab = ttk.Frame(notebook, padding=10)
        notebook.add(issues_tab, text=f"Consistency Issues ({len(issues)})")
        
        columns_i = ('Type', 'ID', 'Description')
        tree_i = ttk.Treeview(issues_tab, columns=columns_i, show='headings')
        for col in columns_i:
            tree_i.heading(col, text=col)
            tree_i.column(col, width=150)
        tree_i.column('Description', width=400)
        tree_i.pack(fill='both', expand=True)
        for issue in issues:
            tree_i.insert('', 'end', values=(issue['type'], issue['id'], issue['message']))
            
        # Tab 2: Rule Violations
        rules_tab = ttk.Frame(notebook, padding=10)
        notebook.add(rules_tab, text=f"Rule Violations ({len(violations)})")
        
        columns_r = ('Rule', 'ID', 'Status')
        tree_r = ttk.Treeview(rules_tab, columns=columns_r, show='headings')
        for col in columns_r:
            tree_r.heading(col, text=col)
            tree_r.column(col, width=150)
        tree_r.pack(fill='both', expand=True)
        for v in violations:
            tree_r.insert('', 'end', values=(v['rule'], v['id'], v['status']))

    def _validate_rules(self) -> None:
        """Run rule validation and show results."""
        violations = self.service.validate_rules()
        if not violations:
            messagebox.showinfo("Rule Validation", "All rules passed! No violations found.")
            return
            
        popup = tk.Toplevel(self.root)
        popup.title("Rule Validation Report")
        popup.geometry("600x400")
        
        ttk.Label(popup, text="Rule Violations Detected:", font=('Segoe UI', 11, 'bold')).pack(pady=10)
        
        frame = ttk.Frame(popup)
        frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ('Rule', 'Entity ID', 'Status')
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        for v in violations:
            tree.insert('', 'end', values=(v['rule'], v['id'], v['status']))

    def _run_consistency_check(self) -> None:
        """Run consistency check and show results."""
        issues = self.service.check_consistency()
        if not issues:
            messagebox.showinfo("Consistency Check", "No traceability issues detected! The system is consistent.")
            return
            
        # Create a popup window to show issues
        popup = tk.Toplevel(self.root)
        popup.title("Traceability Consistency Report")
        popup.geometry("700x450")
        
        ttk.Label(popup, text="Detected Traceability Gaps:", font=('Segoe UI', 11, 'bold')).pack(pady=10)
        
        frame = ttk.Frame(popup)
        frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ('Type', 'Entity ID', 'Description')
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        tree.column('Description', width=400)
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        for issue in issues:
            tree.insert('', 'end', values=(issue['type'], issue['id'], issue['message']))

    def _refresh_dashboard_metrics(self):
        """Fetch and display dashboard metrics."""
        metrics = self.service.get_dashboard_metrics()
        cov = metrics['coverage']
        # Show percentages as e.g. 80.0%
        self.coverage_labels['total'].config(text=str(cov['total']))
        self.coverage_labels['design_coverage'].config(text=f"{cov['design_coverage']*100:.1f}%")
        self.coverage_labels['test_coverage'].config(text=f"{cov['test_coverage']*100:.1f}%")

        trace = metrics['traceability_breakdown']
        self.trace_labels['fully_traced'].config(text=str(trace['fully_traced']))
        self.trace_labels['partially_traced'].config(text=str(trace['partially_traced']))
        self.trace_labels['untraced'].config(text=str(trace['untraced']))

        risk = metrics['risk_summary']
        # Update risk labels
        for key in ['HIGH', 'MEDIUM', 'LOW']:
            self.risk_labels[key].config(text=str(risk.get(key, 0)))
    
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

        # ----- Dependency Section -----
        dep_frame = ttk.LabelFrame(self.req_tab, text="Link Requirement Dependencies", padding=10)
        dep_frame.pack(fill='x', pady=(0, 10))

        ttk.Label(dep_frame, text="Requirement:").grid(row=0, column=0, sticky='w', pady=5)
        self.child_req_combo = ttk.Combobox(dep_frame, width=20, state="readonly")
        self.child_req_combo.grid(row=0, column=1, sticky='w', padx=10, pady=5)

        ttk.Label(dep_frame, text="Depends On:").grid(row=0, column=2, sticky='w', pady=5)
        self.parent_req_combo = ttk.Combobox(dep_frame, width=20, state="readonly")
        self.parent_req_combo.grid(row=0, column=3, sticky='w', padx=10, pady=5)

        self.link_dep_btn = ttk.Button(dep_frame, text="Link Dependency", command=self._link_dependency)
        self.link_dep_btn.grid(row=0, column=4, sticky='w', padx=20, pady=5)
        
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
        
        if not req_id or not description:
            messagebox.showerror("Error", "Requirement ID and Description cannot be empty")
            return

        # AI Duplicate Check
        similar = self.service.check_new_description(description)
        if similar:
            score_pct = int(similar['score'] * 100)
            msg = f"Similar requirement found: {similar['req_id']} ({score_pct}% match).\n\nDo you want to proceed anyway?"
            if not messagebox.askyesno("AI Duplicate Warning", msg):
                return

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

        # ----- AI Suggestion Section -----
        suggest_frame = ttk.LabelFrame(self.rtm_tab, text="AI Link Assistant (Auto-Mapping)", padding=10)
        suggest_frame.pack(fill='x', pady=(0, 10))

        # Selection row
        top_row = ttk.Frame(suggest_frame)
        top_row.pack(fill='x', pady=5)
        ttk.Label(top_row, text="Requirement:").pack(side='left')
        self.suggest_req_combo = ttk.Combobox(top_row, width=30, state="readonly")
        self.suggest_req_combo.pack(side='left', padx=10)
        ttk.Button(top_row, text="Analyze & Suggest", command=self._get_suggestions).pack(side='left')

        # Lists row
        list_row = ttk.Frame(suggest_frame)
        list_row.pack(fill='x', pady=5)
        
        d_frame = ttk.Frame(list_row)
        d_frame.pack(side='left', fill='both', expand=True, padx=5)
        ttk.Label(d_frame, text="Suggested Design:").pack(anchor='w')
        self.suggest_design_list = tk.Listbox(d_frame, height=3)
        self.suggest_design_list.pack(fill='x')

        t_frame = ttk.Frame(list_row)
        t_frame.pack(side='left', fill='both', expand=True, padx=5)
        ttk.Label(t_frame, text="Suggested Tests:").pack(anchor='w')
        self.suggest_test_list = tk.Listbox(t_frame, height=3)
        self.suggest_test_list.pack(fill='x')

        # Action row
        self.apply_suggest_btn = ttk.Button(suggest_frame, text="Apply All Suggestions", command=self._apply_suggestions, state='disabled')
        self.apply_suggest_btn.pack(pady=5)
        
        self.current_suggestions = None

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
    
    def _get_suggestions(self) -> None:
        """Fetch and display link suggestions for the selected requirement."""
        req_id = self.suggest_req_combo.get()
        if not req_id:
            messagebox.showwarning("Warning", "Please select a requirement first")
            return

        # Fetch requirement text
        req_data = self.service.get_requirement_by_id(req_id)
        if not req_data:
            return
        
        req_text = req_data[1]
        
        # Call service for suggestions
        suggestions = self.service.suggest_links(req_text)
        self.current_suggestions = suggestions

        # Update Lists
        self.suggest_design_list.delete(0, tk.END)
        if not suggestions['design']:
            self.suggest_design_list.insert(tk.END, "No strong matches found")
        else:
            for dm_id in suggestions['design']:
                self.suggest_design_list.insert(tk.END, dm_id)

        self.suggest_test_list.delete(0, tk.END)
        if not suggestions['tests']:
            self.suggest_test_list.insert(tk.END, "No strong matches found")
        else:
            for tc_id in suggestions['tests']:
                self.suggest_test_list.insert(tk.END, tc_id)

        # Enable Apply button if suggestions exist
        if suggestions['design'] or suggestions['tests']:
            self.apply_suggest_btn.config(state='normal')
        else:
            self.apply_suggest_btn.config(state='disabled')

    def _apply_suggestions(self) -> None:
        """Automatically create trace links for all suggestions."""
        if not self.current_suggestions:
            return
            
        req_id = self.suggest_req_combo.get()
        if not req_id:
            return

        applied_count = 0
        
        # Link Designs
        for dm_id in self.current_suggestions['design']:
            success, _ = self.service.link_requirement_to_design(req_id, dm_id)
            if success: applied_count += 1
            
        # Link Tests
        for tc_id in self.current_suggestions['tests']:
            success, _ = self.service.link_requirement_to_test(req_id, tc_id)
            if success: applied_count += 1

        if applied_count > 0:
            messagebox.showinfo("Success", f"Successfully applied {applied_count} trace links based on AI suggestions.")
            self._refresh_rtm()
            self.apply_suggest_btn.config(state='disabled')
        else:
            messagebox.showinfo("Info", "No new links were created (they might already exist).")

    def _refresh_traceability_dropdowns(self) -> None:
        """Refresh all dropdown menus in the traceability tab."""
        # Get current data
        req_ids = self.service.get_requirement_ids()
        dm_ids = self.service.get_design_module_ids()
        tc_ids = self.service.get_test_case_ids()
        
        # Update requirement dropdowns in Traceability tab
        self.rtm_req_dm_combo['values'] = req_ids
        self.rtm_req_tc_combo['values'] = req_ids
        
        # Update requirement dropdowns in Requirements tab
        self.child_req_combo['values'] = req_ids
        self.parent_req_combo['values'] = req_ids

        # Update requirement dropdown in Impact tab
        # Some tabs/widgets may not be initialized in all construction orders
        if hasattr(self, 'impact_req_combo') and self.impact_req_combo:
            self.impact_req_combo['values'] = req_ids
        
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

    # ==================== IMPACT ANALYSIS TAB ====================

    def _create_impact_tab(self) -> None:
        """Create the Impact Analysis tab with upstream, downstream, design, tests, and risk."""
        self.impact_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.impact_tab, text='Impact Analysis')

        # ----- Selection Section -----
        select_frame = ttk.LabelFrame(self.impact_tab, text="Select Requirement for Analysis", padding=10)
        select_frame.pack(fill='x', pady=(0, 10))

        ttk.Label(select_frame, text="Requirement:").grid(row=0, column=0, sticky='w', pady=5)
        self.impact_req_combo = ttk.Combobox(select_frame, width=30, state="readonly")
        self.impact_req_combo.grid(row=0, column=1, sticky='w', padx=10, pady=5)

        self.analyze_btn = ttk.Button(select_frame, text="Analyze Impact", command=self._analyze_impact)
        self.analyze_btn.grid(row=0, column=2, sticky='w', padx=20, pady=5)

        # ----- Results Section -----
        results_frame = ttk.Frame(self.impact_tab)
        results_frame.pack(fill='both', expand=True)

        # Use a grid layout for clean separation
        results_frame.grid_rowconfigure(1, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_columnconfigure(1, weight=1)

        # Upstream Dependencies
        upstream_frame = ttk.LabelFrame(results_frame, text="Upstream Dependencies")
        upstream_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        self.upstream_list = tk.Listbox(upstream_frame, height=5)
        self.upstream_list.pack(fill='both', expand=True, padx=5, pady=5)

        # Downstream Impact
        downstream_frame = ttk.LabelFrame(results_frame, text="Downstream Impact")
        downstream_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        self.downstream_list = tk.Listbox(downstream_frame, height=5)
        self.downstream_list.pack(fill='both', expand=True, padx=5, pady=5)

        # Linked Design Modules
        design_frame = ttk.LabelFrame(results_frame, text="Linked Design Modules")
        design_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        self.design_list = tk.Listbox(design_frame, height=5)
        self.design_list.pack(fill='both', expand=True, padx=5, pady=5)

        # Linked Test Cases
        test_frame = ttk.LabelFrame(results_frame, text="Linked Test Cases")
        test_frame.grid(row=1, column=1, sticky='nsew', padx=5, pady=5)
        self.test_list = tk.Listbox(test_frame, height=5)
        self.test_list.pack(fill='both', expand=True, padx=5, pady=5)

        # Risk Analysis
        risk_frame = ttk.LabelFrame(results_frame, text="Risk Assessment")
        risk_frame.grid(row=2, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        self.risk_label = tk.Label(risk_frame, text="UNKNOWN", font=('Segoe UI', 12, 'bold'))
        self.risk_label.pack(pady=10)

    def _link_dependency(self) -> None:
        """Handle creating a requirement dependency link."""
        child_id = self.child_req_combo.get()
        parent_id = self.parent_req_combo.get()

        if not child_id or not parent_id:
            messagebox.showwarning("Warning", "Please select both requirements")
            return

        success, message = self.service.link_requirement_dependency(parent_id, child_id)
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)

    def _analyze_impact(self) -> None:
        """Perform and display full impact analysis with risk and artifacts."""
        req_id = self.impact_req_combo.get()
        if not req_id:
            messagebox.showwarning("Warning", "Please select a requirement to analyze")
            return

        result = self.service.get_full_impact_analysis(req_id)

        # Upstream
        self.upstream_list.delete(0, tk.END)
        if not result['upstream']:
            self.upstream_list.insert(tk.END, "No upstream dependencies")
        else:
            for req in result['upstream']:
                self.upstream_list.insert(tk.END, req)

        # Downstream
        self.downstream_list.delete(0, tk.END)
        if not result['downstream']:
            self.downstream_list.insert(tk.END, "No downstream dependencies")
        else:
            for req in result['downstream']:
                self.downstream_list.insert(tk.END, req)

        # Design Modules
        self.design_list.delete(0, tk.END)
        if not result['design']:
            self.design_list.insert(tk.END, "No linked design modules")
        else:
            for mod in result['design']:
                self.design_list.insert(tk.END, mod)

        # Test Cases
        self.test_list.delete(0, tk.END)
        if not result['tests']:
            self.test_list.insert(tk.END, "No linked test cases")
        else:
            for tc in result['tests']:
                self.test_list.insert(tk.END, tc)

        # Risk Level (color coded)
        risk = result['risk']
        color = {'HIGH': 'red', 'MEDIUM': 'orange', 'LOW': 'green'}.get(risk, 'black')
        self.risk_label.config(text=f"{risk} RISK", fg=color)


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




