import os
import sys

try:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
    from docx.shared import Pt, Inches, RGBColor
    from docx.oxml.shared import OxmlElement
    from docx.oxml.ns import qn
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx"])
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
    from docx.shared import Pt, Inches, RGBColor
    from docx.oxml.shared import OxmlElement
    from docx.oxml.ns import qn

def set_page_borders(doc):
    for sec in doc.sections:
        sectPr = sec._sectPr
        pgBorders = OxmlElement('w:pgBorders')
        pgBorders.set(qn('w:offsetFrom'), 'page')
        for border_name in ['top', 'left', 'bottom', 'right']:
            border = OxmlElement(f'w:{border_name}')
            border.set(qn('w:val'), 'single')
            border.set(qn('w:sz'), '12')
            border.set(qn('w:space'), '24')
            border.set(qn('w:color'), '000000')
            pgBorders.append(border)
        sectPr.append(pgBorders)

def add_page_number(doc):
    for section in doc.sections:
        footer = section.footer
        p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run = p.add_run("Page ")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        
        fldChar1 = OxmlElement('w:fldChar')
        fldChar1.set(qn('w:fldCharType'), 'begin')
        instrText = OxmlElement('w:instrText')
        instrText.set(qn('xml:space'), 'preserve')
        instrText.text = "PAGE"
        fldChar2 = OxmlElement('w:fldChar')
        fldChar2.set(qn('w:fldCharType'), 'end')
        
        run._r.append(fldChar1)
        run._r.append(instrText)
        run._r.append(fldChar2)

def set_font(run, bold=False, size=12, font_name='Times New Roman'):
    run.font.name = font_name
    run.font.size = Pt(size)
    run.bold = bold

