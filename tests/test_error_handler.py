import unittest
from src.execution.error_handler import ErrorHandler

class TestErrorHandler(unittest.TestCase):
    def test_handle_error(self):
        handler = ErrorHandler()
        self.assertIsNone(handler.handle_error("Sample Error"))

