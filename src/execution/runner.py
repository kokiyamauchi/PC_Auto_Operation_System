import subprocess

class ScriptRunner:
    def __init__(self):
        pass

    def run_script(self, script_path, script_type='python'):
        """指定されたスクリプトを実行する"""
        try:
            if script_type == 'python':
                subprocess.run(['python', script_path], check=True)
            elif script_type == 'batch':
                subprocess.run(['cmd', '/c', script_path], check=True)
            elif script_type == 'shell':
                subprocess.run(['bash', script_path], check=True)
            else:
                raise ValueError("Unsupported script type")
        except subprocess.CalledProcessError as e:
            print(f"Error executing script: {e}")

