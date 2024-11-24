# script_generator.py
class ScriptGenerator:
    def __init__(self):
        self.supported_types = {'python', 'batch', 'shell'}

    def generate_script(self, llm_response: dict, script_type: str = 'python') -> str:
        if script_type not in self.supported_types:
            raise ValueError(f"Unsupported script type: {script_type}")

        generator_method = getattr(self, f"_generate_{script_type}_script")
        return generator_method(llm_response)

    def _generate_python_script(self, llm_response: dict) -> str:
        code = llm_response.get('code', '')
        return f"""#!/usr/bin/env python3
# Generated Python Script
{code}
"""

    def _generate_batch_script(self, llm_response: dict) -> str:
        code = llm_response.get('code', '')
        return f"""@echo off
REM Generated Batch Script
{code}
"""

    def _generate_shell_script(self, llm_response: dict) -> str:
        code = llm_response.get('code', '')
        return f"""#!/bin/bash
# Generated Shell Script
{code}
"""