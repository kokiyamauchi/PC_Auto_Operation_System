import requests

class LLMInterface:
    def __init__(self, api_endpoint):
        self.api_endpoint = api_endpoint

    def send_screenshot(self, file_path):
        """スクリーンショットをLLMに送信し、解析結果を受け取る"""
        with open(file_path, 'rb') as file:
            response = requests.post(self.api_endpoint, files={'file': file})
        return response.json()

