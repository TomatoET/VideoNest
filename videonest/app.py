from __future__ import annotations

import os
import subprocess
import sys
from datetime import date
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from .generator import build_project_dir, generate_project_structure, sanitize_project_name


class VideoNestApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("VideoNest - 视频素材巢")
        self.geometry("760x520")
        self.minsize(680, 480)

        self.generated_dir: Path | None = None

        self.project_name_var = ctk.StringVar()
        self.project_date_var = ctk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        self.save_path_var = ctk.StringVar(value=str(Path.home() / "Videos"))
        self.status_var = ctk.StringVar(value="请输入项目名称并选择保存路径。")

        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        container = ctk.CTkFrame(self, corner_radius=10)
        container.grid(row=0, column=0, sticky="nsew", padx=24, pady=24)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(5, weight=1)

        title = ctk.CTkLabel(
            container,
            text="VideoNest 视频素材巢",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title.grid(row=0, column=0, columnspan=3, sticky="w", padx=24, pady=(22, 8))

        subtitle = ctk.CTkLabel(
            container,
            text="自动生成统一的视频项目素材目录",
            text_color="#AAB2C0",
        )
        subtitle.grid(row=1, column=0, columnspan=3, sticky="w", padx=24, pady=(0, 20))

        ctk.CTkLabel(container, text="项目名称").grid(row=2, column=0, sticky="w", padx=24, pady=10)
        project_entry = ctk.CTkEntry(
            container,
            textvariable=self.project_name_var,
            placeholder_text="例如：AquaCore智能鱼缸视频",
        )
        project_entry.grid(row=2, column=1, columnspan=2, sticky="ew", padx=(0, 24), pady=10)

        ctk.CTkLabel(container, text="项目日期").grid(row=3, column=0, sticky="w", padx=24, pady=10)
        date_entry = ctk.CTkEntry(container, textvariable=self.project_date_var)
        date_entry.grid(row=3, column=1, columnspan=2, sticky="ew", padx=(0, 24), pady=10)

        ctk.CTkLabel(container, text="保存路径").grid(row=4, column=0, sticky="w", padx=24, pady=10)
        path_entry = ctk.CTkEntry(container, textvariable=self.save_path_var)
        path_entry.grid(row=4, column=1, sticky="ew", padx=(0, 12), pady=10)
        browse_button = ctk.CTkButton(container, text="选择路径", width=120, command=self.choose_save_path)
        browse_button.grid(row=4, column=2, sticky="e", padx=(0, 24), pady=10)

        status_frame = ctk.CTkFrame(container, fg_color="#151A22", corner_radius=8)
        status_frame.grid(row=5, column=0, columnspan=3, sticky="nsew", padx=24, pady=(18, 14))
        status_frame.grid_columnconfigure(0, weight=1)
        status_frame.grid_rowconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            status_frame,
            textvariable=self.status_var,
            justify="left",
            anchor="nw",
            wraplength=640,
            text_color="#D7DEE9",
        )
        self.status_label.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)

        action_frame = ctk.CTkFrame(container, fg_color="transparent")
        action_frame.grid(row=6, column=0, columnspan=3, sticky="ew", padx=24, pady=(0, 22))
        action_frame.grid_columnconfigure(0, weight=1)

        self.generate_button = ctk.CTkButton(
            action_frame,
            text="生成目录",
            height=42,
            command=self.generate_directory,
        )
        self.generate_button.grid(row=0, column=1, sticky="e", padx=(0, 12))

        self.open_button = ctk.CTkButton(
            action_frame,
            text="打开生成目录",
            height=42,
            state="disabled",
            command=self.open_generated_directory,
        )
        self.open_button.grid(row=0, column=2, sticky="e")

        project_entry.focus_set()

    def choose_save_path(self) -> None:
        selected_path = filedialog.askdirectory(title="选择视频项目保存路径")
        if selected_path:
            self.save_path_var.set(selected_path)
            self._set_status(f"保存路径已选择：{selected_path}", "info")

    def generate_directory(self) -> None:
        project_name = self.project_name_var.get()
        project_date = self.project_date_var.get().strip()
        save_path = self.save_path_var.get().strip()
        sanitized_name = sanitize_project_name(project_name)

        if not sanitized_name:
            self._show_warning("请输入项目名称。")
            return

        if not save_path:
            self._show_warning("请选择保存路径。")
            return

        target_dir = build_project_dir(save_path, sanitized_name, project_date)
        if target_dir.exists():
            should_continue = messagebox.askyesno(
                "文件夹已存在",
                f"目标文件夹已存在：\n{target_dir}\n\n是否继续创建缺失的目录和文件？已有同名文件不会被覆盖。",
            )
            if not should_continue:
                self._set_status("已取消生成。", "info")
                return

        try:
            result = generate_project_structure(project_name, save_path, project_date)
        except Exception as exc:
            self._show_error(str(exc))
            return

        self.generated_dir = result.project_dir
        self.open_button.configure(state="normal")

        changed_name_note = ""
        if result.sanitized_project_name != project_name.strip():
            changed_name_note = f"\n项目名包含 Windows 非法字符，已替换为：{result.sanitized_project_name}"

        skipped_note = ""
        if result.skipped_files:
            skipped_note = f"\n已有同名文件未覆盖：{len(result.skipped_files)} 个"

        self._set_status(
            f"生成成功：{result.project_dir}{changed_name_note}{skipped_note}",
            "success",
        )
        self.open_generated_directory()

    def open_generated_directory(self) -> None:
        if not self.generated_dir:
            self._show_warning("还没有可打开的生成目录。")
            return

        try:
            open_path(self.generated_dir)
        except Exception as exc:
            self._show_error(f"打开文件夹失败：{exc}")

    def _show_warning(self, message: str) -> None:
        self._set_status(message, "warning")
        messagebox.showwarning("提示", message)

    def _show_error(self, message: str) -> None:
        self._set_status(message, "error")
        messagebox.showerror("错误", message)

    def _set_status(self, message: str, level: str) -> None:
        colors = {
            "info": "#D7DEE9",
            "success": "#5BE49B",
            "warning": "#FFD166",
            "error": "#FF6B6B",
        }
        self.status_var.set(message)
        self.status_label.configure(text_color=colors.get(level, "#D7DEE9"))


def open_path(path: Path) -> None:
    if sys.platform.startswith("win"):
        os.startfile(path)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])


def main() -> None:
    app = VideoNestApp()
    app.mainloop()
