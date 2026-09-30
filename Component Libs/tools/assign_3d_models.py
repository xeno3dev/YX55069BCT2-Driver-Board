"""Attach verified local/stock STEP models to the portable library and PCB.

Run after build_library.py when regenerating the project library.
"""
from pathlib import Path
import shutil
import subprocess

from sexpr import Quoted, parse, dump, children

base = Path(__file__).resolve().parents[1]
project = base.parent / "Kicad Project"
library = base / "YX55069BCT2.pretty"
shapes = base / "YX55069BCT2.3dshapes"
sources = base / "sources"
slate = Path(r"C:\Users\Aylon\GitHub\slate113-mk1\Kicad Project\slate113_libs\slate113.3dshapes")
pcb = project / "YX55069BCT2-Driver-Board.kicad_pcb"

# A stock KiCad model is used only when its footprint/body dimensions match.
stock = {
    "C0402": "Capacitor_SMD.3dshapes/C_0402_1005Metric.step",
    "C0603": "Capacitor_SMD.3dshapes/C_0603_1608Metric.step",
    "C0805": "Capacitor_SMD.3dshapes/C_0805_2012Metric.step",
    "CL05A105KA5NQNC": "Capacitor_SMD.3dshapes/C_0402_1005Metric.step",
    "C_0603_1608Metric": "Capacitor_SMD.3dshapes/C_0603_1608Metric.step",
    "R0402": "Resistor_SMD.3dshapes/R_0402_1005Metric.step",
    "R_0603_1608Metric": "Resistor_SMD.3dshapes/R_0603_1608Metric.step",
    "L_0603_1608Metric": "Inductor_SMD.3dshapes/L_0603_1608Metric.step",
    "HDMI_A_Amphenol_10029449-x01xLF_Horizontal": "Connector_Video.3dshapes/HDMI_A_Amphenol_10029449-x01xLF_Horizontal.step",
}
vendor = {
    "P-VFBGA-80_L7.0-W7.0-R10-C10-P0.65-TL": "tc358870_import.3dshapes/P-VFBGA-80_L7.0-W7.0-H0.9-R10-C10-P0.65-TL.step",
    "C1206": "C100122_import.3dshapes/C1206_L3.2-W1.6-H1.3.step",
    "CRYSTAL-SMD_4P-L3.2-W2.5-BL": "C1986736_import.3dshapes/CRYSTAL-SMD_4P-L3.2-W2.5-BL.step",
    "OSC-SMD_4P-L2.0-W1.6-BL": "OT7EL89CJI-111YLC-48M_import.3dshapes/OSC-SMD_4P-L2.0-W1.6-H0.8.step",
    "QFN-56_L7.0-W7.0-P0.40-TL-EP4.0": "C2913194_import.3dshapes/QFN-56_L7.0-W7.0-P0.40-TL-EP4.0.step",
    "SOD-123FL_L2.7-W1.8-LS3.8-RD": "C405304_import.3dshapes/SOD-123FL_L2.8-W1.8-H1.1-LS3.6.step",
    "SOT-23-3_L2.9-W1.6-P1.90-LS2.8-BR": "C112239_import.3dshapes/SOT-23-3L_L2.9-W1.6-H1.1-LS2.8-P0.95.step",
    "SOT-23-6_L2.9-W1.6-P0.95-LS2.8-BR": "C132604_import.3dshapes/SOT-23-6_L2.9-W1.6-H1.5-LS2.8-P0.95.step",
    "USON-10_L2.5-W1.0-P0.50-BL": "C138714_import.3dshapes/USON-10_L2.5-W1.0-H0.6-P0.50.step",
    "VQFN-10_L2.0-W2.0-P0.45-TL": "C2864845_import.3dshapes/VQFN-10_L2.0-W2.0-P0.45-TL.step",
    "WSON-6_L2.0-W2.0-P0.65-BL-EP": "TLV767_import.3dshapes/WSON-6_L2.0-W2.0-H0.8-P0.65.step",
    "WSON-6_L2.0-W2.0-P0.65-TL-EP": "TLV767_import.3dshapes/WSON-6_L2.0-W2.0-H0.8-P0.65.step",
    "WSON-8_L6.0-W5.0-P1.27-TL-EP": "C2982923_import.3dshapes/WSON-8_L6.0-W5.0-P1.27-TL-EP.step",
}

