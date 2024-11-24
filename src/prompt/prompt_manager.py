# prompt_manager.py
import os
import yaml

class PromptManager:
    def __init__(self, prompt_dir='prompts'):
        self.prompt_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), prompt_dir)
        os.makedirs(self.prompt_dir, exist_ok=True)
        self.prompts = self._load_prompts()

    def _load_prompts(self):
        prompts = {}
        try:
            for filename in os.listdir(self.prompt_dir):
                if filename.endswith('.yaml'):
                    yaml_path = os.path.join(self.prompt_dir, filename)
                    with open(yaml_path, 'r', encoding='utf-8') as f:
                        prompts.update(yaml.safe_load(f))
        except Exception as e:
            print(f"Error loading prompts: {e}")
        return prompts

    def select_prompt(self, template_name):

        if template_name == 'task_break_down':
            return self.prompts['task_break_down']


    def merge_prompt(self, template_name, prompt, goal):
        if template_name == 'task_break_down':
            return prompt.format(goal=goal)


