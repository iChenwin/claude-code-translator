#!/usr/bin/env python3
"""Interactive dialogs for translation hooks using tkinter."""

import tkinter as tk
from tkinter import scrolledtext
from typing import Optional, Tuple


class TranslationEditDialog:
    """Dialog for editing translated prompts."""

    def __init__(self, original: str, translated: str):
        self.original = original
        self.translated = translated
        self.result: Optional[str] = None
        self.cancelled = False

    def show(self) -> Tuple[bool, str]:
        """Show the edit dialog. Returns (confirmed, edited_text)."""
        root = tk.Tk()
        root.title("Edit English Translation / 编辑英文翻译")
        root.geometry("700x500")
        root.configure(bg='#f0f0f0')

        # Center the window
        root.update_idletasks()
        x = (root.winfo_screenwidth() - 700) // 2
        y = (root.winfo_screenheight() - 500) // 2
        root.geometry(f"+{x}+{y}")

        # Original text label
        orig_label = tk.Label(
            root,
            text="Original (原文):",
            font=('Microsoft YaHei', 10, 'bold'),
            bg='#f0f0f0'
        )
        orig_label.pack(anchor='w', padx=10, pady=(10, 2))

        # Original text display (read-only)
        orig_text = scrolledtext.ScrolledText(
            root,
            height=6,
            width=80,
            font=('Consolas', 10),
            bg='#e8e8e8',
            wrap=tk.WORD
        )
        orig_text.pack(padx=10, pady=(0, 10), fill='x')
        orig_text.insert('1.0', self.original)
        orig_text.config(state='disabled')

        # Translated text label
        trans_label = tk.Label(
            root,
            text="English Translation (英文翻译) - You can edit below / 可在下方编辑:",
            font=('Microsoft YaHei', 10, 'bold'),
            bg='#f0f0f0'
        )
        trans_label.pack(anchor='w', padx=10, pady=(0, 2))

        # Translated text edit area
        trans_text = scrolledtext.ScrolledText(
            root,
            height=12,
            width=80,
            font=('Consolas', 10),
            wrap=tk.WORD
        )
        trans_text.pack(padx=10, pady=(0, 10), fill='both', expand=True)
        trans_text.insert('1.0', self.translated)
        trans_text.focus_set()

        # Button frame
        btn_frame = tk.Frame(root, bg='#f0f0f0')
        btn_frame.pack(pady=10)

        def on_confirm():
            self.result = trans_text.get('1.0', 'end-1c')
            self.cancelled = False
            root.destroy()

        def on_cancel():
            self.cancelled = True
            root.destroy()

        # Confirm button
        confirm_btn = tk.Button(
            btn_frame,
            text="Confirm / 确认 (Enter)",
            command=on_confirm,
            font=('Microsoft YaHei', 10),
            bg='#4CAF50',
            fg='white',
            width=20,
            height=2
        )
        confirm_btn.pack(side='left', padx=10)

        # Cancel button
        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel / 取消 (Esc)",
            command=on_cancel,
            font=('Microsoft YaHei', 10),
            bg='#f44336',
            fg='white',
            width=20,
            height=2
        )
        cancel_btn.pack(side='left', padx=10)

        # Keyboard bindings
        root.bind('<Return>', lambda e: on_confirm() if e.state & 0x4 else None)  # Ctrl+Enter
        root.bind('<Escape>', lambda e: on_cancel())

        # Keep window on top
        root.attributes('-topmost', True)
        root.lift()
        root.focus_force()

        root.mainloop()

        if self.cancelled:
            return (False, self.translated)
        return (True, self.result if self.result else self.translated)


class TranslationConfirmDialog:
    """Dialog for confirming whether to translate output."""

    def __init__(self, message_preview: str):
        self.message_preview = message_preview
        self.confirmed = False

    def show(self) -> bool:
        """Show confirmation dialog. Returns True if user wants translation."""
        root = tk.Tk()
        root.title("Translate Output? / 翻译输出?")
        root.geometry("500x300")
        root.configure(bg='#f0f0f0')

        # Center the window
        root.update_idletasks()
        x = (root.winfo_screenwidth() - 500) // 2
        y = (root.winfo_screenheight() - 300) // 2
        root.geometry(f"+{x}+{y}")

        # Question label
        question_label = tk.Label(
            root,
            text="Translate Claude's response to Chinese?\n将 Claude 的回复翻译成中文?",
            font=('Microsoft YaHei', 12, 'bold'),
            bg='#f0f0f0'
        )
        question_label.pack(pady=15)

        # Message preview
        preview_label = tk.Label(
            root,
            text="Preview (预览):",
            font=('Microsoft YaHei', 9),
            bg='#f0f0f0'
        )
        preview_label.pack(anchor='w', padx=10)

        preview_text = scrolledtext.ScrolledText(
            root,
            height=8,
            width=60,
            font=('Consolas', 9),
            bg='#e8e8e8',
            wrap=tk.WORD
        )
        preview_text.pack(padx=10, pady=(0, 15), fill='both', expand=True)

        # Show first 500 chars
        preview = self.message_preview[:500]
        if len(self.message_preview) > 500:
            preview += "\n..."
        preview_text.insert('1.0', preview)
        preview_text.config(state='disabled')

        # Button frame
        btn_frame = tk.Frame(root, bg='#f0f0f0')
        btn_frame.pack(pady=10)

        def on_yes():
            self.confirmed = True
            root.destroy()

        def on_no():
            self.confirmed = False
            root.destroy()

        # Yes button
        yes_btn = tk.Button(
            btn_frame,
            text="Yes / 是 (Y)",
            command=on_yes,
            font=('Microsoft YaHei', 10),
            bg='#4CAF50',
            fg='white',
            width=15,
            height=2
        )
        yes_btn.pack(side='left', padx=10)

        # No button
        no_btn = tk.Button(
            btn_frame,
            text="No / 否 (N)",
            command=on_no,
            font=('Microsoft YaHei', 10),
            bg='#9e9e9e',
            fg='white',
            width=15,
            height=2
        )
        no_btn.pack(side='left', padx=10)

        # Keyboard bindings
        root.bind('y', lambda e: on_yes())
        root.bind('Y', lambda e: on_yes())
        root.bind('n', lambda e: on_no())
        root.bind('N', lambda e: on_no())
        root.bind('<Return>', lambda e: on_yes())
        root.bind('<Escape>', lambda e: on_no())

        # Keep window on top
        root.attributes('-topmost', True)
        root.lift()
        root.focus_force()

        root.mainloop()

        return self.confirmed


