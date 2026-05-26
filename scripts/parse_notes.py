import os
import re
import subprocess
import json
import shutil

# List of projects
PROJECTS = [
    {"id": "660a34dc98394a7ad6c3947e", "title": "Discrete Mathematics"},
    {"id": "6609d37779e4eaf2ae58e4e5", "title": "Abstract Algebra"},
    {"id": "6609d18949d2d5df48ead5f5", "title": "Linear Algebra"},
    {"id": "6609d31579e4eaf2ae58ccae", "title": "Commutative Algebra"},
    {"id": "6609d04373a2d4415454e7b3", "title": "Group Algebras"},
    {"id": "6609a1405fc8a1ebb3d13cb4", "title": "Lie Algebras"},
    {"id": "6609d278a8f132e4d3239090", "title": "Category Theory"},
    {"id": "660a74d8a58796580dcddda9", "title": "Real Analysis"},
    {"id": "660adb531645d8f5a06d1b1c", "title": "Complex Analysis"},
    {"id": "660ae12af96d65c9b0092d8a", "title": "Functional Analysis"},
    {"id": "660aee636411044ef54a4135", "title": "Differential Equations"},
    {"id": "660aeabb1369f317085b9d94", "title": "Dynamical Systems"},
    {"id": "660a52208f63f06d39471f6c", "title": "Topological Spaces"},
    {"id": "660a44e4c1db7ab7be81543c", "title": "Algebraic Topology"},
    {"id": "660a4d551a5dec8a20706024", "title": "Differential Topology"},
    {"id": "660a546949d2d5df480098c2", "title": "Algebraic Geometry"},
    {"id": "660a3ed4717a06ecc6733921", "title": "Differential Geometry"},
    {"id": "65fd0b42cf8cf5e0e4b505ef", "title": "Quantum Algebras"},
    {"id": "6609c85960acd1a3ec1e7da6", "title": "Quantum Systems"},
    {"id": "679c461fa3ce494f024f6065", "title": "Machine Learning"}
]

BASE_DIR = "projects_temp"
OUTPUT_DIR = "data/notes_content"
MANIFEST_PATH = "data/manifest.json"

if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)
os.makedirs(OUTPUT_DIR, exist_ok=True)

manifest = {"projects": []}

def run_latexml(preamble, body, filename):
    tmp_tex = "tmp.tex"
    full_tex = r"\documentclass{amsart}" + "\n" + preamble + "\n" + r"\begin{document}" + "\n" + body + "\n" + r"\end{document}"
    
    with open(tmp_tex, "w", encoding="utf-8") as f:
        f.write(full_tex)
    
    output_file = os.path.join(OUTPUT_DIR, filename)
    try:
        # Convert to XML then to HTML5
        subprocess.run(["latexml", "--dest=tmp.xml", tmp_tex], check=True, capture_output=True)
        subprocess.run(["latexmlpost", "--format=html5", "--nodefaultcss", "--dest=" + output_file, "tmp.xml"], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"Error processing {filename}: {e}")
    return filename

for proj in PROJECTS:
    proj_path = os.path.join(BASE_DIR, proj["id"])
    main_tex = os.path.join(proj_path, "main.tex")
    preamble_tex = os.path.join(proj_path, "mypreamble.tex")
    
    if not os.path.exists(main_tex): continue

    preamble_content = ""
    if os.path.exists(preamble_tex):
        with open(preamble_tex, "r", encoding="utf-8") as f:
            preamble_content = f.read()

    with open(main_tex, "r", encoding="utf-8") as f:
        content = f.read()

    proj_data = {"title": proj["title"], "sections": []}
    sections = re.split(r'\\section\{', content)[1:]
    
    for i, sec_text in enumerate(sections):
        sec_title = sec_text.split('}')[0]
        sec_obj = {"name": sec_title, "subsections": []}
        subsections = re.split(r'\\subsection\{', sec_text)[1:]
        
        for j, subsec_text in enumerate(subsections):
            subsec_title = subsec_text.split('}')[0]
            subsec_body = subsec_text.split('}', 1)[1].replace(r"\end{document}", "")
            
            file_name = f"{proj['id']}_{i}_{j}.html"
            run_latexml(preamble_content, subsec_body, file_name)
            
            sec_obj["subsections"].append({"name": subsec_title, "file": file_name})
        
        proj_data["sections"].append(sec_obj)
    manifest["projects"].append(proj_data)

with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)