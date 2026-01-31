# Claude Code 翻译插件

[English](./README_en.md) | [加入讨论](https://github.com/iChenwin/claude-code-translator/issues)

**通过将提示词自动翻译为英文，节省 30%~50% 的 Token 消耗。**

这是一个非侵入式的 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 插件。它会在后台通过通义千问或百度 API 将你的中文/日文等输入自动翻译成英文。这不仅能大幅节省 Token，还能让 Claude 发挥更强的逻辑推理能力。

## 主要特性

- **无感介入**：自动检测非英文输入并翻译，保留代码块、URL 和文件路径原样。
- **高兼容性**：完美支持 VS Code 集成模式、REPL 和甚至文件读写操作。
- **双引擎支持**：内置 **通义千问 (Qianwen)** 和 **百度翻译** 支持。
- **交互可控**：支持在发送前预览并修改翻译后的英文 Prompt。

![Claude Code Translator Screenshot](./screenshot.png)

## 快速开始

### Prerequisites
- Python 3.8+
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed
- Qianwen API key (get one at [阿里云百炼](https://bailian.console.aliyun.com/)) OR
- Baidu AI Translation API key (get one at [百度翻译开放平台](https://fanyi-api.baidu.com/))

1. **下载与安装依赖**
   ```bash
   git clone https://github.com/iChenwin/claude-code-translator.git
   cd claude-code-translator
   pip install -r requirements.txt
   ```

2. **配置 API Key**
   将 `config.example.json` 重命名为 `config.json` 并填入密钥。
   
   *使用通义千问 (推荐):*
   ```json
   {
     "provider": "qianwen",
     "qianwen": { "api_key": "你的阿里云DashScope-Key" }
   }
   ```
   *使用百度翻译:*
   ```json
   {
     "provider": "baidu",
     "baidu": { "api_key": "你的百度翻译api_key", "app_id": "你的百度翻译app_id" }
   }
   ```

3. **安装 Hook**
   ```bash
   python install.py
   ```

重启 Claude Code 即可生效。

## 配置选项 (`config.json`)

| 选项Key | 说明 | 默认值 |
| :--- | :--- | :--- |
| `provider` | 翻译服务商 (`qianwen` 或 `baidu`) | `qianwen` |
| `translate_output` | 是否将 Claude 的英文回复翻译回中文显示 | `true` |
| `interactive_input` | 发送前是否弹窗确认/修改英文 Prompt | `true` |

## 卸载

```bash
python install.py --uninstall
```
