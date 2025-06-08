import subprocess
import time
import pyautogui
from typing import Optional
from mcp.server.fastmcp import FastMCP
import subprocess

def force_copy_to_clipboard(text):
    # 특수문자 이스케이프 처리
    escaped_text = text.replace('"', '\\"').replace("'", "\\'")
    
    # AppleScript로 직접 클립보드 설정
    script = f'''
    on run
        set the clipboard to "{escaped_text}"
    end run
    '''
    
    subprocess.run(['osascript', '-e', script])
    
    # 확인
    result = subprocess.run(['pbpaste'], capture_output=True, text=True)
    print(f"클립보드 확인: {result.stdout[:50]}...")
def paste_to_active_app():
    """현재 활성화된 앱에 붙여넣기"""
    script = '''
    tell application "System Events"
        keystroke "v" using command down
    end tell
    '''
    subprocess.run(['osascript', '-e', script])

class ChatGPTAutomation:
    def __init__(self):
        # 안전 설정
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
        
    def activate_chatgpt(self):
        """ChatGPT Desktop 앱 활성화"""
        # macOS의 경우
        subprocess.run(['osascript', '-e', 
            'tell application "ChatGPT" to activate'])
        time.sleep(1)
        
    def send_message(self, message):
        """메시지 전송"""
        # 클립보드를 통한 안전한 한글 입력
        time.sleep(0.3)  # 클립보드 복사 완료 대기
        force_copy_to_clipboard(message)
        paste_to_active_app()  # 클립보드 내용 가져오기
        time.sleep(0.5)  # 붙여넣기 완료 대기
        pyautogui.press('enter')

# Initialize the MCP server
mcp = FastMCP("chatgpt")
chatgpt_automation = ChatGPTAutomation()

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
        # Activate ChatGPT and send message
        chatgpt_automation.activate_chatgpt()
        chatgpt_automation.send_message(prompt)
        
        return "Message sent to ChatGPT successfully. Please check the ChatGPT app for the response."
        
    except Exception as e:
        raise Exception(f"Failed to send message to ChatGPT: {str(e)}")

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
