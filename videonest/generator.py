from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .templates import (
    ASSET_CSV_HEADER,
    DIRECTORY_TEMPLATE,
    SHOOTING_LIST_CONTENT,
    project_readme_content,
)


INVALID_WINDOWS_CHARS = r'<>:"/\\|?*'
INVALID_WINDOWS_CHARS_PATTERN = re.compile(f"[{re.escape(INVALID_WINDOWS_CHARS)}]")


@dataclass(frozen=True)
class GenerationResult:
    project_dir: Path
    sanitized_project_name: str
    created_files: tuple[Path, ...]
    skipped_files: tuple[Path, ...]


def sanitize_project_name(project_name: str) -> str:
    sanitized = INVALID_WINDOWS_CHARS_PATTERN.sub("_", project_name.strip())
    sanitized = re.sub(r"\s+", " ", sanitized)
    sanitized = sanitized.rstrip(" .")
    return sanitized


def build_project_dir(base_path: str | Path, project_name: str, project_date: str) -> Path:
    sanitized_name = sanitize_project_name(project_name)
    return Path(base_path).expanduser().resolve() / f"{project_date}_{sanitized_name}"


def validate_inputs(project_name: str, base_path: str | Path, project_date: str) -> tuple[str, Path]:
    sanitized_name = sanitize_project_name(project_name)
    if not sanitized_name:
        raise ValueError("请输入项目名称。")

    if not str(base_path).strip():
        raise ValueError("请选择保存路径。")

    target_base = Path(base_path).expanduser()
    if not target_base.exists():
        raise ValueError("保存路径不存在。")

    if not target_base.is_dir():
        raise ValueError("保存路径不是文件夹。")

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", project_date.strip()):
        raise ValueError("日期格式应为 YYYY-MM-DD。")

    return sanitized_name, target_base


def generate_project_structure(
    project_name: str,
    base_path: str | Path,
    project_date: str,
) -> GenerationResult:
    sanitized_name, target_base = validate_inputs(project_name, base_path, project_date)
    project_dir = target_base.resolve() / f"{project_date}_{sanitized_name}"
    project_dir.mkdir(parents=True, exist_ok=True)

    for relative_dir in DIRECTORY_TEMPLATE:
        (project_dir / Path(relative_dir)).mkdir(parents=True, exist_ok=True)

    file_writes = {
        project_dir / "项目说明.md": project_readme_content(sanitized_name, project_date),
        project_dir / "素材清单.csv": ASSET_CSV_HEADER,
        project_dir / "拍摄清单.md": SHOOTING_LIST_CONTENT,
    }

    created_files: list[Path] = []
    skipped_files: list[Path] = []
    for file_path, content in file_writes.items():
        if file_path.exists():
            skipped_files.append(file_path)
            continue

        if file_path.suffix.lower() == ".csv":
            with file_path.open("w", encoding="utf-8-sig", newline="") as csv_file:
                csv_file.write(content)
        else:
            file_path.write_text(content, encoding="utf-8")
        created_files.append(file_path)

    return GenerationResult(
        project_dir=project_dir,
        sanitized_project_name=sanitized_name,
        created_files=tuple(created_files),
        skipped_files=tuple(skipped_files),
    )