def add_centered(doc, text, bold=False, size=12, color=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    set_font(run, bold, size)
    if color:
        run.font.color.rgb = color
    return p

def add_justified(doc, text, bold=False, size=12):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run = p.add_run(text)
    set_font(run, bold, size)
    return p

doc = Document()
style = doc.styles['Normal']
font = style.font
font.name = 'Times New Roman'
font.size = Pt(12)

set_page_borders(doc)
add_page_number(doc)

logo_path = r"C:\Users\vssra\.gemini\antigravity\brain\0e8e167d-749c-4d29-80e4-5091e04f16ba\.user_uploaded\media_1791003322831_803a58c1.png"

# --- Page 1: Cover ---
add_centered(doc, "Rice Variety Classification Using Lightweight Machine Learning\n", bold=True, size=16, color=RGBColor(128,0,0))
add_centered(doc, "A Project Report submitted in fulfillment of the requirements for the Machine Learning Project\n", bold=True, size=12)
add_centered(doc, "BACHELOR OF TECHNOLOGY\nIN\nDEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING(AI&ML)\n", bold=True, size=14)
add_centered(doc, "Submitted by\n", bold=False, size=12)

team_list_cover = "MALLADI VENKATA SUBRAHMANYA SRAVAN (A24126552268)\nDWARAPUDI SUSWETHA (A24126552079)\nROHITH GURUGUBELLI (A24126552112)\nKOYYA APPALA REDDY (A24126552089)\n"
add_centered(doc, team_list_cover, bold=False, size=12)

add_centered(doc, "Under the guidance of\nDr. Appala Srinuvasu Muttipati\nAssociate Professor\n", bold=True, size=12)

if os.path.exists(logo_path):
    p_logo = doc.add_paragraph()
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_logo = p_logo.add_run()
    run_logo.add_picture(logo_path, width=Inches(2.0))

p_dept = add_centered(doc, "\nDEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING(AI&ML)\nANIL NEERUKONDA INSTITUTE OF TECHNOLOGY AND SCIENCES\n(UGC AUTONOMOUS)", bold=True, size=12)
p_acc = add_centered(doc, "(Permanently Affiliated to AU, Approved by AICTE and Accredited by NBA & NAAC with 'A+' Grade)\nSangivalasa, bheemili mandal, visakhapatnam dist.(A.P)\n2026-2027", bold=False, size=10)

p_dept.paragraph_format.space_after = Pt(0)
p_dept.paragraph_format.space_before = Pt(0)
p_acc.paragraph_format.space_after = Pt(0)
p_acc.paragraph_format.space_before = Pt(0)

doc.add_page_break()

# --- Page 2: Certificate ---
if os.path.exists(logo_path):
    p_logo2 = doc.add_paragraph()
    p_logo2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_logo2 = p_logo2.add_run()
    run_logo2.add_picture(logo_path, width=Inches(2.0))

p_cert = add_centered(doc, "\nANITS CERTIFICATE\n", bold=True, size=16)
p_cert.paragraph_format.keep_with_next = True

cert_text = "This is to certify that the project report entitled “RICE VARIETY CLASSIFICATION USING LIGHTWEIGHT MACHINE LEARNING” submitted by 1. MALLADI VENKATA SUBRAHMANYA SRAVAN (Regd No. A24126552268), 2. DWARAPUDI SUSWETHA (Regd No. A24126552079), 3. ROHITH GURUGUBELLI (Regd No. A24126552112), 4. KOYYA APPALA REDDY (Regd No. A24126552089), in fulfillment of the requirements for the Machine Learning Project in the Department of Computer Science and Engineering (AI&ML) during the year 2026-2027 of Anil Neerukonda Institute of Technology and Sciences (A+), Visakhapatnam, is a record of bonafide work to be carried out under the guidance and supervision named below, pending review and signature."
add_justified(doc, cert_text)

doc.add_paragraph("\n\n\n")

table = doc.add_table(rows=1, cols=2)
table.autofit = True
row = table.rows[0].cells
row[0].text = "PROJECT GUIDE\nDr. Appala Srinuvasu Muttipati\nASSOCIATE PROFESSOR\nDEPARTMENT OF CSE (AI&ML)\nANITS"
row[1].text = "HEAD OF THE DEPARTMENT\nDr K. SELVANI DEEPTHI\nDEPARTMENT OF CSE (AI&ML)\nANITS"

for cell in row:
    for par in cell.paragraphs:
        for run in par.runs:
            set_font(run, bold=True, size=12)

doc.add_page_break()

# --- Page 3: Declaration ---
p_decl = add_centered(doc, "DECLARATION\n", bold=True, size=16)
p_decl.paragraph_format.keep_with_next = True
decl_text1 = "We hereby declare that the project report entitled “RICE VARIETY CLASSIFICATION USING LIGHTWEIGHT MACHINE LEARNING”, submitted for the Machine Learning Project, is a record of original work carried out by us under the guidance of Dr. Appala Srinuvasu Muttipati, Associate Professor, Department of Computer Science and Engineering (AI&ML). The implementation, experiments, and results reported were produced and verified by us; all external ideas, definitions and results drawn from published sources have been acknowledged in the References section."
add_justified(doc, decl_text1)

decl_text2 = "We further declare that this report has not been submitted, in full or in part, for the award of any other degree, diploma, or similar title to this or any other institution."
add_justified(doc, decl_text2)

p_names = doc.add_paragraph()
run_names = p_names.add_run("\n\nPlace: Visakhapatnam\nDate: 19-09-2026\n\nMALLADI VENKATA SUBRAHMANYA SRAVAN (A24126552268)\nDWARAPUDI SUSWETHA (A24126552079)\nROHITH GURUGUBELLI (A24126552112)\nKOYYA APPALA REDDY (A24126552089)")
set_font(run_names, size=12)

doc.add_page_break()

# --- Page 4: Acknowledgement ---
p_ack = add_centered(doc, "ACKNOWLEDGEMENT\n", bold=True, size=16)
p_ack.paragraph_format.keep_with_next = True

ack_text1 = "We express our sincere gratitude to our project guide, Dr. Appala Srinuvasu Muttipati, Associate Professor, Department of CSE (AI&ML), for his valuable guidance, continuous encouragement, and constructive feedback throughout this project. His insistence on precise reasoning at every step shaped the way we approached this work from the outset."
add_justified(doc, ack_text1)

ack_text2 = "We thank Dr. K. Selvani Deepthi, Head of the Department, for providing the departmental resources, laboratory access, and environment necessary to carry out this work, and for fostering a culture in the department where this kind of applied, project-driven learning is encouraged. We are equally grateful to all the faculty members of the Department of Computer Science and Engineering (AI&ML) for their valuable advice and encouragement."
add_justified(doc, ack_text2)

ack_text3 = "Finally, we thank our classmates for the many useful discussions during the course of this project, and our families for their patience and support throughout the duration of this work."
add_justified(doc, ack_text3)

p_names_ack = doc.add_paragraph()
run_names_ack = p_names_ack.add_run("\n\nTEAM MEMBERS\n\nMALLADI VENKATA SUBRAHMANYA SRAVAN (A24126552268)\nDWARAPUDI SUSWETHA (A24126552079)\nROHITH GURUGUBELLI (A24126552112)\nKOYYA APPALA REDDY (A24126552089)")
set_font(run_names_ack, size=12)

doc.add_page_break()

# --- NEW FORMATTED TABLE OF CONTENTS ---
p_toc_title = doc.add_paragraph()
p_toc_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
run_title = p_toc_title.add_run("TABLE OF CONTENTS")
run_title.bold = True
run_title.font.size = Pt(16)
run_title.font.name = 'Times New Roman'
run_title.font.color.rgb = RGBColor(23, 54, 93) # Dark Blue matching the image
p_toc_title.paragraph_format.keep_with_next = True

# Add bottom border to TOC title
pBdr = OxmlElement('w:pBdr')
bottom = OxmlElement('w:bottom')
bottom.set(qn('w:val'), 'single')
bottom.set(qn('w:sz'), '12')
bottom.set(qn('w:space'), '4')
bottom.set(qn('w:color'), '17365D') # Dark blue border
pBdr.append(bottom)
p_toc_title._p.get_or_add_pPr().append(pBdr)

doc.add_paragraph() # Add some spacing

toc_items = [
    ("1. Problem statement", "6"),
    ("2. Dataset", "6"),
    ("3. Exploratory data analysis", "6"),
    ("4. Baseline model comparison", "7"),
    ("5. Feature selection", "7"),
    ("6. Lightweight model comparison", "8"),
    ("7. Final model", "8"),
    ("8. Error analysis and limitations", "9"),
    ("9. OUTPUTS AND EXPERIMENTAL RESULTS", "10"),
    ("10. APPENDIX: SOURCE CODE IMPLEMENTATION", "11"),
    ("11. Conclusion", "12")
]

for item, page_num in toc_items:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(8)
    tab_stops = p.paragraph_format.tab_stops
    # Right-aligned tab at 6.5 inches with dotted leader
    tab_stops.add_tab_stop(Inches(6.5), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
    
    run = p.add_run(f"{item}\t{page_num}")
    run.bold = True
    run.font.size = Pt(11)
    run.font.name = 'Times New Roman'

doc.add_page_break()

# --- Page 5: Project Content ---
base_dir = r"D:\Machine Learning Project\rice_classification_project"
with open(os.path.join(base_dir, "PROJECT_REPORT.md"), "r", encoding="utf-8") as f:
    content = f.read()

lines = content.split('\n')
i = 0
conclusion_lines = []
in_conclusion = False

while i < len(lines):
    line = lines[i].strip()
    
    if line.startswith('## 9. Conclusion'):
        in_conclusion = True
        conclusion_lines.append(line.replace('9. Conclusion', '11. Conclusion'))
        i += 1
        continue
    
    if in_conclusion:
        conclusion_lines.append(line)
        i += 1
        continue
    
    # Process markdown tables natively into docx 'Table Grid'
    if line.startswith('|'):
        table_lines = []
        while i < len(lines) and lines[i].strip().startswith('|'):
            table_lines.append(lines[i].strip())
            i += 1
        
        data_rows = []
        for t_line in table_lines:
            if '---' in t_line:
                continue
            cells = [c.strip() for c in t_line.split('|')]
            if cells and cells[0] == '': cells.pop(0)
            if cells and cells[-1] == '': cells.pop(-1)
            data_rows.append(cells)
        
        if data_rows:
            num_cols = max(len(row) for row in data_rows)
            md_table = doc.add_table(rows=len(data_rows), cols=num_cols)
            md_table.style = 'Table Grid'
            for r_idx, row_data in enumerate(data_rows):
                for c_idx, cell_text in enumerate(row_data):
                    if c_idx < len(md_table.rows[r_idx].cells):
                        cell = md_table.cell(r_idx, c_idx)
                        cell.text = cell_text
                        for paragraph in cell.paragraphs:
                            for run in paragraph.runs:
                                set_font(run, bold=(r_idx == 0), size=12)
        continue

    elif line.startswith('# '):
        h = doc.add_heading(level=1)
        h.paragraph_format.keep_with_next = True
        run = h.add_run(line.replace('# ', ''))
        set_font(run, bold=True, size=16)
        run.font.color.rgb = RGBColor(0,0,128)
    elif line.startswith('## '):
        h = doc.add_heading(level=2)
        h.paragraph_format.keep_with_next = True
        run = h.add_run(line.replace('## ', ''))
        set_font(run, bold=True, size=14)
        run.font.color.rgb = RGBColor(0,0,128)
    elif line.startswith('### '):
        h = doc.add_heading(level=3)
        h.paragraph_format.keep_with_next = True
        run = h.add_run(line.replace('### ', ''))
        set_font(run, bold=True, size=12)
        run.font.color.rgb = RGBColor(0,0,128)
    elif line != "" and not line.startswith('-'):
        add_justified(doc, line)
    elif line.startswith('-'):
        p = doc.add_paragraph(style='List Bullet')
        run = p.add_run(line[1:].strip())
        set_font(run, size=12)
    
    i += 1

doc.add_page_break()

# --- Outputs and Images ---
h = doc.add_heading(level=1)
h.paragraph_format.keep_with_next = True
run = h.add_run("OUTPUTS AND EXPERIMENTAL RESULTS")
set_font(run, bold=True, size=16)
run.font.color.rgb = RGBColor(0,0,128)

figures_dir = os.path.join(base_dir, "outputs", "figures")
if os.path.exists(figures_dir):
    for img_file in sorted(os.listdir(figures_dir)):
        if img_file.endswith(".png"):
            h2 = doc.add_heading(level=2)
            h2.paragraph_format.keep_with_next = True
            run = h2.add_run(img_file)
            set_font(run, bold=True, size=14)
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run_img = p_img.add_run()
            try:
                run_img.add_picture(os.path.join(figures_dir, img_file), width=Inches(5))
            except Exception as e:
                doc.add_paragraph(f"[Image {img_file} could not be loaded: {e}]")
            doc.add_paragraph()

doc.add_page_break()

# --- Code and Programs ---
h = doc.add_heading(level=1)
h.paragraph_format.keep_with_next = True
run = h.add_run("APPENDIX: SOURCE CODE IMPLEMENTATION")
set_font(run, bold=True, size=16)
run.font.color.rgb = RGBColor(0,0,128)

code_files = ["run_project.py", "predict_rice.py"]
for cf in code_files:
    cf_path = os.path.join(base_dir, cf)
    if os.path.exists(cf_path):
        h2 = doc.add_heading(level=2)
        h2.paragraph_format.keep_with_next = True
        run = h2.add_run(cf)
        set_font(run, bold=True, size=14)
        with open(cf_path, "r", encoding="utf-8") as src:
            code_text = src.read()
        p = doc.add_paragraph()
        run_code = p.add_run(code_text)
        set_font(run_code, size=10, font_name='Courier New')
        doc.add_page_break()

# --- Conclusion at the very end ---
for line in conclusion_lines:
    if line.startswith('## '):
        h = doc.add_heading(level=1)
        h.paragraph_format.keep_with_next = True
        run = h.add_run(line.replace('## ', ''))
        set_font(run, bold=True, size=16)
        run.font.color.rgb = RGBColor(0,0,128)
    elif line != "":
        add_justified(doc, line)

doc.save(os.path.join(base_dir, "Final_Project_Report_v4.docx"))
print("Report v4 regenerated perfectly matching the image TOC style.")
