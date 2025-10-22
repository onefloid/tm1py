from pathlib import Path
import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

api_map = {
    "Services": {
        "AnnotationService": "TM1py.Services.AnnotationService",
        "CubeService": "TM1py.Services.CubeService",
        "DimensionService": "TM1py.Services.DimensionService",
        "SubsetService": "TM1py.Services.SubsetService",
        "ViewService": "TM1py.Services.ViewService",
    },
    "Objects": {
        "Annotation": "TM1py.Objects.Annotation",
        "Cube": "TM1py.Objects.Cube",
        "Chore": "TM1py.Objects.Chore",
        "Dimension": "TM1py.Objects.Dimension",
        "Subset": "TM1py.Objects.Subset",
        "View": "TM1py.Objects.View",
    },
    "Extras": {
        "Exceptions": "TM1py.Exceptions.Exceptions",
        "Utils": "TM1py.Utils.Utils",
        "MDXUtils": "TM1py.Utils.MDXUtils"
    }
}

for category, entries in api_map.items():
    for name, import_path in entries.items():
        # Kein "docs/" Prefix – direkt relativer Pfad
        filename = Path("reference") / category.lower() / f"{name.lower()}.md"

        # Stub schreiben
        with mkdocs_gen_files.open(filename, "w") as f:
            f.write(f"<!-- {name}-->\n\n")
            f.write(f"::: {import_path}\n")

        # Navigationseintrag
        rel_filename = Path(*filename.parts[1:])
        nav[category, name] = rel_filename

# SUMMARY für mkdocs
with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())


with mkdocs_gen_files.open("reference/index.md", "w") as f:
    f.write("# API Reference\n\n")
    f.write("Welcome to the API Reference section. Please select a category on the left.\n")
    
    # TODO: Add menu
    # for item in nav.items():
    #     print(item)
