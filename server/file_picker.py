from __future__ import annotations


def select_path(directory: bool = False) -> str:
    """Open a native file/folder picker on the desktop host."""
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        if directory:
            path = filedialog.askdirectory(title="选择本地模型目录")
        else:
            path = filedialog.askopenfilename(title="选择本地模型文件")
    finally:
        root.destroy()
    return path or ""
