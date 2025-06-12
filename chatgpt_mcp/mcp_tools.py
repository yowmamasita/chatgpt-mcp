import subprocess
import asyncio
import json
from mcp.server.fastmcp import FastMCP
from chatgpt_mcp.chatgpt_automation import ChatGPTAutomation, check_chatgpt_access
from chatgpt_mcp.button_helper import ChatGPTButtonHelper



async def get_chatgpt_response() -> str:
    """Get the latest response from ChatGPT after sending a message.
    
    Returns:
        ChatGPT's latest response text
    """
    try:
        # Use the new comprehensive text extraction AppleScript
        applescript = '''
on run
    tell application "System Events"
        -- Check if ChatGPT process exists
        if not (exists process "ChatGPT") then
            return "{\"status\": \"error\", \"message\": \"ChatGPT process not found\"}"
        end if
        
        tell process "ChatGPT"
            -- Activate ChatGPT
            set frontmost to true
            delay 0.5
            
            -- Check if window exists
            if not (exists window 1) then
                return "{\"status\": \"error\", \"message\": \"No ChatGPT window found\"}"
            end if
            
            -- Get entire contents
            set allElements to entire contents of window 1
            
            -- Collect texts and buttons for completion detection
            set allTexts to {}
            set buttonsList to {}
            
            repeat with elem in allElements
                try
                    set elemClass to class of elem
                    
                    -- Collect static texts
                    if elemClass is static text then
                        try
                            set textContent to value of elem
                            if textContent is missing value then
                                set textContent to description of elem
                            end if
                            
                            if textContent is not missing value and length of textContent > 0 then
                                set trimmedText to textContent
                                if trimmedText is not equal to "" and trimmedText is not equal to " " then
                                    set end of allTexts to textContent
                                end if
                            end if
                        end try
                    end if
                    
                    -- Collect buttons for sequence analysis
                    if elemClass is button then
                        set end of buttonsList to elem
                    end if
                end try
            end repeat
            
            -- Universal conversation completion detection
            set conversationComplete to false
            set foundModelButton to false
            
            repeat with i from 1 to count of buttonsList
                try
                    set currentButton to item i of buttonsList
                    set btnHelp to help of currentButton
                    set btnValue to value of currentButton
                    
                    -- Check if this is the model selection button
                    if btnValue is not missing value and btnHelp is not missing value then
                        if (btnHelp contains "모델" or btnHelp contains "model" or btnHelp contains "GPT") and (length of btnValue > 0) then
                            set foundModelButton to true
                            -- Check if next button exists and has voice/input related functionality
                            if i < (count of buttonsList) then
                                set nextButton to item (i + 1) of buttonsList
                                try
                                    set nextBtnHelp to help of nextButton
                                    if nextBtnHelp is not missing value then
                                        if (nextBtnHelp contains "음성 받아쓰기" or nextBtnHelp contains "Transcribe voice") then
                                            set conversationComplete to true
                                        end if
                                    end if
                                end try
                            end if
                            exit repeat
                        end if
                    end if
                end try
            end repeat
            
            -- Fallback: Check if we have any voice-related buttons at all
            if not conversationComplete and foundModelButton then
                repeat with btnElement in buttonsList
                    try
                        set btnHelp to help of btnElement
                        if btnHelp is not missing value then
                            if (btnHelp contains "음성" or btnHelp contains "받아쓰기" or btnHelp contains "voice" or btnHelp contains "dictation" or btnHelp contains "speech") then
                                set conversationComplete to true
                                exit repeat
                            end if
                        end if
                    end try
                end repeat
            end if
            
            -- Build simplified JSON result
            set jsonResult to "{\"status\": \"success\", "
            
            -- Add text count and texts
            set textCount to count of allTexts
            set jsonResult to jsonResult & "\"textCount\": " & textCount & ", \"texts\": ["
            
            repeat with i from 1 to textCount
                set currentText to item i of allTexts
                -- Escape JSON characters
                set currentText to my escapeJSON(currentText)
                
                set jsonResult to jsonResult & "\"" & currentText & "\""
                if i < textCount then
                    set jsonResult to jsonResult & ", "
                end if
            end repeat
            
            set jsonResult to jsonResult & "], "
            
            -- Add only the essential indicator
            set jsonResult to jsonResult & "\"indicators\": {"
            set jsonResult to jsonResult & "\"conversationComplete\": " & conversationComplete
            set jsonResult to jsonResult & "}}"
            
            return jsonResult
        end tell
    end tell
end run

-- JSON escape function
on escapeJSON(txt)
    set txt to my replaceText(txt, "\\", "\\\\")
    set txt to my replaceText(txt, "\"", "\\\"")
    set txt to my replaceText(txt, return, "\\n")
    set txt to my replaceText(txt, linefeed, "\\n")
    set txt to my replaceText(txt, tab, "\\t")
    return txt
end escapeJSON

-- Text replacement function
on replaceText(someText, oldItem, newItem)
    set {tempTID, AppleScript's text item delimiters} to {AppleScript's text item delimiters, oldItem}
    try
        set {textItems, AppleScript's text item delimiters} to {text items of someText, newItem}
        set {someText, AppleScript's text item delimiters} to {textItems as text, tempTID}
    on error errorMessage number errorNumber
        set AppleScript's text item delimiters to tempTID
        error errorMessage number errorNumber
    end try
    return someText
end replaceText
'''
        
        result = subprocess.run(
            ["osascript", "-e", applescript],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"AppleScript error: {result.stderr}")
        
        # Parse JSON result
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return result.stdout.strip()
        
        # Check for errors
        if data.get('status') == 'error':
            raise Exception(data.get('message', 'Unknown error'))
        
        # Extract texts from JSON
        texts = data.get('texts', [])
        if not texts:
            return "No response received from ChatGPT."
        
        # Join all texts with newlines
        full_text = '\n'.join(texts)
        
        # Filter out UI elements and system texts
        ui_elements = ['Regenerate', 'Continue generating', 'Stop generating', 
                      'Copy', '▍', 'ChatGPT', 'Send a message', 'Message ChatGPT',
                      'Type a message', 'Ask anything']
        
        # Split text into lines for better filtering
        lines = full_text.split('\n')
        filtered_lines = []
        
        for line in lines:
            # Skip empty lines and UI elements
            line = line.strip()
            if not line or line in ui_elements:
                continue
            
            # Skip lines that are just UI elements
            is_ui_element = False
            for ui_elem in ui_elements:
                if line == ui_elem:
                    is_ui_element = True
                    break
            
            if not is_ui_element:
                filtered_lines.append(line)
        
        # Find the user's prompt and ChatGPT's response
        # The response typically comes after the user's prompt
        response_text = '\n'.join(filtered_lines)
        
        # Try to identify and extract just ChatGPT's response
        # This is a heuristic approach - may need refinement
        if len(filtered_lines) > 1:
            # Assume the first line might be the user's prompt
            # and the rest is ChatGPT's response
            # But only if there's a clear separation
            potential_response = '\n'.join(filtered_lines[1:])
            if potential_response and len(potential_response) > 10:
                response_text = potential_response
        
        return response_text if response_text else "No response received from ChatGPT."
        
    except Exception as e:
        # Fallback to improved extraction if available
        try:
            from chatgpt_mcp.improved_extraction import get_chatgpt_response_improved
            return await get_chatgpt_response_improved()
        except ImportError:
            pass
        
        raise Exception(f"Failed to get response from ChatGPT: {str(e)}")


