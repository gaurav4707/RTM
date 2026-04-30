"""
Visualization Module

This module provides graph visualizations for the RTM Tool
using networkx and matplotlib.
"""

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk

class GraphVisualizer:
    def __init__(self, service):
        self.service = service
        
    def create_graph(self):
        """Create a networkx graph from the current RTM data."""
        G = nx.Graph()
        
        # Add nodes and edges
        rtm_data = self.service.get_traceability_matrix()
        
        for row in rtm_data:
            req_id, _, _, modules, tests = row
            
            # Add requirement node
            G.add_node(req_id, type='requirement', color='#4CAF50', size=2000)
            
            # Process design modules
            if modules and modules != "None" and modules != "":
                for mod in modules.split(", "):
                    G.add_node(mod, type='design', color='#2196F3', size=1200)
                    G.add_edge(req_id, mod)
                    
            # Process test cases
            if tests and tests != "None" and tests != "":
                for test in tests.split(", "):
                    G.add_node(test, type='test', color='#FFC107', size=1200)
                    G.add_edge(req_id, test)

        # Add requirement dependencies (directed edges)
        dependencies = self.service.db.get_all_requirement_dependencies()
        for parent_id, child_id in dependencies:
            if parent_id in G and child_id in G:
                G.add_edge(parent_id, child_id, color='red')
                    
        return G
        
    def draw_graph(self, frame):
        """Draw the graph on a Tkinter frame."""
        # Clear previous widgets
        for widget in frame.winfo_children():
            widget.destroy()
            
        G = self.create_graph()
        
        if len(G.nodes) == 0:
            ttk.Label(frame, text="No data to visualize.").pack(padx=20, pady=20)
            return
            
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Get attributes based on node type
        node_colors = [nx.get_node_attributes(G, 'color').get(node, '#808080') for node in G.nodes()]
        node_sizes = [nx.get_node_attributes(G, 'size').get(node, 1000) for node in G.nodes()]
        
        # Get edge attributes
        edge_colors = [nx.get_edge_attributes(G, 'color').get(edge, '#AAAAAA') for edge in G.edges()]
        
        # Use spring layout for better readability
        pos = nx.spring_layout(G, seed=42, k=0.5)
        
        nx.draw(G, pos, ax=ax, with_labels=True, node_color=node_colors, 
                node_size=node_sizes, font_size=10, font_weight='bold',
                edge_color=edge_colors, width=2)
                
        # Add legend
        import matplotlib.patches as mpatches
        import matplotlib.lines as mlines
        req_patch = mpatches.Patch(color='#4CAF50', label='Requirement')
        des_patch = mpatches.Patch(color='#2196F3', label='Design Module')
        test_patch = mpatches.Patch(color='#FFC107', label='Test Case')
        dep_line = mlines.Line2D([], [], color='red', label='Dependency', linewidth=2)
        ax.legend(handles=[req_patch, des_patch, test_patch, dep_line], loc='upper right')
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
