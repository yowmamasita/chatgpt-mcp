import subprocess
import time
import pyautogui
from utils.clipboard_utils import force_copy_to_clipboard, paste_to_active_app


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
        time.sleep(0.5)  # 클립보드 복사 완료 대기
        # 백스페이스를 먼저 입력
        pyautogui.press('backspace')
        time.sleep(0.1)
        force_copy_to_clipboard(message)
        paste_to_active_app()  # 클립보드 내용 가져오기
        time.sleep(0.5)  # 붙여넣기 완료 대기
        pyautogui.press('enter')


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