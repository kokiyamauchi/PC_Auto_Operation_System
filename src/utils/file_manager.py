import os

class FileManager:
    def __init__(self):
        pass

    def save_file(self, content, file_path):
        """指定されたパスにファイルを保存"""
        with open(file_path, 'w') as file:
            file.write(content)

    def load_file(self, file_path):
        """指定されたパスからファイルを読み込む"""
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                return file.read()
        return None