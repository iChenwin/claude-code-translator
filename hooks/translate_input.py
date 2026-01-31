#!/usr/bin/env python3
"""UserPromptSubmit hook for translating Chinese input to English."""

import sys
import json
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.qianwen_client import QianwenClient
from lib.baidu_client import BaiduClient
from lib.dialogs import show_edit_dialog


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
        input_data = json.loads(sys.stdin.read())
        prompt = input_data.get('prompt', '')

        if not prompt:
            # No prompt, continue without modification
            print(json.dumps({"result": "continue"}))
            return

        # Load config
        config = load_config()

        # Initialize client based on provider
        client = get_translation_client(config)

        # Check if prompt contains non-English text
        if not client.detect_non_english(prompt):
            # No non-English text detected, continue without modification
            print(json.dumps({"result": "continue"}))
            return

        # Translate to English
        translated = client.translate(prompt, 'English')

        # Check if interactive mode is enabled
        interactive_input = config.get('interactive_input', True)

        if interactive_input:
            # Show edit dialog for user to review/edit translation
            confirmed, edited_translation = show_edit_dialog(prompt, translated)

            if not confirmed:
                # User cancelled, continue with original prompt without translation context
                print(json.dumps({"result": "continue"}))
                return

            translated = edited_translation

        # Build context showing translation
        # Note: UserPromptSubmit hooks cannot modify the prompt, only add context
        # Claude will see: original Chinese prompt + this context with translation
        context = f"""[Translation Context]
The user's message above is in Chinese. Here is the English translation:

{translated}

Please respond based on the translated meaning."""

        # Output as plain text - simpler and more reliable
        print(context)

    except Exception as e:
        # On error, log to stderr and continue with original prompt
        print(f"Translation hook error: {e}", file=sys.stderr)
        print(json.dumps({"result": "continue"}))


if __name__ == '__main__':
    main()
