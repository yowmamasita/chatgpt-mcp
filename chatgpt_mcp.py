#!/usr/bin/env python3
"""ChatGPT MCP Server - A Model Context Protocol server for interacting with ChatGPT on macOS"""

import asyncio
import subprocess
import base64
import re
from typing import Optional
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("chatgpt")

async def check_chatgpt_access() -> bool:
    """Check if ChatGPT app is installed and running"""
    try:
        # Check if ChatGPT is running
        result = subprocess.run(
            ["osascript", "-e", 'tell application "System Events" to return application process "ChatGPT" exists'],
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip() != "true":
            print("ChatGPT app is not running, attempting to launch...")
            try:
                subprocess.run(
                    ["osascript", "-e", 'tell application "ChatGPT" to activate', "-e", "delay 2"],
                    check=True
                )
            except subprocess.CalledProcessError:
                raise Exception("Could not activate ChatGPT app. Please start it manually.")
        
        return True
    except Exception as e:
        raise Exception(f"Cannot access ChatGPT app. Please make sure ChatGPT is installed and properly configured. Error: {str(e)}")

@mcp.tool()
async def ask_chatgpt(prompt: str, conversation_id: Optional[str] = None) -> str:
    """Send a prompt to ChatGPT and return confirmation.
    
    Args:
        prompt: The text to send to ChatGPT
        conversation_id: Optional conversation ID to continue a specific conversation
    
    Returns:
        Confirmation message
    """
    await check_chatgpt_access()
    
    try:
        # Check if prompt contains CJK (Chinese, Japanese, Korean) characters
        def has_cjk_chars(text):
            return bool(re.search(r'[\u4e00-\u9fff\u3400-\u4dbf\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af\u1100-\u11ff\u3130-\u318f]', text))
        
        has_cjk = has_cjk_chars(prompt)
        processed_prompt = prompt
        
        if has_cjk:
            # Encode multi-byte text to Base64 and ask ChatGPT to decode it
            base64_text = base64.b64encode(prompt.encode('utf-8')).decode('ascii')
            processed_prompt = f"Please decode this Base64 text and respond in the same language: {base64_text}"
        
        # AppleScript to send message to ChatGPT
        # Escape quotes for AppleScript
        escaped_prompt = processed_prompt.replace('\\', '\\\\').replace('"', '\\"')
        
        applescript = f'''
tell application "ChatGPT"
    activate
    delay 1
end tell

tell application "System Events"
    tell process "ChatGPT"
        -- Clear existing text
        keystroke "a" using {{command down}}
        key code 51 -- delete key
        delay 0.5
        
        -- Type the processed prompt (ASCII only)
        keystroke "{escaped_prompt}"
        delay 0.5
        keystroke return
        
        -- Wait for response completion
        delay 3
    end tell
end tell

return "Message sent to ChatGPT successfully"
        '''
        
        result = subprocess.run(
            ["osascript", "-e", applescript],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"AppleScript error: {result.stderr}")
        
        return "Message sent to ChatGPT successfully. Please check the ChatGPT app for the response."
        
    except Exception as e:
        raise Exception(f"Failed to get response from ChatGPT: {str(e)}")

@mcp.tool()
async def get_conversations() -> list[str]:
    """Get available conversations from ChatGPT.
    
    Returns:
        List of conversation titles
    """
    try:
        applescript = '''
            -- Check if ChatGPT is running
            tell application "System Events"
                if not (application process "ChatGPT" exists) then
                    return "ChatGPT is not running"
                end if
            end tell

            tell application "ChatGPT"
                -- Activate ChatGPT and give it time to respond
                activate
                delay 1.5

                tell application "System Events"
                    tell process "ChatGPT"
                        -- Check if ChatGPT window exists
                        if not (exists window 1) then
                            return "No ChatGPT window found"
                        end if
                        
                        -- Try to get conversation titles with multiple approaches
                        set conversationsList to {}
                        
                        try
                            -- First attempt: try buttons in group 1 of group 1
                            if exists group 1 of group 1 of window 1 then
                                set chatButtons to buttons of group 1 of group 1 of window 1
                                repeat with chatButton in chatButtons
                                    set buttonName to name of chatButton
                                    if buttonName is not "New chat" then
                                        set end of conversationsList to buttonName
                                    end if
                                end repeat
                            end if
                            
                            -- If we didn't find any conversations, try an alternative approach
                            if (count of conversationsList) is 0 then
                                -- Try to find UI elements by accessibility description
                                set uiElements to UI elements of window 1
                                repeat with elem in uiElements
                                    try
                                        if exists (attribute "AXDescription" of elem) then
                                            set elemDesc to value of attribute "AXDescription" of elem
                                            if elemDesc is not "New chat" and elemDesc is not "" then
                                                set end of conversationsList to elemDesc
                                            end if
                                        end if
                                    end try
                                end repeat
                            end if
                            
                            -- If still no conversations found, return a specific message
                            if (count of conversationsList) is 0 then
                                return "No conversations found"
                            end if
                        on error errMsg
                            -- Return error message for debugging
                            return "Error: " & errMsg
                        end try
                        
                        return conversationsList
                    end tell
                end tell
            end tell
        '''
        
        result = subprocess.run(
            ["osascript", "-e", applescript],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"AppleScript error: {result.stderr}")
        
        # Parse the AppleScript result into a list
        result_text = result.stdout.strip()
        
        if result_text == "ChatGPT is not running":
            raise Exception("ChatGPT application is not running")
        elif result_text == "No ChatGPT window found":
            raise Exception("No ChatGPT window found")
        elif result_text == "No conversations found":
            return []
        elif result_text.startswith("Error:"):
            raise Exception(result_text)
        
        # Split comma-separated conversation list
        conversations = [conv.strip() for conv in result_text.split(", ")]
        return conversations
        
    except Exception as e:
        raise Exception(f"Error retrieving conversations: {str(e)}")

def main():
    """Main entry point for the MCP server"""
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
