import os
from PIL import ImageGrab  # Windowsの場合、Pillowライブラリを使用
import datetime

class ScreenshotCapture:
    def __init__(self, save_path='data/screenshots/'):
        self.save_path = save_path

    def capture_screen(self):
        """指定された画面のスクリーンショットを取得し、保存する"""
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = os.path.join(self.save_path, f'screenshot_{timestamp}.png')
        screenshot = ImageGrab.grab()
        screenshot.save(file_path)
        return file_path

