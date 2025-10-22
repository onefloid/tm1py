from pathlib import Path
import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

api_map = {
    "Services": {
        "AnnotationService": "TM1py.Services.AnnotationService",
        "ApplicationService": "TM1py.Services.ApplicationService",
        "AuditLogService": "TM1py.Services.AuditLogService",
        "CellService": "TM1py.Services.CellService",
        "ChoreService": "TM1py.Services.ChoreService",
        "ConfigurationService": "TM1py.Services.ConfigurationService",
        "CubeService": "TM1py.Services.CubeService",
        "DimensionService": "TM1py.Services.DimensionService",
        "ElementService": "TM1py.Services.ElementService",
        "FileService": "TM1py.Services.FileService",
        "GitService": "TM1py.Services.GitService",
        "HierarchyService": "TM1py.Services.HierarchyService",
        "JobService": "TM1py.Services.JobService",
        "LoggerService": "TM1py.Services.LoggerService",
        "ManageService": "TM1py.Services.ManageService",
        "MessageLogService": "TM1py.Services.MessageLogService",
        "MonitoringService": "TM1py.Services.MonitoringService",
        "ObjectService": "TM1py.Services.ObjectService",
        "PowerBiService": "TM1py.Services.PowerBiService",
        "ProcessService": "TM1py.Services.ProcessService",
        "RestService": "TM1py.Services.RestService",
        "SandboxService": "TM1py.Services.SandboxService",
        "SecurityService": "TM1py.Services.SecurityService",
        "ServerService": "TM1py.Services.ServerService",
        "SessionService": "TM1py.Services.SessionService",
        "SubsetService": "TM1py.Services.SubsetService",
        "ThreadService": "TM1py.Services.ThreadService",
        "TM1Service": "TM1py.Services.TM1Service",
        "TransactionLogService": "TM1py.Services.TransactionLogService",
        "UserService": "TM1py.Services.UserService",
        "ViewService": "TM1py.Services.ViewService",
    },
    "Objects": {
        "Annotation": "TM1py.Objects.Annotation",
        "Application": "TM1py.Objects.Application",
        "Axis": "TM1py.Objects.Axis",
        "Chore": "TM1py.Objects.Chore",
        "ChoreFrequency": "TM1py.Objects.ChoreFrequency",
        "ChoreStartTime": "TM1py.Objects.ChoreStartTime",
        "ChoreTask": "TM1py.Objects.ChoreTask",
        "Cube": "TM1py.Objects.Cube",
        "Dimension": "TM1py.Objects.Dimension",
        "Element": "TM1py.Objects.Element",
        "ElementAttribute": "TM1py.Objects.ElementAttribute",
        "Git": "TM1py.Objects.Git",
        "GitCommit": "TM1py.Objects.GitCommit",
        "GitPlan": "TM1py.Objects.GitPlan",
        "GitProject": "TM1py.Objects.GitProject",
        "GitRemote": "TM1py.Objects.GitRemote",
        "Hierarchy": "TM1py.Objects.Hierarchy",
        "MDXView": "TM1py.Objects.MDXView",
        "NativeView": "TM1py.Objects.NativeView",
        "Process": "TM1py.Objects.Process",
        "ProcessDebugBreakpoint": "TM1py.Objects.ProcessDebugBreakpoint",
        "Rules": "TM1py.Objects.Rules",
        "Sandbox": "TM1py.Objects.Sandbox",
        "Server": "TM1py.Objects.Server",
        "Subset": "TM1py.Objects.Subset",
        "TM1Object": "TM1py.Objects.TM1Object",
        "User": "TM1py.Objects.User",
        "View": "TM1py.Objects.View",
    },
    "Extras": {
        "Exceptions": "TM1py.Exceptions.Exceptions",
        "Utils": "TM1py.Utils.Utils",
        "MDXUtils": "TM1py.Utils.MDXUtils",
    },
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
