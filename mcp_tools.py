import subprocess
from mcp.server.fastmcp import FastMCP
from chatgpt_automation import ChatGPTAutomation, check_chatgpt_access


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
                        set maxWaitTime to 120 -- Maximum wait time in seconds
                        set waitInterval to 1 -- Check interval in seconds
                        set totalWaitTime to 0
                        set previousText to ""
                        set stableCount to 0
                        set requiredStableChecks to 3 -- Number of consecutive stable checks required
                        
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
        # 프롬프트에서 개행 문자 제거 및 더블쿼츠를 싱글쿼츠로 변경
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


def setup_mcp_tools(mcp: FastMCP):
    """MCP 도구들을 설정"""
    
    @mcp.tool()
    async def ask_chatgpt_tool(prompt: str) -> str:
        """Send a prompt to ChatGPT and return the response."""
        return await ask_chatgpt(prompt)

    @mcp.tool()
    async def get_chatgpt_response_tool() -> str:
        """Get the latest response from ChatGPT after sending a message."""
        return await get_chatgpt_response()

    @mcp.tool()
    async def get_conversations_tool() -> list[str]:
        """Get available conversations from ChatGPT."""
        return await get_conversations()
