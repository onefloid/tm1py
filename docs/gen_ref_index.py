from pathlib import Path
import mkdocs_gen_files

# Build a navigation entry for all files in docs/reference
nav = mkdocs_gen_files.Nav()

for path in sorted(Path("docs/reference").glob("*.md")):
    doc_path = path.relative_to("docs/reference")
    print(doc_path)
    if doc_path.name == "index.md":
        continue
    nav[doc_path.stem.title()] = doc_path

# Write the auto-generated index.md
with mkdocs_gen_files.open("reference/index.md", "w") as f:
    f.write("# API Reference\n\n")
    f.writelines(nav.build_literate_nav())

