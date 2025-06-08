import subprocess


def force_copy_to_clipboard(text):
    """클립보드에 텍스트 복사"""
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