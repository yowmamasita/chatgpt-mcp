import subprocess
import asyncio
from mcp.server.fastmcp import FastMCP
from chatgpt_mcp.chatgpt_automation import ChatGPTAutomation, check_chatgpt_access
from chatgpt_mcp.button_helper import ChatGPTButtonHelper



async def get_chatgpt_response() -> str:
    """Get the latest response from ChatGPT after sending a message.
    
    Returns:
        ChatGPT's latest response text
    """
    try:
        # Import the improved extraction
        from chatgpt_mcp.improved_extraction import get_chatgpt_response_improved
        return await get_chatgpt_response_improved()
    except ImportError:
        # Fallback to basic extraction if improved version not available
        try:
            # Use description property which actually contains the text
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
                            
                            -- Get all text content immediately
                            set frontWin to front window
                            set allUIElements to entire contents of frontWin
                            set allText to {}
                            
                            repeat with e in allUIElements
                                try
                                    if (role of e) is "AXStaticText" then
                                        set textDesc to description of e
                                        if textDesc is not missing value then
                                            set end of allText to (textDesc as string)
                                        end if
                                    end if
                                end try
                            end repeat
                            
                            -- Join all text with newlines
                            set AppleScript's text item delimiters to linefeed
                            set fullText to allText as text
                            
                            -- Return all captured text
                            return fullText
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
            
            # Get the full text and return it as-is for basic fallback
            full_text = result.stdout.strip()
            
            if not full_text:
                return "No response received from ChatGPT."
            
            # Basic cleanup only
            ui_elements = ['Regenerate', 'Continue generating', 'Stop generating', 'Copy', '▍', 'ChatGPT']
            for ui_elem in ui_elements:
                full_text = full_text.replace(ui_elem, '').strip()
            
            return full_text
            
        except Exception as e:
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
        
        # Wait for processing to complete with a shorter initial timeout
        import time
        start_time = time.time()
        initial_timeout = 15  # 15 seconds initial timeout as suggested
        max_wait = 300  # 5 minutes max for longer responses
        
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