async def ask_chatgpt(prompt: str) -> str:
    """Send a prompt to ChatGPT and wait for the complete response.
    
    This function handles the entire interaction cycle:
    1. Sends the prompt to ChatGPT
    2. Waits for ChatGPT to start processing (button changes to 'stop')
    3. Waits for processing to complete (button changes back to 'submit' or 'waveform')
    4. Retrieves and returns the complete response
    
    Args:
        prompt: The text to send to ChatGPT
    
    Returns:
        ChatGPT's complete response
    """
    await check_chatgpt_access()
    
    button_helper = ChatGPTButtonHelper()
    
    try:
        # Since we're using clipboard paste, we can keep newlines
        # Just escape any quotes to prevent issues
        cleaned_prompt = prompt.replace('"', "'").strip()
        
        # Activate ChatGPT and send message
        chatgpt_automation = ChatGPTAutomation()
        chatgpt_automation.activate_chatgpt()
        
        # Check initial button state
        initial_button = button_helper.find_action_button()
        if not initial_button:
            # Try activating ChatGPT again
            chatgpt_automation.activate_chatgpt()
            await asyncio.sleep(1)
            initial_button = button_helper.find_action_button()
            if not initial_button:
                raise Exception("Cannot find ChatGPT action button. Make sure ChatGPT is open and visible.")
        
        # Send the message
        chatgpt_automation.send_message_with_keystroke(cleaned_prompt)
        
        # Wait for ChatGPT to start processing (button changes to 'stop')
        started_processing = False
        button_states_seen = []
        
        for i in range(20):  # Wait up to 10 seconds
            button_info = button_helper.find_action_button()
            current_state = button_info.get('state') if button_info else None
            button_states_seen.append(current_state)
            
            if button_helper.is_processing():
                started_processing = True
                break
            
            # Check if response might already be complete (very quick responses)
            if current_state in ['submit', 'waveform', 'voice'] and i > 2:
                # Give it a moment to ensure any response is rendered
                await asyncio.sleep(1)
                response = await get_chatgpt_response()
                if response and response != "No response received from ChatGPT." and len(response) > 1:
                    return response
            
            await asyncio.sleep(0.5)
        
        if not started_processing:
            # Log what states we saw for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"Button states seen while waiting: {button_states_seen}")
            
            # Try one more time to get response in case it completed very quickly
            await asyncio.sleep(1)
            response = await get_chatgpt_response()
            if response and response != "No response received from ChatGPT." and len(response) > 1:
                return response
            
            # If still no response, raise error with more context
            button_state = button_helper.find_action_button()
            current_state = button_state.get('state') if button_state else 'not found'
            raise Exception(f"ChatGPT did not start processing the message. Current button state: {current_state}. States seen: {button_states_seen}")
        
        # Wait for processing to complete
        import time
        start_time = time.time()
        initial_timeout = 15  # 15 seconds initial timeout
        max_wait = 300  # 5 minutes max for longer responses
        
        # Response completion will be checked via the AppleScript JSON response
        has_copy_extractor = False
        
        # First, wait with the shorter timeout
        while time.time() - start_time < initial_timeout:
            button_info = button_helper.find_action_button()
            button_state = button_info.get('state') if button_info else None
            
            # If button is no longer in 'stop' state, processing is complete
            if button_state and button_state != 'stop':
                # Wait a bit more to ensure text is fully rendered
                await asyncio.sleep(1)
                break
            
            await asyncio.sleep(0.2)  # Check more frequently
        
        # If still processing after initial timeout, continue waiting but check for response
        if button_helper.is_processing():
            # Try to get response anyway - ChatGPT might have responded but button is stuck
            try:
                response = await get_chatgpt_response()
                if response and response != "No response received from ChatGPT." and len(response) > 10:
                    return response
            except:
                pass
            
            # Continue waiting for button state change
            while time.time() - start_time < max_wait:
                button_info = button_helper.find_action_button()
                button_state = button_info.get('state') if button_info else None
                
                if button_state and button_state != 'stop':
                    await asyncio.sleep(1)
                    break
                
                await asyncio.sleep(0.5)
        
        # Get the complete response
        response = await get_chatgpt_response()
        
        if not response or response == "No response received from ChatGPT.":
            raise Exception("Failed to retrieve response from ChatGPT")
        
        return response
        
    except Exception as e:
        raise Exception(f"Failed to interact with ChatGPT: {str(e)}")


