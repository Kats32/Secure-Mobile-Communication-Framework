"""Export the Markdown project explanation as a PDF using LibreOffice."""

from pathlib import Path
import re
import subprocess
from zipfile import ZIP_DEFLATED, ZipFile
from xml.etree import ElementTree as ET


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "PROJECT_EXPLANATION.md"
PDF = HERE / "PROJECT_EXPLANATION.pdf"
TEMP_DOCX = HERE / ".project_explanation_export.docx"
WORD = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
ET.register_namespace("w", WORD)


def tag(name):
    return f"{{{WORD}}}{name}"


def plain_text(text):
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    return text.replace("**", "").replace("`", "")


def add_paragraph(parent, text="", style=None):
    para = ET.SubElement(parent, tag("p"))
    props = ET.SubElement(para, tag("pPr"))
    if style:
        ET.SubElement(props, tag("pStyle")).set(tag("val"), style)
    run = ET.SubElement(para, tag("r"))
    ET.SubElement(run, tag("t")).text = plain_text(text)


def add_table(parent, rows):
    table = ET.SubElement(parent, tag("tbl"))
    props = ET.SubElement(table, tag("tblPr"))
    borders = ET.SubElement(props, tag("tblBorders"))
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        edge = ET.SubElement(borders, tag(side))
        edge.set(tag("val"), "single")
        edge.set(tag("sz"), "4")
        edge.set(tag("color"), "D9CBD3")
    count = max(map(len, rows))
    grid = ET.SubElement(table, tag("tblGrid"))
    for _ in range(count):
        ET.SubElement(grid, tag("gridCol")).set(tag("w"), str(9000 // count))
    for row_index, row in enumerate(rows):
        tr = ET.SubElement(table, tag("tr"))
        for col_index in range(count):
            cell = ET.SubElement(tr, tag("tc"))
            cell_props = ET.SubElement(cell, tag("tcPr"))
            width = ET.SubElement(cell_props, tag("tcW"))
            width.set(tag("w"), str(9000 // count))
            width.set(tag("type"), "dxa")
            if row_index == 0:
                ET.SubElement(cell_props, tag("shd")).set(tag("fill"), "F1E2EB")
            para = ET.SubElement(cell, tag("p"))
            run = ET.SubElement(para, tag("r"))
            if row_index == 0:
                ET.SubElement(ET.SubElement(run, tag("rPr")), tag("b"))
            value = row[col_index] if col_index < len(row) else ""
            ET.SubElement(run, tag("t")).text = plain_text(value)


def make_document():
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    document = ET.Element(tag("document"))
    body = ET.SubElement(document, tag("body"))
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        if line.startswith("```mermaid"):
            index += 1
            while index < len(lines) and not lines[index].startswith("```"):
                index += 1
            if index < len(lines):
                index += 1
            add_paragraph(body, "User → PySide6 interface → TCP client ⇄ TCP / newline JSON ⇄ Server", "Diagram")
            add_paragraph(body, "Interface: local accounts · chat · attack simulator · activity logs", "Diagram")
            add_paragraph(body, "Messaging: ECDH + HKDF · AES-256-GCM · RSA-PSS", "Diagram")
            continue
        if line.startswith("```"):
            index += 1
            while index < len(lines) and not lines[index].startswith("```"):
                add_paragraph(body, lines[index], "Code")
                index += 1
            index += 1
            continue
        heading = re.match(r"^(#{1,3})\s+(.*)", line)
        if heading:
            add_paragraph(body, heading.group(2), f"Heading{len(heading.group(1))}")
            index += 1
            continue
        if line.startswith("|"):
            rows = []
            while index < len(lines) and lines[index].startswith("|"):
                row = [cell.strip() for cell in lines[index].strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?", cell) for cell in row):
                    rows.append(row)
                index += 1
            if rows:
                add_table(body, rows)
                add_paragraph(body)
            continue
        if re.match(r"^-\s+", line):
            while index < len(lines) and re.match(r"^-\s+", lines[index]):
                add_paragraph(body, "•  " + re.sub(r"^-\s+", "", lines[index]))
                index += 1
            continue
        if re.match(r"^\d+\.\s+", line):
            while index < len(lines) and re.match(r"^\d+\.\s+", lines[index]):
                add_paragraph(body, re.sub(r"^\d+\.\s+", "", lines[index]))
                index += 1
            continue
        paragraph_lines = [line.strip()]
        index += 1
        while (index < len(lines) and lines[index].strip()
               and not lines[index].startswith(("#", "```", "|", "- "))
               and not re.match(r"^\d+\.\s+", lines[index])):
            paragraph_lines.append(lines[index].strip())
            index += 1
        add_paragraph(body, " ".join(paragraph_lines))

    section = ET.SubElement(body, tag("sectPr"))
    page = ET.SubElement(section, tag("pgSz"))
    page.set(tag("w"), "11906")
    page.set(tag("h"), "16838")
    margins = ET.SubElement(section, tag("pgMar"))
    for key, value in (("top", "850"), ("right", "850"), ("bottom", "850"), ("left", "850"), ("header", "425"), ("footer", "425")):
        margins.set(tag(key), value)
    return ET.tostring(document, encoding="utf-8", xml_declaration=True)


def make_styles():
    styles = ET.Element(tag("styles"))
    normal = ET.SubElement(styles, tag("style"), {tag("type"): "paragraph", tag("default"): "1", tag("styleId"): "Normal"})
    run_props = ET.SubElement(normal, tag("rPr"))
    fonts = ET.SubElement(run_props, tag("rFonts"))
    fonts.set(tag("ascii"), "Carlito")
    fonts.set(tag("hAnsi"), "Carlito")
    ET.SubElement(run_props, tag("sz")).set(tag("val"), "21")
    for level, size in ((1, "34"), (2, "28"), (3, "24")):
        style = ET.SubElement(styles, tag("style"), {tag("type"): "paragraph", tag("styleId"): f"Heading{level}"})
        props = ET.SubElement(style, tag("pPr"))
        ET.SubElement(props, tag("keepNext"))
        spacing = ET.SubElement(props, tag("spacing"))
        spacing.set(tag("before"), "240" if level == 1 else "180")
        spacing.set(tag("after"), "100")
        rpr = ET.SubElement(style, tag("rPr"))
        ET.SubElement(rpr, tag("b"))
        ET.SubElement(rpr, tag("color")).set(tag("val"), "54213F")
        ET.SubElement(rpr, tag("sz")).set(tag("val"), size)
    for name, size, align in (("Code", "18", None), ("Diagram", "21", "center")):
        style = ET.SubElement(styles, tag("style"), {tag("type"): "paragraph", tag("styleId"): name})
        props = ET.SubElement(style, tag("pPr"))
        if align:
            ET.SubElement(props, tag("jc")).set(tag("val"), align)
        if name == "Code":
            ET.SubElement(props, tag("shd")).set(tag("fill"), "F4F0F3")
        rpr = ET.SubElement(style, tag("rPr"))
        if name == "Code":
            fonts = ET.SubElement(rpr, tag("rFonts"))
            fonts.set(tag("ascii"), "Consolas")
            fonts.set(tag("hAnsi"), "Consolas")
        ET.SubElement(rpr, tag("sz")).set(tag("val"), size)
    return ET.tostring(styles, encoding="utf-8", xml_declaration=True)


def main():
    content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>'''
    root_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'''
    doc_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>'''
    with ZipFile(TEMP_DOCX, "w", ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", content_types)
        docx.writestr("_rels/.rels", root_rels)
        docx.writestr("word/document.xml", make_document())
        docx.writestr("word/styles.xml", make_styles())
        docx.writestr("word/_rels/document.xml.rels", doc_rels)
    try:
        subprocess.run([
            "libreoffice", "--headless", "--convert-to", "pdf",
            "--outdir", str(HERE), str(TEMP_DOCX),
        ], check=True)
        generated = HERE / ".project_explanation_export.pdf"
        generated.replace(PDF)
    finally:
        TEMP_DOCX.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
