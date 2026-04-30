"""
Professional PDF Report Generation for RTM Tool
Provides functionality to generate clean, readable reports for Traceability, Coverage, and Risk.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os
from datetime import datetime

class ReportGenerator:
    def __init__(self, filename):
        self.filename = filename
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='ReportTitle', 
            parent=self.styles['Heading1'], 
            fontSize=18,
            spaceAfter=20, 
            alignment=1, # Center
            textColor=colors.HexColor("#2C3E50")
        ))
        self.styles.add(ParagraphStyle(
            name='SectionHeading', 
            parent=self.styles['Heading2'], 
            fontSize=14,
            spaceBefore=15, 
            spaceAfter=10,
            textColor=colors.HexColor("#2980B9")
        ))
        self.styles.add(ParagraphStyle(
            name='SummaryText', 
            parent=self.styles['Normal'], 
            fontSize=11,
            leading=14,
            spaceAfter=12
        ))

    def _create_base_elements(self, title, summary_text):
        elements = []
        # Title
        elements.append(Paragraph(title, self.styles['ReportTitle']))
        
        # Metadata (Date)
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elements.append(Paragraph(f"Generated on: {date_str}", self.styles['Normal']))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Summary Section
        elements.append(Paragraph("Executive Summary", self.styles['SectionHeading']))
        elements.append(Paragraph(summary_text, self.styles['SummaryText']))
        elements.append(Spacer(1, 0.2 * inch))
        
        return elements

    def _get_table_style(self, header_color="#34495E"):
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(header_color)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ])

    def generate_traceability_report(self, rtm_data):
        """Generates a comprehensive Traceability Matrix PDF."""
        doc = SimpleDocTemplate(self.filename, pagesize=landscape(letter))
        summary = "This report provides a full mapping between requirements, their implemented design modules, and verifying test cases. It highlights the end-to-end traceability of the system."
        elements = self._create_base_elements("Requirement Traceability Matrix (RTM) Report", summary)
        
        elements.append(Paragraph("Traceability Data", self.styles['SectionHeading']))
        
        # Prepare table data
        table_data = [["Req ID", "Description", "Type", "Design Modules", "Test Cases"]]
        for row in rtm_data:
            table_data.append([
                row[0], 
                Paragraph(row[1], self.styles['Normal']), # Use Paragraph for wrapping
                row[2], 
                row[3] if row[3] else "None", 
                row[4] if row[4] else "None"
            ])
            
        t = Table(table_data, colWidths=[0.8*inch, 3.5*inch, 1.2*inch, 2.0*inch, 2.0*inch])
        t.setStyle(self._get_table_style())
        elements.append(t)
        
        doc.build(elements)

    def generate_coverage_report(self, stats):
        """Generates a project coverage analysis PDF."""
        doc = SimpleDocTemplate(self.filename, pagesize=letter)
        summary = f"This report analyzes the coverage of requirements across design and testing phases. Total requirements analyzed: {stats['total']}."
        elements = self._create_base_elements("Traceability Coverage Report", summary)
        
        # Key Metrics Table
        elements.append(Paragraph("Key Coverage Metrics", self.styles['SectionHeading']))
        
        table_data = [
            ["Metric", "Value", "Status"],
            ["Design Coverage", f"{stats['design_coverage']*100:.1f}%", "Pass" if stats['design_coverage'] > 0.8 else "Warning"],
            ["Test Coverage", f"{stats['test_coverage']*100:.1f}%", "Pass" if stats['test_coverage'] > 0.8 else "Warning"],
            ["Fully Traced Requirements", str(stats['fully_traced']), "Target: All"],
            ["Untraced Requirements", str(stats['untraced']), "CRITICAL" if stats['untraced'] > 0 else "Clean"]
        ]
        
        t = Table(table_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        t.setStyle(self._get_table_style("#27AE60"))
        elements.append(t)
        
        doc.build(elements)

    def generate_risk_report(self, risk_items):
        """Generates a risk assessment report for requirements."""
        doc = SimpleDocTemplate(self.filename, pagesize=letter)
        summary = "This report identifies high-risk requirements based on missing traceability links (Design or Test). High-risk items require immediate engineering attention."
        elements = self._create_base_elements("Requirement Risk Assessment Report", summary)
        
        elements.append(Paragraph("Identified Risks by Requirement", self.styles['SectionHeading']))
        
        table_data = [["Req ID", "Risk Level", "Impacted Design", "Impacted Tests"]]
        for item in risk_items:
            # item format from service: {'id': 'REQ-1', 'risk': 'HIGH', 'design': [...], 'tests': [...]}
            color = colors.red if item['risk'] == 'HIGH' else (colors.orange if item['risk'] == 'MEDIUM' else colors.green)
            
            table_data.append([
                item['id'],
                Paragraph(f"<font color='{color}'><b>{item['risk']}</b></font>", self.styles['Normal']),
                ", ".join(item['design']) if item['design'] else "None",
                ", ".join(item['tests']) if item['tests'] else "None"
            ])
            
        t = Table(table_data, colWidths=[1.2*inch, 1.2*inch, 2.0*inch, 2.0*inch])
        t.setStyle(self._get_table_style("#C0392B"))
        elements.append(t)
        
        doc.build(elements)
