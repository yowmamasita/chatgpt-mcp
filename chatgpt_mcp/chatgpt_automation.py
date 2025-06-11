import subprocess
import time
try:
    from chatgpt_mcp.button_helper import ChatGPTButtonHelper
except ImportError:
    from button_helper import ChatGPTButtonHelper


class ChatGPTAutomation:
    def __init__(self):
        self.button_helper = ChatGPTButtonHelper()
        
    def activate_chatgpt(self):
        """Activate ChatGPT Desktop app"""
        subprocess.run(['osascript', '-e', 'tell application "ChatGPT" to activate'])
        time.sleep(1)

    def send_message_with_keystroke(self, message):
        """Send message using clipboard paste for speed and reliability"""
        time.sleep(0.2)  # Reduced delay since pasting is faster
        # Paste the message and press Enter
        self._type_with_applescript(message, press_enter=True)
    
    
    def send_message_with_button(self, message):
        """Send message using the submit button instead of Enter key"""
        time.sleep(0.5)
        
        # Type the message
        self._type_with_applescript(message, press_enter=False)
        
        # Wait for button to be in submit state
        if self.button_helper.wait_for_button_state('submit', timeout=5):
            # Click the submit button
            return self.button_helper.click_action_button()
        else:
            print("Submit button not ready")
            return False
    
    def stop_generation(self):
        """Stop the current generation if ChatGPT is processing"""
        if self.button_helper.is_processing():
            return self.button_helper.click_action_button()
        return False
    
    def get_button_state(self):
        """Get the current state of the action button"""
        button_info = self.button_helper.find_action_button()
        if button_info:
            return button_info.get('state', 'unknown')
        return None
    
    def start_new_chat(self):
        """Start a new chat conversation in ChatGPT"""
        # The New Chat button is consistently at this position in the sidebar
        script = '''
        tell application "System Events"
            tell process "ChatGPT"
                set frontmost to true
                delay 0.5
                
                -- Click on the New Chat button position
                -- Based on UI analysis, it's centered in the sidebar around x:362, y:200
                click at {362, 200}
                
                delay 0.5
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        return result.returncode == 0
    
    def _type_with_applescript(self, text, press_enter=False):
        """Type text using clipboard and paste for speed and reliability"""
        # First, copy text to clipboard
        process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE, text=True)
        process.communicate(input=text)
        
        # Then paste using Cmd+V
        script = '''
        tell application "System Events"
            tell process "ChatGPT"
                -- Clear any existing text with Cmd+A and Delete
                keystroke "a" using command down
                delay 0.1
                key code 51  -- delete
                delay 0.1
                
                -- Paste text from clipboard
                keystroke "v" using command down
                delay 0.2
        '''
        
        if press_enter:
            script += '''
                -- Press Enter key to send
                key code 36
            '''
        
        script += '''
            end tell
        end tell
        '''
        
        subprocess.run(['osascript', '-e', script], capture_output=True, text=True)


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