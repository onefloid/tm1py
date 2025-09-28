from pathlib import Path
import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

api_map = {
    "Services": {
        "CubeService": "TM1py.Services.CubeService",
        "DimensionService": "TM1py.Services.DimensionService",
    },
    "Objects": {
        "Cube": "TM1py.Objects.Cube",
        "Dimension": "TM1py.Objects.Dimension",
    },
}

for category, entries in api_map.items():
    for name, import_path in entries.items():
        # Kein "docs/" Prefix – direkt relativer Pfad
        filename = Path("reference") / category.lower() / f"{name.lower()}.md"

        # Stub schreiben
        with mkdocs_gen_files.open(filename, "w") as f:
            f.write(f"# {name}\n\n")
            f.write(f"::: {import_path}\n")

        # Navigationseintrag
        rel_filename = Path(*filename.parts[1:])
        nav["API Reference", category, name] = rel_filename

# SUMMARY für mkdocs
with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