def show_edit_dialog(original: str, translated: str) -> Tuple[bool, str]:
    """
    Show translation edit dialog.

    Args:
        original: Original text in source language
        translated: Translated text

    Returns:
        Tuple of (confirmed, edited_text)
        - confirmed: True if user confirmed, False if cancelled
        - edited_text: The edited translation (or original translation if cancelled)
    """
    dialog = TranslationEditDialog(original, translated)
    return dialog.show()


def show_confirm_dialog(message_preview: str) -> bool:
    """
    Show translation confirmation dialog.

    Args:
        message_preview: Preview of the message to translate

    Returns:
        True if user wants to translate, False otherwise
    """
    dialog = TranslationConfirmDialog(message_preview)
    return dialog.show()


class TranslationResultDialog:
    """Dialog for displaying translation results."""

    def __init__(self, original: str, translated: str):
        self.original = original
        self.translated = translated

    def show(self):
        """Show the result dialog."""
        root = tk.Tk()
        root.title("Translation Result / 翻译结果")
        root.geometry("800x600")
        root.configure(bg='#f0f0f0')

        # Center the window
        root.update_idletasks()
        x = (root.winfo_screenwidth() - 800) // 2
        y = (root.winfo_screenheight() - 600) // 2
        root.geometry(f"+{x}+{y}")

        # Main container with two columns
        main_frame = tk.Frame(root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Left column: Original
        left_frame = tk.Frame(main_frame, bg='#f0f0f0')
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))

        tk.Label(
            left_frame, 
            text="Original (原文):", 
            font=('Microsoft YaHei', 10, 'bold'),
            bg='#f0f0f0'
        ).pack(anchor='w')

        orig_text = scrolledtext.ScrolledText(
            left_frame,
            font=('Consolas', 10),
            bg='#e8e8e8',
            wrap=tk.WORD
        )
        orig_text.pack(fill='both', expand=True)
        orig_text.insert('1.0', self.original)
        orig_text.config(state='disabled')

        # Right column: Translated
        right_frame = tk.Frame(main_frame, bg='#f0f0f0')
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))

        tk.Label(
            right_frame, 
            text="Translation (中文翻译):", 
            font=('Microsoft YaHei', 10, 'bold'),
            bg='#f0f0f0'
        ).pack(anchor='w')

        trans_text = scrolledtext.ScrolledText(
            right_frame,
            font=('Microsoft YaHei', 10),
            bg='#ffffff',
            wrap=tk.WORD
        )
        trans_text.pack(fill='both', expand=True)
        trans_text.insert('1.0', self.translated)
        trans_text.config(state='disabled')

        # Button frame
        btn_frame = tk.Frame(root, bg='#f0f0f0')
        btn_frame.pack(fill='x', padx=10, pady=(0, 10))

        def on_copy():
            root.clipboard_clear()
            root.clipboard_append(self.translated)
            copy_btn.config(text="Copied! / 已复制!", bg='#8BC34A')
            root.after(2000, lambda: copy_btn.config(text="Copy Translation / 复制译文", bg='#2196F3'))

        def on_close():
            root.destroy()

        # Copy button
        copy_btn = tk.Button(
            btn_frame,
            text="Copy Translation / 复制译文",
            command=on_copy,
            font=('Microsoft YaHei', 10),
            bg='#2196F3',
            fg='white',
            width=20,
            height=2
        )
        copy_btn.pack(side='right', padx=5)

        # Close button
        close_btn = tk.Button(
            btn_frame,
            text="Close / 关闭 (Esc)",
            command=on_close,
            font=('Microsoft YaHei', 10),
            bg='#9e9e9e',
            fg='white',
            width=15,
            height=2
        )
        close_btn.pack(side='right', padx=5)

        # Bind Esc to close
        root.bind('<Escape>', lambda e: on_close())

        # Keep window on top
        root.attributes('-topmost', True)
        root.lift()
        root.focus_force()

        root.mainloop()


def show_translation_result(original: str, translated: str):
    """
    Show translation result dialog.
    """
    dialog = TranslationResultDialog(original, translated)
    dialog.show()


if __name__ == '__main__':
    # Test the dialogs
    print("Testing edit dialog...")
    confirmed, text = show_edit_dialog(
        "这是一个测试消息",
        "This is a test message"
    )
    print(f"Confirmed: {confirmed}, Text: {text}")

    print("\nTesting confirm dialog...")
    result = show_confirm_dialog("This is a sample response from Claude that could be translated.")
    print(f"Want translation: {result}")
