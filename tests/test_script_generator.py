import unittest
from src.llm.script_generator import ScriptGenerator

class TestScriptGenerator(unittest.TestCase):
    def test_generate_python_script(self):
        generator = ScriptGenerator()
        script = generator.generate_script(llm_response={}, script_type='python')
        self.assertIn('Generated Python Script', script)

