import sys
import logging

# Set up logging to stderr for debugging
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.debug("Starting ChatGPT MCP imports...")

from mcp.server.fastmcp import FastMCP
from chatgpt_mcp.mcp_tools import setup_mcp_tools

logger.debug("Imports successful, creating FastMCP instance...")

# Initialize the MCP server
mcp = FastMCP("chatgpt")

logger.debug("FastMCP instance created, setting up tools...")

# Setup MCP tools
setup_mcp_tools(mcp)

logger.debug("MCP tools setup complete")

def main():
    """Main entry point for the MCP server"""
    logger.info("ChatGPT MCP Server main() called")
    try:
        logger.info("Starting MCP server with stdio transport...")
        mcp.run(transport='stdio')
    except Exception as e:
        logger.error(f"Error starting server: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
