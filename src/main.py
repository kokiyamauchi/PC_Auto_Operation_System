import os
from src.screenshot.capture import ScreenshotCapture
from src.llm.interface import LLMInterface
from src.llm.script_generator import ScriptGenerator
from src.execution.runner import ScriptRunner
from src.feedback_loop.checker import FeedbackLoopChecker
from src.task_manager.task_queue import TaskQueueManager
from src.error_handling.retry_mechanism import RetryMechanism
from src.error_handling.notification import NotificationManager
from src.utils.logger import setup_logger

import yaml

def load_config(file_path='config/settings.yaml'):
    """設定ファイルを読み込む関数"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"設定ファイルが見つかりません: {file_path}")
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# ロガーのセットアップ
logger = setup_logger()

def initialize_task_queue(config):
    """タスクキューを初期化"""
    initial_tasks = config.get('initial_tasks', [])
    
    if not initial_tasks:
        logger.warning("初期タスクが設定ファイルにありません。デフォルトタスクを設定します。")
        initial_tasks = [
            {"id": 1, "type": "screenshot_analysis", "description": "Take a screenshot and analyze."}
        ]
    
    task_queue = TaskQueueManager()
    for task in initial_tasks:
        task_queue.add_task(task)
    
    return task_queue

def main():
    # 設定の読み込み
    try:
        config = load_config()
    except FileNotFoundError as e:
        logger.error(str(e))
        return

    # 初期化
    screenshot_capturer = ScreenshotCapture()
    llm_interface = LLMInterface(api_endpoint=config['llm_api_endpoint'])
    script_generator = ScriptGenerator()
    script_runner = ScriptRunner()
    feedback_checker = FeedbackLoopChecker(api_endpoint=config['llm_api_endpoint'])
    task_queue = initialize_task_queue(config)
    retry_mechanism = RetryMechanism(max_retries=config['retry_attempts'])
    notification_manager = NotificationManager(
        smtp_server=config['smtp_server'],
        port=config['smtp_port']
    )

    # タスクを取得し処理開始
    while not task_queue.is_empty():
        task = task_queue.get_next_task()
        logger.info(f"Processing task: {task}")

        # スクリーンショット取得と送信
        screenshot_path = screenshot_capturer.capture_screen()
        llm_response = llm_interface.send_screenshot(screenshot_path)

        # スクリプトの生成と実行
        script = script_generator.generate_script(llm_response, script_type='python')
        script_path = os.path.join('data/scripts/python/', 'generated_script.py')
        with open(script_path, 'w') as f:
            f.write(script)

        # スクリプト実行と進行状況チェック
        if retry_mechanism.execute_with_retry(script_runner.run_script, script_path, 'python'):
            logger.info("Task executed successfully.")
        else:
            logger.error("Task failed after maximum retries.")
            notification_manager.send_notification(
                recipient_email=config['notification_recipient_email'],
                subject='Task Failure Notification',
                message='The task has failed after multiple attempts.'
            )

        # フィードバックループで進行状況確認
        if not feedback_checker.check_task_progress(screenshot_path):
            logger.info("Task needs re-execution.")
            task_queue.add_task(task)  # タスクを再度キューに追加

if __name__ == '__main__':
    main()