import subprocess
from mcp.server.fastmcp import FastMCP
from chatgpt_mcp.chatgpt_automation import ChatGPTAutomation, check_chatgpt_access


async def get_chatgpt_response() -> str:
    """Get the latest response from ChatGPT after sending a message.
    
    Returns:
        ChatGPT's latest response text
    """
    try:
        applescript = '''
            tell application "ChatGPT"
                activate
                delay 1
                tell application "System Events"
                    tell process "ChatGPT"
                        -- Check if window exists before accessing
                        if not (exists window 1) then
                            return "No ChatGPT window found"
                        end if
                        -- Wait for the response with dynamic detection
                        set maxWaitTime to 300 -- Maximum wait time in seconds (5 minutes)
                        set waitInterval to 1 -- Check interval in seconds
                        set totalWaitTime to 0
                        set previousText to ""
                        set stableCount to 0
                        set requiredStableChecks to 60 -- Number of consecutive stable checks required (60 seconds for image generation)
                        
                        repeat while totalWaitTime < maxWaitTime
                            delay waitInterval
                            set totalWaitTime to totalWaitTime + waitInterval
                            
                            -- Get current text
                            if not (exists window 1) then
                                return "No ChatGPT window found"
                            end if
                            set frontWin to front window
                            set allUIElements to entire contents of frontWin
                            set conversationText to {}
                            repeat with e in allUIElements
                                try
                                    if (role of e) is "AXStaticText" then
                                        set end of conversationText to (description of e)
                                    end if
                                end try
                            end repeat
                            
                            set AppleScript's text item delimiters to linefeed
                            set currentText to conversationText as text
                            
                            -- Check if text has stabilized (not changing anymore)
                            if currentText is equal to previousText then
                                set stableCount to stableCount + 1
                                if stableCount ≥ requiredStableChecks then
                                    -- Text has been stable for multiple checks, assume response is complete
                                    exit repeat
                                end if
                            else
                                -- Text changed, reset stable count
                                set stableCount to 0
                                set previousText to currentText
                            end if
                            
                            -- Check for response completion indicators
                            if currentText contains "▍" then
                                -- ChatGPT is still typing (blinking cursor indicator)
                                set stableCount to 0
                            else if currentText contains "Regenerate" or currentText contains "Continue generating" then
                                -- Response likely complete if these UI elements are visible
                                set stableCount to stableCount + 1
                            end if
                        end repeat
                        
                        -- Final check for text content
                        if (count of conversationText) = 0 then
                            return "No response text found. ChatGPT may still be processing or encountered an error."
                        else
                            -- Clean up the response text
                            set AppleScript's text item delimiters to linefeed
                            set responseText to conversationText as text
                            
                            return responseText
                        end if
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
        
        # Post-process the result to clean up any UI text that might have been captured
        cleaned_result = result.stdout.strip()
        cleaned_result = cleaned_result.replace('Regenerate', '').replace('Continue generating', '').replace('▍', '').strip()
        
        # More context-aware incomplete response detection
        is_likely_complete = (
            len(cleaned_result) > 50 or  # Longer responses are likely complete
            cleaned_result.endswith('.') or 
            cleaned_result.endswith('!') or 
            cleaned_result.endswith('?') or
            cleaned_result.endswith(':') or
            cleaned_result.endswith(')') or
            cleaned_result.endswith('}') or
            cleaned_result.endswith(']') or
            '\n\n' in cleaned_result or  # Multiple paragraphs suggest completeness
            cleaned_result and cleaned_result[0].isupper() and any(cleaned_result.endswith(p) for p in ['.', '!', '?'])  # Complete sentence structure
        )
        
        if len(cleaned_result) > 0 and not is_likely_complete:
            print("Warning: ChatGPT response may be incomplete")
        
        return cleaned_result if cleaned_result else "No response received from ChatGPT."
        
    except Exception as e:
        raise Exception(f"Failed to get response from ChatGPT: {str(e)}")


async def ask_chatgpt(prompt: str) -> str:
    """Send a prompt to ChatGPT and return the response.
    
    Args:
        prompt: The text to send to ChatGPT
    
    Returns:
        ChatGPT's response
    """
    await check_chatgpt_access()
    
    try:
        # Remove newline characters from prompt and change double quotes to single quotes
        cleaned_prompt = prompt.replace('\n', ' ').replace('\r', ' ').replace('"', "'").strip()
        
        # Activate ChatGPT and send message using keystroke
        chatgpt_automation = ChatGPTAutomation()
        chatgpt_automation.activate_chatgpt()
        chatgpt_automation.send_message_with_keystroke(cleaned_prompt)
        
        # Get the response
        response = await get_chatgpt_response()
        return response
        
    except Exception as e:
        raise Exception(f"Failed to send message to ChatGPT: {str(e)}")


def setup_mcp_tools(mcp: FastMCP):
    """Setup MCP tools"""
    
    @mcp.tool()
    async def ask_chatgpt_tool(prompt: str) -> str:
        """Send a prompt to ChatGPT and return the response."""
        return await ask_chatgpt(prompt)

    @mcp.tool()
    async def get_chatgpt_response_tool() -> str:
        """Get the latest response from ChatGPT after sending a message."""
        return await get_chatgpt_response()
