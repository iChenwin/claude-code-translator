#!/usr/bin/env python3
"""Notification hook for translating Claude's English output to Chinese."""

import sys
import json
import os
import io

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.qianwen_client import QianwenClient
from lib.baidu_client import BaiduClient
from lib.dialogs import show_confirm_dialog, show_translation_result


def get_translation_client(config):
    """Get the appropriate translation client based on config.

    Args:
        config: Configuration dictionary

    Returns:
        Translation client instance
    """
    provider = config.get('provider', 'qianwen')

    if provider == 'baidu':
        baidu_config = config['baidu']
        return BaiduClient(
            api_key=baidu_config['api_key'],
            app_id=baidu_config['app_id']
        )
    else:
        # Default to qianwen
        qianwen_config = config['qianwen']
        return QianwenClient(
            base_url=qianwen_config['base_url'],
            api_key=qianwen_config['api_key'],
            model=qianwen_config['model']
        )


def load_config():
    """Load configuration from config.json."""
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'config.json'
    )
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    """Main hook handler."""
    try:
        # Read input from stdin
        # Ensure we are reading UTF-8
        try:
            if hasattr(sys.stdin, 'buffer'):
                sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
        except Exception:
            pass

        raw_input = sys.stdin.read().strip()
        if raw_input.startswith('\ufeff'):
            raw_input = raw_input[1:]
        input_data = json.loads(raw_input)

        # Debug logging
        with open('d:/code/src/claude-translator/debug_output_hook.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps(input_data, ensure_ascii=False, indent=2) + "\n\n")

        # Check if this is an assistant message notification
        # Check if this is an idle prompt notification (meaning Claude finished responding)
        notification_type = input_data.get('notification_type', '')
        if notification_type not in ['idle_prompt', 'permission_prompt']:
            # Not a relevant event
            print(json.dumps({"result": "continue"}))
            return

        # Get the transcript path
        transcript_path = input_data.get('transcript_path', '')
        if not transcript_path or not os.path.exists(transcript_path):
            print(json.dumps({"result": "continue"}))
            return

        # Read the last line of the transcript file
        last_assistant_message = ""
        try:
            with open(transcript_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Iterate backwards to find the last assistant message
                for line in reversed(lines):
                    try:
                        entry = json.loads(line)
                        msg = entry.get('message', {})
                        if msg.get('role') == 'assistant' and msg.get('type') == 'message':
                            # Found the last assistant message
                            content_list = msg.get('content', [])
                            for content in content_list:
                                if content.get('type') == 'text':
                                    last_assistant_message += content.get('text', '')
                            break
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            # Log error reading transcript
            with open('d:/code/src/claude-translator/debug_output_error.log', 'a', encoding='utf-8') as f:
                f.write(f"Error reading transcript: {e}\n")
            print(json.dumps({"result": "continue"}))
            return

        if not last_assistant_message:
            # No assistant message found
            print(json.dumps({"result": "continue"}))
            return

        # Load config
        config = load_config()

        # Check if output translation is enabled
        if not config.get('translate_output', True):
            print(json.dumps({"result": "continue"}))
            return

        # Initialize client based on provider
        client = get_translation_client(config)

        # Skip if message is already primarily Chinese
        # (We check if it has significant Chinese content to avoid double translation)
        chinese_char_count = sum(1 for c in last_assistant_message if '\u4e00' <= c <= '\u9fff')
        if chinese_char_count > len(last_assistant_message) * 0.3:
            print(json.dumps({"result": "continue"}))
            return

        # Check if interactive mode is enabled
        interactive_output = config.get('interactive_output', True)

        if interactive_output:
            # Ask user if they want to translate
            # Use the first 500 chars for preview
            preview_msg = last_assistant_message[:500] + "..." if len(last_assistant_message) > 500 else last_assistant_message
            if not show_confirm_dialog(preview_msg):
                # User declined translation
                print(json.dumps({"result": "continue"}))
                return

        # Debug logging before translation
        with open('d:/code/src/claude-translator/debug_output_hook.log', 'a', encoding='utf-8') as f:
            f.write(f"Translating message (len={len(last_assistant_message)}):\n{last_assistant_message}\n\n")

        # Translate to Chinese
        translated, usage = client.translate(last_assistant_message, 'Chinese')

        # Debug logging after translation
        with open('d:/code/src/claude-translator/debug_output_hook.log', 'a', encoding='utf-8') as f:
            f.write(f"Translation result (len={len(translated)}):\n{translated}\n")
            f.write(f"Usage: {usage}\n\n")

        # Show result in a standalone window
        show_translation_result(last_assistant_message, translated, usage)
        
        # Continue without adding context to Claude (since we showed it to user)
        print(json.dumps({"result": "continue"}))

    except Exception as e:
        # On error, log to stderr and continue normally
        with open('d:/code/src/claude-translator/debug_output_error.log', 'a', encoding='utf-8') as f:
            f.write(f"Error: {e}\n")
        print(f"Output translation hook error: {e}", file=sys.stderr)
        print(json.dumps({"result": "continue"}))


if __name__ == '__main__':
    main()