def model_for(name):
    if name in stock:
        path = Path(r"C:\Program Files\KiCad\10.0\share\kicad\3dmodels") / stock[name]
        assert path.is_file(), path
        return "${KICAD10_3DMODEL_DIR}/" + stock[name]
    if name == "USB-C-SMD_TYPE-C16PIN":
        source = slate / "USB-C-SMD_TYPE-C16PIN.step"
    elif name in vendor:
        source = sources / vendor[name]
    else:
        return None
    assert source.is_file(), source
    shapes.mkdir(exist_ok=True)
    target = shapes / source.name
    if not target.exists():
        shutil.copy2(source, target)
    return "${KIPRJMOD}/../Component Libs/YX55069BCT2.3dshapes/" + target.name

def rotation_for(name):
    if name not in vendor:
        return "0"
    source_fp = sources / (vendor[name].split("/", 1)[0].replace(".3dshapes", ".pretty")) / (name + ".kicad_mod")
    if not source_fp.is_file():
        return "0"
    source_node = parse(source_fp.read_text(encoding="utf-8"))
    models = children(source_node, "model")
    if not models:
        return "0"
    rotation = children(models[0], "rotate")
    return str(rotation[0][1][3]) if rotation else "0"

def add_model(node, path, name):
    if children(node, "model"):
        return False
    node.append(["model", Quoted(path),
                 ["offset", ["xyz", "0", "0", "0"]],
                 ["scale", ["xyz", "1", "1", "1"]],
                 ["rotate", ["xyz", "0", "0", rotation_for(name)]]])
    return True

assigned = set()
for path in library.glob("*.kicad_mod"):
    model = model_for(path.stem)
    if model:
        node = parse(path.read_text(encoding="utf-8"))
        node[:] = [x for x in node if not (isinstance(x, list) and x and x[0] == "model"
                                      and str(x[1]) == model)]
        if add_model(node, model, path.stem):
            path.write_text(dump(node) + "\n", encoding="utf-8")
        assigned.add(path.stem)

def footprint_ranges(text):
    """Yield exact top-level footprint spans without reformatting the board."""
    i = 0
    while True:
        start = text.find('\n\t(footprint ', i)
        if start < 0:
            return
        start += 2
        depth, quoted, escaped = 0, False, False
        for end in range(start, len(text)):
            c = text[end]
            if quoted:
                if escaped:
                    escaped = False
                elif c == '\\':
                    escaped = True
                elif c == '"':
                    quoted = False
            elif c == '"':
                quoted = True
            elif c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    yield start, end + 1
                    i = end + 1
                    break

board_text = pcb.read_text(encoding="utf-8")
# Recover KiCad's original formatting if an earlier run of this helper used
# dump() on the whole board. Only do so when every non-model node is identical.
original_text = subprocess.check_output(
    ["git", "show", "HEAD:Kicad Project/YX55069BCT2-Driver-Board.kicad_pcb"],
    cwd=base.parent,
).decode("utf-8")
current_tree = parse(board_text)
original_tree = parse(original_text)
for fp in children(current_tree, "footprint"):
    fp[:] = [x for x in fp if not (isinstance(x, list) and x and x[0] == "model"
                                  and str(fp[1]).startswith("YX55069BCT2:"))]
if current_tree == original_tree:
    board_text = original_text
updated = 0
unresolved = set()
replacements = []
for start, end in footprint_ranges(board_text):
    original = board_text[start:end]
    fp = parse(original)
    if not str(fp[1]).startswith("YX55069BCT2:") or children(fp, "model"):
        continue
    name = str(fp[1]).split(":", 1)[1]
    model = model_for(name)
    if model is None:
        unresolved.add(name)
        continue
    block = ('\n\t\t(model "' + model + '"\n'
             '\t\t\t(offset (xyz 0 0 0))\n'
             '\t\t\t(scale (xyz 1 1 1))\n'
             '\t\t\t(rotate (xyz 0 0 ' + rotation_for(name) + '))\n\t\t)')
    replacements.append((end - 3, block))
    updated += 1
for at, block in reversed(replacements):
    board_text = board_text[:at] + block + board_text[at:]
if replacements:
    pcb.write_text(board_text, encoding="utf-8")
print(f"Assigned {len(assigned)} library models and {updated} board instances")
print("Still missing:", ", ".join(sorted(unresolved)) or "none")
