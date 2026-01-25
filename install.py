#!/usr/bin/env python3
"""Installation script for Claude Code Translation Plugin.

This script adds hook configurations to ~/.claude/settings.json
to enable automatic translation of Chinese input/output.
"""

import json
import os
import sys
from pathlib import Path


def get_claude_settings_path():
    """Get the path to Claude settings file."""
    home = Path.home()
    return home / '.claude' / 'settings.json'


def get_hook_commands():
    """Get the hook command configurations."""
    # Get absolute path to hooks directory
    hooks_dir = Path(__file__).parent / 'hooks'
    input_hook = hooks_dir / 'translate_input.py'
    output_hook = hooks_dir / 'translate_output.py'

    # Use forward slashes for cross-platform compatibility
    input_hook_str = str(input_hook).replace('\\', '/')
    output_hook_str = str(output_hook).replace('\\', '/')

    return {
        "input": f"python \"{input_hook_str}\"",
        "output": f"python \"{output_hook_str}\""
    }


def install_hooks():
    """Install translation hooks to Claude settings."""
    settings_path = get_claude_settings_path()

    # Create .claude directory if it doesn't exist
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing settings or create new
    if settings_path.exists():
        with open(settings_path, 'r', encoding='utf-8') as f:
            try:
                settings = json.load(f)
            except json.JSONDecodeError:
                settings = {}
    else:
        settings = {}

    # Ensure hooks section exists
    if 'hooks' not in settings:
        settings['hooks'] = {}

    hooks = get_hook_commands()

    # Add UserPromptSubmit hook for input translation
    settings['hooks']['UserPromptSubmit'] = [
        {
            "matcher": "",
            "hooks": [
                {
                    "type": "command",
                    "command": hooks["input"]
                }
            ]
        }
    ]

    # Add Notification hook for output translation (optional)
    settings['hooks']['Notification'] = [
        {
            "matcher": "",
            "hooks": [
                {
                    "type": "command",
                    "command": hooks["output"]
                }
            ]
        }
    ]

    # Write settings back
    with open(settings_path, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

    print(f"Hooks installed successfully to: {settings_path}")
    print("\nConfigured hooks:")
    print(f"  - UserPromptSubmit: {hooks['input']}")
    print(f"  - Notification: {hooks['output']}")
    print("\nTo disable output translation, set 'translate_output': false in config.json")
    print("\nRestart Claude Code for changes to take effect.")


def uninstall_hooks():
    """Remove translation hooks from Claude settings."""
    settings_path = get_claude_settings_path()

    if not settings_path.exists():
        print("No Claude settings file found. Nothing to uninstall.")
        return

    with open(settings_path, 'r', encoding='utf-8') as f:
        try:
            settings = json.load(f)
        except json.JSONDecodeError:
            print("Invalid settings file. Nothing to uninstall.")
            return

    if 'hooks' not in settings:
        print("No hooks configured. Nothing to uninstall.")
        return

    # Remove our hooks
    hooks_removed = False
    for hook_name in ['UserPromptSubmit', 'Notification']:
        if hook_name in settings['hooks']:
            del settings['hooks'][hook_name]
            hooks_removed = True

    if hooks_removed:
        # Clean up empty hooks section
        if not settings['hooks']:
            del settings['hooks']

        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)

        print("Translation hooks uninstalled successfully.")
    else:
        print("No translation hooks found. Nothing to uninstall.")


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == '--uninstall':
        uninstall_hooks()
    else:
        install_hooks()


if __name__ == '__main__':
    main()
