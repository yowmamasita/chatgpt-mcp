import subprocess
import time


class ChatGPTAutomation:
    def __init__(self):
        pass
        
    def activate_chatgpt(self):
        """Activate ChatGPT Desktop app"""
        subprocess.run(['osascript', '-e', 'tell application "ChatGPT" to activate'])
        time.sleep(1)

    def send_message_with_keystroke(self, message):
        """Send message directly using keystrokes with AppleScript"""
        time.sleep(0.5)
        self._type_with_applescript(message)
    
    def _type_with_applescript(self, text):
        """Type text using AppleScript"""
        escaped_text = text.replace('"', '\\"').replace("\\", "\\\\")
        
        script = f'''
        tell application "System Events"
            tell process "ChatGPT"
                -- First backspace
                key code 51
                delay 0.1
                
                -- Type text (each character individually)
                set textToType to "{escaped_text}"
                repeat with i from 1 to length of textToType
                    set currentChar to character i of textToType
                    keystroke currentChar
                    delay 0.01
                end repeat
                
                -- Press Enter key
                key code 36
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