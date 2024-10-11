from src.llm.interface import LLMInterface

class FeedbackLoopChecker:
    def __init__(self, api_endpoint='https://api.llmservice.com'):
        self.llm_interface = LLMInterface(api_endpoint)

    def check_task_progress(self, file_path):
        """タスクの進行状況をスクリーンショットで確認し、完了状況を評価する"""
        response = self.llm_interface.send_screenshot(file_path)
        status = response.get('status', 'incomplete')
        return status == 'complete'  # 完了状態ならTrue、未完了ならFalse
