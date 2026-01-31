# Claude Code Translation Plugin

[简体中文](./README.md)

**Save 30%~50% on token costs by automatically translating prompts to English.**

This plugin hooks into [Claude Code](https://docs.anthropic.com/en/docs/claude-code) to translate non-English input (Chinese, Japanese, etc.) into English before it reaches Claude. This not only saves tokens but often improves Claude's reasoning quality.

## Features

- **Seamless**: Automatically detects and translates non-English input.
- **Smart**: Ignores code blocks, file paths, and URLs.
- **Flexible**: Supports **Qianwen (Alibaba)** and **Baidu** translation APIs.
- **Native Experience**: Fully compatible with VS Code integration and session management.

![Claude Code Translator Screenshot](./screenshot.png)

## Installation

### Prerequisites
- Python 3.8+
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed
- Qianwen API key (get one at [阿里云百炼](https://bailian.console.aliyun.com/)) OR
- Baidu AI Translation API key (get one at [百度翻译开放平台](https://fanyi-api.baidu.com/))

1. **Clone & Install Dependencies**
   ```bash
   git clone https://github.com/iChenwin/claude-code-translator.git
   cd claude-code-translator
   pip install -r requirements.txt
   ```

2. **Configure API Key**
   Rename `config.example.json` to `config.json` and add your API key.
   
   *Using Qianwen (Recommended):*
   ```json
   {
     "provider": "qianwen",
     "qianwen": { "api_key": "sk-..." }
   }
   ```
   *Using Baidu:*
   ```json
   {
     "provider": "baidu",
     "baidu": { "api_key": "...", "app_id": "..." }
   }
   ```

3. **Install Hooks**
   ```bash
   python install.py
   ```

Restart Claude Code, and you're good to go!

## Configuration (`config.json`)

| Option | Description | Default |
| :--- | :--- | :--- |
| `provider` | `qianwen` or `baidu` | `qianwen` |
| `translate_output` | Translate Claude's value-added english response back to your language? | `true` |
| `interactive_input` | Show a popup to review/edit the English translation before sending? | `true` |

## Uninstallation

```bash
python install.py --uninstall
```
