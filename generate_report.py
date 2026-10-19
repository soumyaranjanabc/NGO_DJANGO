import os
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Path to the markdown report (generated earlier)
report_md_path = os.path.join(os.path.dirname(__file__), 'report.md')

if not os.path.exists(report_md_path):
    raise FileNotFoundError(f"Report markdown not found at {report_md_path}")

# Read markdown content
with open(report_md_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Simple parser: headings start with '#', subheadings with '##', tables start with '|'

doc = Document()

# Title page
doc.add_heading('NoSQL Assessment 2 – Project Report', 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('NGO Volunteer Operations Platform')
doc.add_paragraph('Generated on: ' + __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

doc.add_page_break()

for line in lines:
    stripped = line.strip('\n')
    if stripped.startswith('# '):
        # Main heading
        doc.add_heading(stripped[2:], level=1)
    elif stripped.startswith('## '):
        doc.add_heading(stripped[3:], level=2)
    elif stripped.startswith('### '):
        doc.add_heading(stripped[4:], level=3)
    elif stripped.startswith('|'):
        # Table handling – split rows by '|'
        # Collect consecutive table lines
        table_rows = []
        # The current line is part of a table, gather until a non-table line
        idx = lines.index(line)
        while idx < len(lines) and lines[idx].strip().startswith('|'):
            row = [cell.strip() for cell in lines[idx].strip().strip('|').split('|')]
            table_rows.append(row)
            idx += 1
        # Skip the markdown separator line (---) if present and ensure there are at least two rows
        if len(table_rows) > 1 and all(set(cell) <= {'-'} for cell in table_rows[1]):
            table_rows.pop(1)
        # Create table in docx
        if table_rows:
            table = doc.add_table(rows=1, cols=len(table_rows[0]))
            hdr_cells = table.rows[0].cells
            for i, hdr in enumerate(table_rows[0]):
                hdr_cells[i].text = hdr
            for data_row in table_rows[1:]:
                row_cells = table.add_row().cells
                for i, cell in enumerate(data_row):
                    row_cells[i].text = cell
        # Advance the outer loop index
        continue
    elif stripped:
        doc.add_paragraph(stripped)
    else:
        doc.add_paragraph('')

# Save the document
output_path = os.path.join(os.path.dirname(__file__), 'NoSQL_Assessment2_Report.docx')
doc.save(output_path)
print(f"Report generated at {output_path}")
