import os
import ast
from pathlib import Path

# Configuration
ROOT_DIR = Path(".").resolve()
OUTPUT_FILE = f"{ROOT_DIR.name}_LLM_readable.md"

INCLUDE_EXTENSIONS = {".py", ".md", ".txt", ".yaml", ".yml", ".json", ".toml", ".csv"}
SKIP_DIRS = {".git", "__pycache__", ".mypy_cache", ".venv", "env", "venv", ".idea", ".vscode"}
INDENT = "    "


def should_include_file(file_path: Path):
    return file_path.suffix in INCLUDE_EXTENSIONS


def generate_tree_structure(root: Path) -> str:
    tree_lines = ["# Repository Structure\n"]

    def _walk(path: Path, prefix=""):
        dir_entries = [p for p in path.iterdir() if p.is_dir() and p.name not in SKIP_DIRS]
        file_entries = [p for p in path.iterdir() if p.is_file() and should_include_file(p)]
        entries = sorted(dir_entries + file_entries, key=lambda p: p.name.lower())
        for i, entry in enumerate(entries):
            connector = "└── " if i == len(entries) - 1 else "├── "
            tree_lines.append(f"{prefix}{connector}{entry.name}{ '/' if entry.is_dir() else ''}")
            if entry.is_dir():
                extension = "    " if i == len(entries) - 1 else "│   "
                _walk(entry, prefix + extension)

    _walk(root)
    return "\n".join(tree_lines) + "\n"


def get_readme_content(root: Path) -> str:
    for filename in ["README.md", "readme.md", "Readme.md"]:
        readme_path = root / filename
        if readme_path.exists():
            try:
                with open(readme_path, "r", encoding="utf-8") as f:
                    return "# README\n\n" + f.read() + "\n\n"
            except Exception as e:
                return f"# README\n\n⚠️ Could not read README: {e}\n\n"
    return ""


def get_imported_modules(file_path: Path) -> list:
    imported = set()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(file_path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    dots = "." * node.level
                    imported.add(dots + node.module)
    except Exception:
        pass
    return sorted(imported)


def write_imports_section(root_dir: Path):
    markdown_lines = ["# Module Imports\n"]
    py_files = sorted(root_dir.rglob("*.py"), key=lambda p: str(p.relative_to(root_dir)))
    for file_path in py_files:
        if not should_include_file(file_path):  # Though rglob *.py should be fine
            continue
        rel_path = file_path.relative_to(root_dir)
        imported = get_imported_modules(file_path)
        markdown_lines.append(f"\n## `{rel_path}`\n")
        if imported:
            markdown_lines.append("Imported modules:\n")
            for mod in imported:
                markdown_lines.append(f"- {mod}")
        else:
            markdown_lines.append("No imported modules.")
        markdown_lines.append("\n")
    return "\n".join(markdown_lines) + "\n"


def write_file_contents(root_dir: Path):
    markdown_lines = ["# File Contents\n"]
    readme_names = {"readme.md", "readme.md", "readme.md"}  # Lowercase set

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = sorted([d for d in dirnames if d not in SKIP_DIRS])
        rel_path = Path(dirpath).relative_to(root_dir)
        for filename in sorted(filenames):
            if filename.lower() in readme_names and rel_path == Path("."):
                continue  # Skip README since it's added separately
            file_path = Path(dirpath) / filename
            if not should_include_file(file_path):
                continue
            markdown_lines.append(f"\n### `{file_path.relative_to(root_dir)}`\n")
            lang = file_path.suffix[1:] if file_path.suffix else "text"
            if lang == "md":
                lang = "markdown"
            elif lang == "txt":
                lang = "text"
            markdown_lines.append(f"```{lang}")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    markdown_lines.append(f.read())
            except Exception as e:
                markdown_lines.append(f"⚠️ Could not read file: {e}")
            markdown_lines.append("```")
    return "\n".join(markdown_lines) + "\n"


def main():
    print(f"Generating markdown from: {ROOT_DIR}")
    readme_section = get_readme_content(ROOT_DIR)
    tree_diagram = generate_tree_structure(ROOT_DIR)
    imports_section = write_imports_section(ROOT_DIR)
    file_content_section = write_file_contents(ROOT_DIR)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(readme_section)
        f.write(tree_diagram)
        f.write(imports_section)
        f.write(file_content_section)

    print(f"✅ Output written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()