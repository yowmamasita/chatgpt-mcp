# ChatGPT MCP Plus

An enhanced Model Context Protocol (MCP) server that enables AI assistants to interact with the ChatGPT desktop app on macOS.

> **Based on** the original [chatgpt-mcp](https://github.com/xncbf/chatgpt-mcp) by [@xncbf](https://github.com/xncbf)

## What's New in Plus Version

- **Dynamic Button Detection**: Reliable UI interaction without hardcoded positions
- **Enhanced Response Handling**: Waits for complete responses using button state monitoring
- **New Chat Tool**: Start fresh conversations with a single command
- **Improved Reliability**: Better error handling and state detection

## Features

- Send prompts to ChatGPT and receive complete responses
- Start new chat conversations to clear context
- Automatic response detection using button state monitoring
- Built with Python and FastMCP

**Note:** This server only supports English text input. Non-English characters may not work properly.

## Installation

### Prerequisites
- macOS
- ChatGPT desktop app installed and running
- Python 3.10+
- uv package manager

## For Claude Code Users

Simply run:
```bash
claude mcp add chatgpt-mcp-plus uvx chatgpt-mcp-plus
```

That's it! You can start using ChatGPT commands in Claude Code.

## For Other MCP Clients

### Step 1: Install the MCP Server

#### Option A: Install from PyPI (Recommended)
```bash
# Install with uv
uv add chatgpt-mcp-plus
```

#### Option B: Manual Installation
```bash
# Clone the repository
git clone https://github.com/yowmamasita/chatgpt-mcp
cd chatgpt-mcp

# Install dependencies with uv
uv sync
```

### Step 2: Configure Your MCP Client

If installed from PyPI, add to your MCP client configuration:
```json
{
  "mcpServers": {
    "chatgpt-plus": {
      "command": "uvx",
      "args": ["chatgpt-mcp-plus"]
    }
  }
}
```

If manually installed, add to your MCP client configuration:
```json
{
  "mcpServers": {
    "chatgpt-plus": {
      "command": "uv",
      "args": ["run", "chatgpt-mcp-plus"],
      "cwd": "/path/to/chatgpt-mcp"
    }
  }
}
```

## Usage

1. **Open ChatGPT desktop app** and make sure it's running
2. **Open your MCP client** (Claude Code, etc.)
3. **Use ChatGPT commands** in your AI assistant:

### Available Tools

- **ask_chatgpt**: Send a prompt to ChatGPT and get the complete response
  ```
  Example: "Ask ChatGPT to explain quantum computing"
  ```

- **new_chat**: Start a fresh conversation in ChatGPT
  ```
  Example: "Start a new chat in ChatGPT"
  ```

The AI assistant will automatically use the appropriate MCP tools to interact with ChatGPT.

## Tool Details

### ask_chatgpt
Send a prompt to ChatGPT and wait for the complete response.

**Parameters:**
- `prompt` (string): The text to send to ChatGPT

**Returns:** ChatGPT's complete response text

**Example:**
```python
response = await ask_chatgpt("What is the capital of France?")
# Returns: "The capital of France is Paris..."
```

### new_chat
Start a new conversation in ChatGPT, clearing any previous context.

**Parameters:** None

**Returns:** Success message

**Example:**
```python
result = await new_chat()
# Returns: "Successfully started a new chat conversation"
```

## Acknowledgments

This project is based on the original [chatgpt-mcp](https://github.com/xncbf/chatgpt-mcp) by [@xncbf](https://github.com/xncbf). The Plus version adds enhanced features including dynamic button detection, improved response handling, and new chat functionality.

## License

MIT
