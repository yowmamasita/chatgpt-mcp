import subprocess
import re
import time
from typing import Optional, Dict


class ChatGPTButtonHelper:
    """Helper class to find and interact with ChatGPT's main action button dynamically"""
    
    @staticmethod
    def find_action_button() -> Optional[Dict[str, any]]:
        """
        Find the main action button (submit/stop/voice) in ChatGPT.
        The button is identified by its large size (45+ pixels).
        
        Returns:
            Dictionary with button info including:
            - x, y: Position coordinates
            - width, height: Button dimensions
            - help: Help text (contains state info)
            - enabled: Whether button is enabled
            - state: 'submit', 'stop', 'waveform', or 'unknown'
        """
        script = '''
        tell application "System Events"
            tell process "ChatGPT"
                tell window 1
                    tell group 1
                        tell UI element 1  -- Split group
                            set largeButtons to {}
                            
                            repeat with grp in UI elements
                                if role of grp is "AXGroup" then
                                    repeat with elem in UI elements of grp
                                        try
                                            if role of elem is "AXButton" then
                                                set btnSize to size of elem
                                                
                                                -- Look for large buttons (45+ pixels)
                                                if (item 1 of btnSize) > 45 and (item 2 of btnSize) > 45 then
                                                    set btnPos to position of elem
                                                    set btnInfo to "{"
                                                    set btnInfo to btnInfo & "\\"x\\":" & (item 1 of btnPos) & ","
                                                    set btnInfo to btnInfo & "\\"y\\":" & (item 2 of btnPos) & ","
                                                    set btnInfo to btnInfo & "\\"width\\":" & (item 1 of btnSize) & ","
                                                    set btnInfo to btnInfo & "\\"height\\":" & (item 2 of btnSize) & ","
                                                    
                                                    -- Get help text (contains state info)
                                                    try
                                                        set helpText to help of elem
                                                        set btnInfo to btnInfo & "\\"help\\":\\"" & helpText & "\\","
                                                    on error
                                                        set btnInfo to btnInfo & "\\"help\\":null,"
                                                    end try
                                                    
                                                    -- Get enabled state
                                                    set btnInfo to btnInfo & "\\"enabled\\":" & (enabled of elem) & ","
                                                    
                                                    -- Get description
                                                    try
                                                        set btnDesc to description of elem
                                                        set btnInfo to btnInfo & "\\"description\\":\\"" & btnDesc & "\\""
                                                    on error
                                                        set btnInfo to btnInfo & "\\"description\\":null"
                                                    end try
                                                    
                                                    set btnInfo to btnInfo & "}"
                                                    set end of largeButtons to btnInfo
                                                end if
                                            end if
                                        end try
                                    end repeat
                                end if
                            end repeat
                            
                            -- Return the rightmost large button (typically our action button)
                            if (count of largeButtons) > 0 then
                                -- If multiple large buttons, return the rightmost one
                                set rightmostButton to item 1 of largeButtons
                                set maxX to 0
                                
                                repeat with btnStr in largeButtons
                                    -- Extract X position
                                    set xStart to offset of "\\"x\\":" in btnStr
                                    set xEnd to offset of "," in (text (xStart + 5) thru -1 of btnStr)
                                    set xValue to (text (xStart + 5) thru (xStart + 3 + xEnd) of btnStr) as number
                                    
                                    if xValue > maxX then
                                        set maxX to xValue
                                        set rightmostButton to btnStr
                                    end if
                                end repeat
                                
                                return rightmostButton
                            else
                                return "null"
                            end if
                        end tell
                    end tell
                end tell
            end tell
        end tell
        '''
        
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0 or result.stdout.strip() == "null":
                return None
            
            # Parse the pseudo-JSON response
            button_str = result.stdout.strip()
            button_info = {}
            
            # Extract values using regex
            x_match = re.search(r'"x":(\d+)', button_str)
            y_match = re.search(r'"y":(\d+)', button_str)
            width_match = re.search(r'"width":(\d+)', button_str)
            height_match = re.search(r'"height":(\d+)', button_str)
            help_match = re.search(r'"help":"([^"]*)"', button_str)
            enabled_match = re.search(r'"enabled":(true|false)', button_str)
            desc_match = re.search(r'"description":"([^"]*)"', button_str)
            
            if x_match and y_match:
                button_info = {
                    'x': int(x_match.group(1)),
                    'y': int(y_match.group(1)),
                    'width': int(width_match.group(1)) if width_match else 0,
                    'height': int(height_match.group(1)) if height_match else 0,
                    'help': help_match.group(1) if help_match else None,
                    'enabled': enabled_match.group(1) == 'true' if enabled_match else False,
                    'description': desc_match.group(1) if desc_match else None
                }
                
                # Determine state based on help text
                if button_info['help']:
                    help_text = button_info['help']
                    if 'Send message' in help_text:
                        button_info['state'] = 'submit'
                    elif 'Stop' in help_text:
                        button_info['state'] = 'stop'
                    elif 'Start voice' in help_text or 'voice conversation' in help_text:
                        button_info['state'] = 'voice'
                    else:
                        # Unknown help text
                        button_info['state'] = 'unknown'
                else:
                    # No help text
                    button_info['state'] = 'waveform'
                
                return button_info
            
            return None
            
        except Exception:
            return None
    
    @staticmethod
    def click_action_button() -> bool:
        """
        Click the main action button regardless of its current state.
        
        Returns:
            True if successful, False otherwise
        """
        button_info = ChatGPTButtonHelper.find_action_button()
        if not button_info:
            return False
        
        script = f'''
        tell application "System Events"
            tell process "ChatGPT"
                set frontmost to true
                delay 0.1
                click at {{{button_info['x']}, {button_info['y']}}}
            end tell
        end tell
        '''
        
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def wait_for_button_state(target_state: str, timeout: int = 10) -> bool:
        """
        Wait for the button to reach a specific state.
        
        Args:
            target_state: 'submit', 'stop', 'voice', 'waveform', or 'unknown'
            timeout: Maximum seconds to wait
            
        Returns:
            True if target state reached, False if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            button_info = ChatGPTButtonHelper.find_action_button()
            if button_info and button_info.get('state') == target_state:
                return True
            time.sleep(0.5)
        
        return False
    
    @staticmethod
    def is_processing() -> bool:
        """
        Check if ChatGPT is currently processing (button is in 'stop' state).
        
        Returns:
            True if processing, False otherwise
        """
        button_info = ChatGPTButtonHelper.find_action_button()
        return button_info and button_info.get('state') == 'stop'
    
    @staticmethod
    def can_send_message() -> bool:
        """
        Check if a message can be sent (button is in 'submit' state and enabled).
        
        Returns:
            True if can send, False otherwise
        """
        button_info = ChatGPTButtonHelper.find_action_button()
        return (button_info and 
                button_info.get('state') == 'submit' and 
                button_info.get('enabled', False))