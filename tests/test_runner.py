import unittest
from src.execution.runner import ScriptRunner

class TestScriptRunner(unittest.TestCase):
    def test_run_python_script(self):
        runner = ScriptRunner()
        result = runner.run_script('sample_script.py', script_type='python')
        self.assertIsNone(result)

