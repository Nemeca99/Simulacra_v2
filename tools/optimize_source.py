import ast
from pathlib import Path
from typing import Set


def get_unused_imports(file_path: Path) -> Set[str]:
    """Find unused imports in Python files"""
    with open(file_path) as f:
        tree = ast.parse(f.read())

    imports = set()
    used = set()

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for name in node.names:
                imports.add(name.name)
        elif isinstance(node, ast.Name):
            used.add(node.id)

    return imports - used


def optimize_sources() -> None:
    """Analyze and optimize Python source files"""
    project_root = Path(__file__).parent.parent

    for py_file in project_root.rglob("*.py"):
        if py_file.parent.name == "tests":
            continue

        try:
            unused = get_unused_imports(py_file)
            if unused:
                print(f"\nUnused imports in {py_file.relative_to(project_root)}:")
                for imp in unused:
                    print(f"  - {imp}")
        except SyntaxError:
            continue
