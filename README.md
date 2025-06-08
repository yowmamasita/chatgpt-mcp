# ChatGPT MCP Server

A Model Context Protocol (MCP) server that enables Claude to interact with the ChatGPT desktop app on macOS, with full Korean language support.

## Features

- Send prompts to ChatGPT from Claude
- Retrieve list of conversations from ChatGPT
- Full Korean language support using Base64 encoding
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

Add to your IDE configuration

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

## Korean Language Support

The server automatically detects Korean text and uses Base64 encoding to ensure proper delivery to ChatGPT. When Korean text is detected, it sends a request to ChatGPT to decode and respond in Korean.

## Requirements

- macOS
- ChatGPT desktop app installed
- Python 3.10+
- uv package manager

## License

MIT
