import unittest
from src.screenshot.capture import ScreenshotCapture

class TestScreenshotCapture(unittest.TestCase):
    def test_capture_screen(self):
        capturer = ScreenshotCapture()
        result = capturer.capture_screen()
        self.assertTrue(result.endswith('.png'))
