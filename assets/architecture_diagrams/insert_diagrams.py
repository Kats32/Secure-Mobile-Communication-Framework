"""Embed the generated architecture PNGs at their corresponding report sections."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from xml.etree import ElementTree as ET
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "Secure_Mobile_Communication_Framework_Report.docx"
ASSETS = Path(__file__).parent
NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
}
for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)


def tag(ns, name):
    return f"{{{NS[ns]}}}{name}"


def paragraph_text(p):
    return "".join(t.text or "" for t in p.findall(".//w:t", NS))


def image_paragraph(rel_id, number, name, cx, cy):
    p = ET.Element(tag("w", "p"))
    ppr = ET.SubElement(p, tag("w", "pPr"))
    jc = ET.SubElement(ppr, tag("w", "jc")); jc.set(tag("w", "val"), "center")
    run = ET.SubElement(p, tag("w", "r"))
    drawing = ET.SubElement(run, tag("w", "drawing"))
    inline = ET.SubElement(drawing, tag("wp", "inline"))
    inline.set("distT", "0"); inline.set("distB", "0"); inline.set("distL", "0"); inline.set("distR", "0")
    extent = ET.SubElement(inline, tag("wp", "extent")); extent.set("cx", str(cx)); extent.set("cy", str(cy))
    docpr = ET.SubElement(inline, tag("wp", "docPr")); docpr.set("id", str(number)); docpr.set("name", name)
    frame = ET.SubElement(inline, tag("wp", "cNvGraphicFramePr"))
    ET.SubElement(frame, tag("a", "graphicFrameLocks")).set("noChangeAspect", "1")
    graphic = ET.SubElement(inline, tag("a", "graphic"))
    data = ET.SubElement(graphic, tag("a", "graphicData")); data.set("uri", NS["pic"])
    pic = ET.SubElement(data, tag("pic", "pic"))
    nv = ET.SubElement(pic, tag("pic", "nvPicPr"))
    cnv = ET.SubElement(nv, tag("pic", "cNvPr")); cnv.set("id", "0"); cnv.set("name", name)
    ET.SubElement(nv, tag("pic", "cNvPicPr"))
    fill = ET.SubElement(pic, tag("pic", "blipFill"))
    blip = ET.SubElement(fill, tag("a", "blip")); blip.set(tag("r", "embed"), rel_id)
    stretch = ET.SubElement(fill, tag("a", "stretch")); ET.SubElement(stretch, tag("a", "fillRect"))
    sp = ET.SubElement(pic, tag("pic", "spPr"))
    xfrm = ET.SubElement(sp, tag("a", "xfrm")); ET.SubElement(xfrm, tag("a", "off")).attrib.update(x="0", y="0")
    ET.SubElement(xfrm, tag("a", "ext")).attrib.update(cx=str(cx), cy=str(cy))
    geom = ET.SubElement(sp, tag("a", "prstGeom")); geom.set("prst", "rect"); ET.SubElement(geom, tag("a", "avLst"))
    return p


def main():
    with ZipFile(DOC) as zin:
        files = {item.filename: zin.read(item.filename) for item in zin.infolist()}
    doc = ET.fromstring(files["word/document.xml"])
    rels = ET.fromstring(files["word/_rels/document.xml.rels"])
    rel_ns = "http://schemas.openxmlformats.org/package/2006/relationships"
    targets = [
        ("system_architecture", "System ArchitectureReplace this box with the final architecture diagram"),
        ("registration_flow", "Registration Form → Generate Salt"),
        ("secure_message_workflow", "Authentication → ECDH Key Exchange"),
        ("attack_simulation", "Attack SimulatorInsert final project screenshot/diagram here"),
    ]
    body = doc.find("w:body", NS)
    parents = {child: parent for parent in doc.iter() for child in parent}
    paragraphs = doc.findall(".//w:p", NS)
    next_id = max([int(el.get("id", "0")) for el in rels], default=0) + 1
    image_num = 1
    for name, marker in targets:
        found = next((p for p in paragraphs if marker in paragraph_text(p)), None)
        if found is None:
            raise RuntimeError(f"Could not locate insertion point for {name}")
        rel_id = f"rId{next_id}"; next_id += 1
        rel = ET.SubElement(rels, f"{{{rel_ns}}}Relationship")
        rel.attrib.update(Id=rel_id, Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image", Target=f"media/{name}.png")
        image = ASSETS / f"{name}.png"
        files[f"word/media/{name}.png"] = image.read_bytes()
        # Keep a report-friendly width of 6.35 inches; preserve the artwork's aspect ratio.
        width = 5_806_800
        if name == "secure_message_workflow": width = 5_705_000
        if name == "attack_simulation": width = 5_760_000
        height = int(width * (image_height := {"system_architecture":460,"registration_flow":480,"secure_message_workflow":480,"attack_simulation":490}[name]) / ({"system_architecture":1060,"registration_flow":1060,"secure_message_workflow":1040,"attack_simulation":1050}[name]))
        pic_p = image_paragraph(rel_id, image_num, f"{name}.png", width, height); image_num += 1
        parent = parents[found]
        if "PLACEHOLDER" in paragraph_text(found):
            # Strip the placeholder text and replace its paragraph with the diagram.
            idx = list(parent).index(found); parent.remove(found); parent.insert(idx, pic_p)
        else:
            idx = list(parent).index(found); parent.insert(idx + 1, pic_p)
    files["word/document.xml"] = ET.tostring(doc, encoding="utf-8", xml_declaration=True)
    files["word/_rels/document.xml.rels"] = ET.tostring(rels, encoding="utf-8", xml_declaration=True)
    types = ET.fromstring(files["[Content_Types].xml"])
    ct_ns = "http://schemas.openxmlformats.org/package/2006/content-types"
    if not any(el.get("Extension") == "png" for el in types):
        ET.SubElement(types, f"{{{ct_ns}}}Default", Extension="png", ContentType="image/png")
    files["[Content_Types].xml"] = ET.tostring(types, encoding="utf-8", xml_declaration=True)
    with tempfile.NamedTemporaryFile(dir=ROOT, suffix=".docx", delete=False) as temp:
        temp_path = Path(temp.name)
    try:
        with ZipFile(temp_path, "w", ZIP_DEFLATED) as zout:
            for name, data in files.items(): zout.writestr(name, data)
        shutil.move(temp_path, DOC)
    finally:
        temp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
