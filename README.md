# ChatGPT MCP Server

A Model Context Protocol (MCP) server that enables AI assistants to interact with the ChatGPT desktop app on macOS, with full CJK (Chinese, Japanese, Korean) language support.

## Features

- Send prompts to ChatGPT from any MCP-compatible AI assistant
- Retrieve list of conversations from ChatGPT
- Full CJK language support using Base64 encoding for Chinese, Japanese, and Korean text
- Automatic character detection and encoding
- Built with Python and FastMCP

## Installation

Using uv (recommended):

```bash
# Clone the repository
git clone <your-repo-url>
cd chatgpt-mcp

# Install dependencies with uv
uv sync

# Run the server
uv run chatgpt-mcp
```

## Usage

### General MCP Client Configuration

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "chatgpt": {
      "command": "uv",
      "args": ["run", "chatgpt-mcp"],
      "cwd": "/path/to/chatgpt-mcp"
    }
  }
}
```

### Claude Code Usage

If you're using Claude Code, you can easily set up this MCP server:

1. **Add MCP server to Claude Code:**
   ```bash
   claude mcp add chatgpt-mcp uv run /path/to/chatgpt-mcp
   ```

2. **Use the tools in Claude Code:**
   - Ask Claude Code to "send a message to ChatGPT"
   - Claude Code will automatically use the `ask_chatgpt` tool
   - For CJK languages, encoding is handled automatically

3. **Example usage in Claude Code:**
   ```
   User: Send "안녕하세요, ChatGPT!" to ChatGPT
   Claude: I'll send that Korean message to ChatGPT for you.
   ```

## Available Tools

### ask_chatgpt
Send a prompt to ChatGPT and receive confirmation.

```python
ask_chatgpt(prompt="Hello, ChatGPT!")
```

### get_conversations
Get a list of available conversations from ChatGPT.

```python
get_conversations()
```

## CJK Language Support

The server automatically detects CJK (Chinese, Japanese, Korean) characters and uses Base64 encoding to ensure proper delivery to ChatGPT. When CJK text is detected, it sends a request to ChatGPT to decode and respond in the same language.

### Supported Languages
- **Korean**: Hangul characters (한글)
- **Chinese**: Simplified and Traditional Chinese characters (中文)
- **Japanese**: Hiragana (ひらがな) and Katakana (カタカナ)

### How it works
1. Text is analyzed for CJK characters using Unicode ranges
2. If CJK characters are found, the entire message is Base64 encoded
3. ChatGPT receives a request to decode and respond in the original language
4. Regular ASCII text (including punctuation) is sent directly without encoding

## Requirements

- macOS
- ChatGPT desktop app installed
- Python 3.10+
- uv package manager

## License

MIT
