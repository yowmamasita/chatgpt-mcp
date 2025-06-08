# ChatGPT MCP Server

A Model Context Protocol (MCP) server that enables AI assistants to interact with the ChatGPT desktop app on macOS.

## Features

- Send prompts to ChatGPT from any MCP-compatible AI assistant
- Create new conversations in ChatGPT
- Retrieve list of conversations from ChatGPT
- Built with Python and FastMCP

## Installation

Using uv (recommended):

```bash
# Clone the repository
git clone https://github.com/xncbf/chatgpt-mcp
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

## Available Tools

### ask_chatgpt
Send a prompt to ChatGPT and receive the response.

```python
ask_chatgpt(prompt="Hello, ChatGPT!")
```

### new_chatgpt_conversation
Create a new conversation in ChatGPT.

```python
new_chatgpt_conversation()
```

### get_conversations
Get a list of available conversations from ChatGPT.

```python
get_conversations()
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
