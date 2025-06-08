# ChatGPT MCP Server

A Model Context Protocol (MCP) server that enables AI assistants to interact with the ChatGPT desktop app on macOS.

## Features

- Send prompts to ChatGPT from any MCP-compatible AI assistant
- Built with Python and FastMCP

**Note:** This server only supports English text input. Non-English characters may not work properly.

## Installation & Setup

### Step 1: Install ChatGPT Desktop App
Make sure you have the ChatGPT desktop app installed and running on your macOS.

### Step 2: Install this MCP Server

```bash
# Clone the repository
git clone https://github.com/xncbf/chatgpt-mcp
cd chatgpt-mcp

# Install dependencies with uv
uv sync
```

### Step 3: Configure MCP Client

#### For Claude Code:
```bash
# Add MCP server to Claude Code
claude mcp add chatgpt-mcp uv run /path/to/chatgpt-mcp
```

#### For other MCP clients:
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

### Step 4: Start Using

1. **Open ChatGPT desktop app** and make sure it's running
2. **Open your MCP client** (Claude Code, etc.)
3. **Use ChatGPT commands** in your AI assistant:
   - "Send a message to ChatGPT"
   - "Create a new ChatGPT conversation"
   - "Get my ChatGPT conversations"

The AI assistant will automatically use the appropriate MCP tools to interact with ChatGPT.

## Available Tools

### ask_chatgpt
Send a prompt to ChatGPT and receive the response.

```python
ask_chatgpt(prompt="Hello, ChatGPT!")
```

### get_chatgpt_response
Get the latest response from ChatGPT after sending a message.

```python
get_chatgpt_response()
```

## Requirements

- macOS
- ChatGPT desktop app installed
- Python 3.10+
- uv package manager

## License

MIT
