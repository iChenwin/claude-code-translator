#!/usr/bin/env python3
"""Notification hook for translating Claude's English output to Chinese."""

import sys
import json
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.qianwen_client import QianwenClient


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
        input_data = json.loads(sys.stdin.read())

        # Check if this is an assistant message notification
        hook_event = input_data.get('hook_event_name', '')
        if hook_event != 'Notification':
            print(json.dumps({"result": "continue"}))
            return

        # Get the message content
        message = input_data.get('message', '')
        message_type = input_data.get('type', '')

        # Only translate assistant text messages
        if message_type != 'assistant' or not message:
            print(json.dumps({"result": "continue"}))
            return

        # Load config
        config = load_config()

        # Check if output translation is enabled
        if not config.get('translate_output', True):
            print(json.dumps({"result": "continue"}))
            return

        qianwen_config = config['qianwen']

        # Initialize client
        client = QianwenClient(
            base_url=qianwen_config['base_url'],
            api_key=qianwen_config['api_key'],
            model=qianwen_config['model']
        )

        # Skip if message is already primarily Chinese
        # (We check if it has significant Chinese content to avoid double translation)
        chinese_char_count = sum(1 for c in message if '\u4e00' <= c <= '\u9fff')
        if chinese_char_count > len(message) * 0.3:
            print(json.dumps({"result": "continue"}))
            return

        # Translate to Chinese
        translated = client.translate(message, 'Chinese')

        # Output with Chinese translation appended
        result = {
            "result": "continue",
            "additionalContext": f"\n---\n[Chinese Translation / 中文翻译]\n{translated}\n---"
        }

        print(json.dumps(result, ensure_ascii=False))

    except Exception as e:
        # On error, log to stderr and continue normally
        print(f"Output translation hook error: {e}", file=sys.stderr)
        print(json.dumps({"result": "continue"}))


if __name__ == '__main__':
    main()