async def ask_chatgpt_simple(prompt: str) -> str:
    """Simpler version of ask_chatgpt that doesn't rely on button detection.
    
    This is a fallback for when button detection fails.
    
    Args:
        prompt: The text to send to ChatGPT
    
    Returns:
        ChatGPT's response
    """
    await check_chatgpt_access()
    
    try:
        # Clean prompt
        cleaned_prompt = prompt.replace('"', "'").strip()
        
        # Activate ChatGPT and send message
        chatgpt_automation = ChatGPTAutomation()
        chatgpt_automation.activate_chatgpt()
        
        # Send the message
        chatgpt_automation.send_message_with_keystroke(cleaned_prompt)
        
        # Wait a fixed amount of time for response
        # This is less sophisticated but more reliable
        await asyncio.sleep(5)  # Initial wait for ChatGPT to start
        
        # Try to get response periodically
        for i in range(6):  # Try for up to 30 seconds
            response = await get_chatgpt_response()
            if response and response != "No response received from ChatGPT." and len(response) > 1:
                return response
            await asyncio.sleep(5)
        
        # Final attempt
        response = await get_chatgpt_response()
        if response and response != "No response received from ChatGPT.":
            return response
        
        return "Failed to get response from ChatGPT. Please check if ChatGPT is responding."
        
    except Exception as e:
        raise Exception(f"Failed to interact with ChatGPT: {str(e)}")


async def new_chat() -> str:
    """Start a new chat conversation in ChatGPT.
    
    Returns:
        Success message or error description
    """
    await check_chatgpt_access()
    
    try:
        # Create automation instance and start new chat
        chatgpt_automation = ChatGPTAutomation()
        chatgpt_automation.activate_chatgpt()
        
        # Start new chat
        success = chatgpt_automation.start_new_chat()
        
        if success:
            # Wait a moment for the UI to update
            await asyncio.sleep(1)
            
            # Verify we're in a new chat by checking button state
            button_helper = ChatGPTButtonHelper()
            button_info = button_helper.find_action_button()
            
            if button_info and button_info.get('state') in ['voice', 'waveform']:
                return "Successfully started a new chat conversation"
            else:
                return "New chat started, but state verification unclear"
        else:
            raise Exception("Failed to click New Chat button")
            
    except Exception as e:
        raise Exception(f"Failed to start new chat: {str(e)}")


def setup_mcp_tools(mcp: FastMCP):
    """Setup MCP tools"""
    
    @mcp.tool()
    async def ask_chatgpt_tool(prompt: str) -> str:
        """Send a prompt to ChatGPT and return the complete response.
        
        This tool handles the entire interaction cycle:
        1. Sends the prompt to ChatGPT
        2. Waits for processing to complete
        3. Returns the complete response
        
        Args:
            prompt: The text to send to ChatGPT
            
        Returns:
            ChatGPT's complete response text
        """
        try:
            return await ask_chatgpt(prompt)
        except Exception as e:
            # If button detection fails, try a simpler approach
            if "button" in str(e).lower() or "processing" in str(e).lower():
                return await ask_chatgpt_simple(prompt)
            raise
    
    @mcp.tool()
    async def new_chat_tool() -> str:
        """Start a new chat conversation in ChatGPT.
        
        This tool clicks the 'New Chat' button to start a fresh conversation,
        clearing any previous context.
        
        Returns:
            Success message indicating the new chat has been started
        """
        return await new_chat()
