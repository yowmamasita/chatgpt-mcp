"""
Improved ChatGPT response extraction based on UI investigation findings.
This module provides a more robust approach to extracting responses.
"""

import subprocess
import asyncio
import logging
from typing import Optional, List, Tuple

logger = logging.getLogger(__name__)


class ImprovedChatGPTExtractor:
    """Improved extraction methods for ChatGPT responses"""
    
    @staticmethod
    def run_applescript(script: str) -> Tuple[bool, str]:
        """Run AppleScript and return success status and output"""
        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0, result.stdout.strip()
        except subprocess.TimeoutExpired:
            return False, "Script timed out"
        except Exception as e:
            return False, str(e)
    
    async def extract_response_method_1(self) -> Optional[str]:
        """Method 1: Enhanced extraction using class-based search"""
        script = '''
        tell application "System Events"
            tell process "ChatGPT"
                if not (exists window 1) then
                    return "ERROR: No ChatGPT window found"
                end if
                
                tell window 1
                    set allTexts to {}
                    set allElements to entire contents
                    
                    repeat with elem in allElements
                        try
                            if class of elem is static text then
                                set textContent to missing value
                                
                                -- Try multiple extraction methods
                                -- Method 1: value property
                                try
                                    set textContent to value of elem
                                end try
                                
                                -- Method 2: name property
                                if textContent is missing value then
                                    try
                                        set textContent to name of elem
                                    end try
                                end if
                                
                                -- Method 3: description property
                                if textContent is missing value then
                                    try
                                        set textContent to description of elem
                                    end try
                                end if
                                
                                -- Method 4: title property
                                if textContent is missing value then
                                    try
                                        set textContent to title of elem
                                    end try
                                end if
                                
                                -- Add to results if we got text
                                if textContent is not missing value then
                                    set textStr to textContent as string
                                    if length of textStr > 0 then
                                        set end of allTexts to textStr
                                    end if
                                end if
                            end if
                        end try
                    end repeat
                    
                    -- Return results
                    if (count of allTexts) > 0 then
                        set AppleScript's text item delimiters to linefeed
                        return (allTexts as text)
                    else
                        return "ERROR: No text extracted"
                    end if
                end tell
            end tell
        end tell
        '''
        
        success, result = self.run_applescript(script)
        if not success:
            logger.error(f"AppleScript failed: {result}")
            return None
        
        if result.startswith("ERROR:"):
            logger.warning(f"Extraction error: {result}")
            return None
        
        return self._process_extracted_text(result)
    
    async def extract_response_method_2(self) -> Optional[str]:
        """Method 2: Group-based hierarchical extraction"""
        script = '''
        tell application "System Events"
            tell process "ChatGPT"
                if not (exists window 1) then
                    return "ERROR: No window"
                end if
                
                tell window 1
                    set allTexts to {}
                    
                    -- Navigate through groups
                    repeat with grp in UI elements
                        if role of grp is "AXGroup" then
                            -- Check each group for text content
                            repeat with subelem in entire contents of grp
                                try
                                    if role of subelem is "AXStaticText" then
                                        set textContent to description of subelem
                                        if textContent is missing value then
                                            set textContent to value of subelem
                                        end if
                                        
                                        if textContent is not missing value then
                                            set textStr to textContent as string
                                            if length of textStr > 0 then
                                                set end of allTexts to textStr
                                            end if
                                        end if
                                    end if
                                end try
                            end repeat
                        end if
                    end repeat
                    
                    if (count of allTexts) > 0 then
                        set AppleScript's text item delimiters to linefeed
                        return (allTexts as text)
                    else
                        return "ERROR: No text in groups"
                    end if
                end tell
            end tell
        end tell
        '''
        
        success, result = self.run_applescript(script)
        if not success or result.startswith("ERROR:"):
            return None
        
        return self._process_extracted_text(result)
    
    async def extract_response_method_3(self) -> Optional[str]:
        """Method 3: Direct UI element class-based extraction"""
        script = '''
        tell application "System Events"
            tell process "ChatGPT"
                if not (exists window 1) then
                    return "ERROR: No window"
                end if
                
                tell window 1
                    set allTexts to {}
                    
                    -- Try using class instead of role
                    repeat with elem in entire contents
                        try
                            if class of elem is static text then
                                set textContent to value of elem
                                if textContent is missing value then
                                    set textContent to name of elem
                                end if
                                
                                if textContent is not missing value then
                                    set textStr to textContent as string
                                    if length of textStr > 0 then
                                        set end of allTexts to textStr
                                    end if
                                end if
                            end if
                        end try
                    end repeat
                    
                    if (count of allTexts) > 0 then
                        set AppleScript's text item delimiters to linefeed
                        return (allTexts as text)
                    else
                        return "ERROR: No static text elements"
                    end if
                end tell
            end tell
        end tell
        '''
        
        success, result = self.run_applescript(script)
        if not success or result.startswith("ERROR:"):
            return None
        
        return self._process_extracted_text(result)
    
    def _process_extracted_text(self, raw_text: str) -> str:
        """Process extracted text to remove UI elements and format properly"""
        if not raw_text:
            return ""
        
        # Split into lines
        elements = [e.strip() for e in raw_text.split('\n') if e.strip()]
        
        # Enhanced UI element list based on investigation
        ui_elements = {
            # Buttons and controls
            'Regenerate', 'Continue generating', 'Stop generating', 'Copy',
            'Send message', 'Reply...', 'New chat',
            # UI indicators
            '▍', '│', '─', '┌', '┐', '└', '┘',
            # Navigation elements
            'ChatGPT', 'Today', 'Yesterday', 'Previous 7 Days', 'Previous 30 Days',
            # Status messages
            'Thinking...', 'Typing...', 'ChatGPT is typing...',
            # Common UI labels
            'You', 'ChatGPT', 'User', 'Assistant'
        }
        
        # Filter out UI elements
        filtered_elements = []
        for elem in elements:
            # Skip if it's a known UI element
            if elem in ui_elements:
                continue
            
            # Skip very short elements (likely UI)
            if len(elem) <= 2:
                continue
            
            # Skip elements that are just numbers or single words (likely UI)
            if elem.isdigit() or (len(elem.split()) == 1 and len(elem) < 10):
                continue
            
            filtered_elements.append(elem)
        
        if not filtered_elements:
            return ""
        
        # Try to identify message boundaries
        return self._extract_assistant_response(filtered_elements)
    
    def _extract_assistant_response(self, elements: List[str]) -> str:
        """Extract the assistant's response from filtered elements"""
        # Enhanced prompt patterns
        user_prompt_patterns = [
            # Question patterns
            lambda e: e.endswith('?') and len(e) > 10,
            # Command patterns
            lambda e: any(e.startswith(cmd) for cmd in [
                'Please ', 'Can you ', 'Could you ', 'Would you ',
                'Write ', 'Create ', 'Generate ', 'Make ', 'Build ',
                'Explain ', 'Describe ', 'List ', 'Show ', 'Tell ',
                'What ', 'How ', 'Why ', 'When ', 'Where ', 'Who ',
                'Debug ', 'Fix ', 'Update ', 'Add ', 'Remove ', 'Delete ',
                'Analyze ', 'Help ', 'Find ', 'Search ', 'Look '
            ]),
            # Contains request keywords
            lambda e: any(word in e.lower() for word in [
                'please', 'help', 'need', 'want', 'would like', 'could you',
                'can you', 'wondering', 'question', 'asking'
            ]) and len(e) > 20,
        ]
        
        # Find the last user prompt
        last_prompt_index = -1
        for i in range(len(elements) - 1, -1, -1):
            elem = elements[i]
            if any(pattern(elem) for pattern in user_prompt_patterns):
                last_prompt_index = i
                break
        
        # Extract response after the prompt
        if last_prompt_index >= 0 and last_prompt_index < len(elements) - 1:
            response_elements = elements[last_prompt_index + 1:]
        else:
            # No clear prompt found - look for assistant response patterns
            assistant_start_index = -1
            assistant_patterns = [
                'I\'ll', 'I can', 'I\'d', 'I would', 'I think',
                'Here\'s', 'Here are', 'Here is',
                'Based on', 'According to', 'To ',
                'The ', 'This ', 'That ', 'These ', 'Those ',
                'Yes,', 'No,', 'Sure,', 'Certainly,',
                'Let me', 'Let\'s'
            ]
            
            for i, elem in enumerate(elements):
                if any(elem.startswith(pattern) for pattern in assistant_patterns):
                    assistant_start_index = i
                    break
            
            if assistant_start_index >= 0:
                response_elements = elements[assistant_start_index:]
            else:
                # Return all elements as fallback
                response_elements = elements
        
        # Join response elements
        response = '\n'.join(response_elements)
        
        # Clean up any remaining artifacts
        response = response.replace('▍', '').strip()
        
        # Remove multiple blank lines
        lines = response.split('\n')
        cleaned_lines = []
        prev_blank = False
        for line in lines:
            is_blank = not line.strip()
            if not (is_blank and prev_blank):
                cleaned_lines.append(line)
            prev_blank = is_blank
        
        return '\n'.join(cleaned_lines).strip()
    
    async def extract_with_fallback(self) -> str:
        """Try multiple extraction methods with fallback"""
        # Try each method in order
        methods = [
            ("Enhanced description-based", self.extract_response_method_1),
            ("Group hierarchical", self.extract_response_method_2),
            ("Class-based", self.extract_response_method_3),
        ]
        
        for method_name, method in methods:
            logger.debug(f"Trying extraction method: {method_name}")
            try:
                result = await method()
                if result and len(result) > 5:  # Ensure we got meaningful content
                    logger.debug(f"Successfully extracted using {method_name}")
                    return result
            except Exception as e:
                logger.debug(f"Method {method_name} failed: {e}")
        
        # All methods failed
        logger.warning("All extraction methods failed")
        return "Failed to extract response from ChatGPT. The app might be in an unexpected state."


# Standalone function that can be used as a drop-in replacement
async def get_chatgpt_response_improved() -> str:
    """Improved ChatGPT response extraction using multiple methods with fallback"""
    extractor = ImprovedChatGPTExtractor()
    return await extractor.extract_with_fallback()


# Synchronous version for compatibility
def get_chatgpt_response_improved_sync() -> str:
    """Synchronous version of improved extraction"""
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(get_chatgpt_response_improved())
    finally:
        loop.close()


if __name__ == "__main__":
    # Test the improved extraction
    print("Testing improved ChatGPT response extraction...")
    result = get_chatgpt_response_improved_sync()
    print(f"Result: {result}")