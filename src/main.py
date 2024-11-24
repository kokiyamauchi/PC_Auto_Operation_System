import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from screenshot.capture import ScreenshotCapture
from llm.interface import LLMInterface
from llm.script_generator import ScriptGenerator
from execution.runner import ScriptRunner
from feedback_loop.checker import FeedbackLoopChecker
from task.task_manager import TaskManager
from task.task_status import TaskExecutionStatus
from prompt.prompt_manager import PromptManager
from error_handling.retry_mechanism import RetryMechanism
from error_handling.notification import NotificationManager
from utils.logger import setup_logger

import yaml


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def load_config(file_path='config/settings.yaml'):
    """設定ファイルを読み込む関数"""
    abs_path = os.path.join(os.path.dirname(ROOT_DIR), file_path)  # ROOT_DIRの親ディレクトリから設定ファイルを探す
    logger.debug(f"Loading configuration file from: {abs_path}")
    with open(abs_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
        logger.debug(f"Loaded configuration: {config}")
        return config

# ロガーのセットアップ
logger = setup_logger()

def setup_directories():
   """必要なディレクトリを作成"""
   dirs = [
       os.path.join(ROOT_DIR, 'config'),
       os.path.join(ROOT_DIR, 'data', 'scripts', 'python'),
       os.path.join(ROOT_DIR, 'data', 'screenshots'),
       os.path.join(ROOT_DIR, 'logs'),
       os.path.join(ROOT_DIR, 'src', 'prompt', 'templates')
   ]
   for dir_path in dirs:
       os.makedirs(dir_path, exist_ok=True)

def main():
    # 設定の読み込み
    setup_directories()
    config = load_config()
    final_goal = config['goal']
    logger.info(f"Final goal set to: {final_goal}")

    try:
        logger.debug("Starting component initialization")
        
        # プロンプトを管理するクラス
        logger.debug("Initializing PromptManager")
        prompt_manager = PromptManager()
        logger.debug("PromptManager initialized successfully")
        
        # スクリーンショットを取るクラス  
        logger.debug("Initializing ScreenshotCapture")
        screenshot_capturer = ScreenshotCapture()
        logger.debug("ScreenshotCapture initialized successfully")
        
        # LLMとやり取りするクラス
        logger.debug("Initializing LLMInterface")
        if 'claude_api_key' not in config:
            raise KeyError("claude_api_key not found in config file")
        llm_interface = LLMInterface(provider="claude", api_key=config['claude_api_key'])
        logger.debug("LLMInterface initialized successfully")
        
        # 以下も同様にログを追加
        logger.debug("Initializing ScriptGenerator")
        script_generator = ScriptGenerator()
        logger.debug("ScriptGenerator initialized successfully")
        
        logger.debug("Initializing ScriptRunner") 
        script_runner = ScriptRunner()
        logger.debug("ScriptRunner initialized successfully")
        
        logger.debug("Initializing FeedbackLoopChecker")
        feedback_checker = FeedbackLoopChecker()
        logger.debug("FeedbackLoopChecker initialized successfully")
        
        logger.debug("Initializing RetryMechanism")
        retry_mechanism = RetryMechanism()
        logger.debug("RetryMechanism initialized successfully")
        
        logger.debug("Initializing NotificationManager")
        notification_manager = NotificationManager()
        logger.debug("NotificationManager initialized successfully")
        
        logger.info("All components initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize components: {str(e)}", exc_info=True)
        raise SystemExit(f"System initialization failed: {str(e)}")



    # ==========================================================
    # ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
    # 
    # タスクを分解する処理
    #
    # ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
    # ----------------------------------------------------------

    # === 最終的なタスクリスト ===
    # 1: Visual Studio Codeをインストールする
    # 2-1: index.htmlファイルを作成する
    # 2-2-1: styles.cssファイルを作成する
    # 2-2-2: CSSでヘッダーのスタイルを設定する
    # 2-2-3: CSSでメインコンテンツのレイアウトを設定する
    # 3: ローカルサーバーを起動する

    def task_generate(goal):                               
        """目標を受け取り、タスクリストを生成する関数"""
        logger.debug(f"Generating tasks for goal: {goal}")

        template_prompt_name = 'task_break_down'
        selected_prompt = prompt_manager.select_prompt(template_prompt_name)              # タスク分解用のプロンプトをプロンプトマネージャーから取得
        logger.debug(f"Selected prompt template: {template_prompt_name}")

        merged_prompt = prompt_manager.merge_prompt(template_prompt_name, selected_prompt, goal)             # 取得したプロンプトと目標を組み合わせる
        logger.debug(f"Generated merged prompt: {merged_prompt}")

        while True:                                                                    # リスト形式で結果が得られるまでループ
            logger.debug("Sending prompt to LLM")
            list_tasks = llm_interface.run(prompt=merged_prompt)                       # LLMにプロンプトを送信してタスクリストを取得
            logger.debug(f"Received response from LLM: {list_tasks}")
            
            if isinstance(list_tasks, list):                                          # 返却値がリスト形式かチェック
                logger.info("Response is in valid list format")                                  # リスト形式の場合はOKとログ出力
                break                                                                  # ループを抜ける
            else:                                                                      # リスト形式でない場合
                logger.warning("Response is not in list format, retrying")                        # エラーログを出力して再試行
        logger.info(f"Successfully generated {len(list_tasks)} tasks")
        logger.debug(f"Generated tasks: {list_tasks}")

        return list_tasks                                                             # 生成されたタスクリストを返却

    def check_task_pc_level(task):                                                    # タスクがPC操作レベルか確認する関数
        template_prompt_name = 'task_check_pc_level'
        logger.debug(f"Checking PC level for task: {task}")
        
        selected_prompt = prompt_manager.select_prompt(template_prompt_name)         # PC操作レベルチェック用のプロンプトを取得
        logger.debug(f"Selected prompt template: {template_prompt_name}")
        
        merged_prompt = prompt_manager.merge_prompt(template_prompt_name, selected_prompt, task)            # プロンプトとタスクを組み合わせる
        logger.debug(f"Generated merged prompt: {merged_prompt}")
        
        result_true_or_false = llm_interface.run(prompt=merged_prompt)               # LLMでタスクのレベルを判定
        logger.debug(f"LLM response for PC level check: {result_true_or_false}")
        
        if result_true_or_false:                                                     # PC操作レベルの場合
            logger.info(f"Task '{task}' is PC level")                               # OKログを出力
            return True                                                              # Trueを返却
        else:                                                                        # PC操作レベルでない場合
            logger.info(f"Task '{task}' is not PC level")                           # NGログを出力
            return False                                                             # Falseを返却
    
    def recursive_task_breakdown(task, task_id=""):                                  # タスクを再帰的に分解する関数
        logger.debug(f"Starting recursive breakdown for task '{task}' with ID '{task_id}'")
        
        if check_task_pc_level(task):                                               # タスクがPC操作レベルかチェック
            result = [(task_id, task)] if task_id else [(task,)]
            logger.debug(f"Task is PC level, returning: {result}")                      # PC操作レベルならそのまま返却（IDの有無で形式を変える）
            return result
        
        logger.info(f"Breaking down task '{task}' further...")                      # 分解開始ログを出力
        subtasks = task_generate(task)                                              # タスクをさらに小さなタスクに分解
        logger.debug(f"Generated subtasks: {subtasks}")
        
        final_tasks = []                                                            # 最終的なタスクリストを格納する配列を初期化
        
        for i, subtask in enumerate(subtasks, 1):                                   # 分解された各サブタスクに対してループ処理
            new_task_id = f"{task_id}-{i}" if task_id else str(i)                  # 新しいタスクIDを生成（階層構造を表現）
            logger.debug(f"Processing subtask {subtask} with new ID {new_task_id}")
            
            decomposed_tasks = recursive_task_breakdown(subtask, new_task_id)       # サブタスクを再帰的に分解
            logger.debug(f"Decomposed tasks for {new_task_id}: {decomposed_tasks}")
            
            final_tasks.extend(decomposed_tasks)                                    # 分解されたタスクを結果リストに追加
        
        logger.debug(f"Completed breakdown for '{task}', returning: {final_tasks}")
        return final_tasks                                                          # 完全に分解されたタスクリストを返却

    def format_task_list(tasks):                                                    # タスクリストを整形する関数
        logger.debug(f"Formatting task list: {tasks}")
        formatted_tasks = []                                                        # 整形後のタスクを格納するリストを初期化
        
        for task_info in tasks:                                                    # 各タスク情報に対してループ
            if len(task_info) == 2:                                                # タスクIDが付与されている場合
                task_id, task = task_info                                          # IDとタスク内容を分離
                formatted_task = f"{task_id}: {task}"                              # "ID: タスク内容"の形式で追加
            else:                                                                  # タスクIDがない場合
                formatted_task = f"{task_info[0]}"                                 # タスク内容のみ追加
            logger.debug(f"Formatted task: {formatted_task}")
            formatted_tasks.append(formatted_task)
        
        return formatted_tasks                                                     # 整形されたタスクリストを返却

    def process_tasks(final_goal):                                                 # メインの処理を実行する関数
        logger.info(f"Starting task processing for goal: {final_goal}")
        initial_tasks = task_generate(goal=final_goal)                            # 最終目標を初期タスクに分解
        logger.debug(f"Generated initial tasks: {initial_tasks}")
        
        final_task_list = []                                                      # 最終的なタスクリストを初期化
        
        for i, task in enumerate(initial_tasks, 1):                               # 各初期タスクに対してループ処理
            logger.debug(f"Processing initial task {i}: {task}")
            decomposed_tasks = recursive_task_breakdown(task, str(i))             # タスクを再帰的に分解
            logger.debug(f"Decomposed tasks for task {i}: {decomposed_tasks}")
            final_task_list.extend(decomposed_tasks)                              # 分解されたタスクを最終リストに追加
        
        formatted_tasks = format_task_list(final_task_list)                       # タスクリストを見やすく整形
        
        logger.info("=== Final Task List ===")                                    # 区切り線を出力
        for task in formatted_tasks:                                              # 各タスクを表示
            logger.info(task)                                                     # タスクを1行ずつ出力
        
        logger.debug(f"Returning final task list: {final_task_list}")
        return final_task_list                                                    # 最終的なタスクリストを返却                                                  # 最終的なタスクリストを返却

    # メイン実行部分
    final_task_list = process_tasks(final_goal)                                   # 最終目標を渡してタスク分解を実行

            

    # ==========================================================
    # ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
    # 
    # 分解した各タスクを実行していく処理
    #
    # ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
    # ----------------------------------------------------------

    def execute_single_task(task, task_id):                                            # 単一タスクの実行関数
        logger.info(f"Executing task {task_id}: {task}")

        # スクリーンショット取得
        try:
            logger.debug("Attempting to capture screenshot")
            screenshot_path = screenshot_capturer.capture_screen()
            logger.debug(f"Screenshot captured successfully: {screenshot_path}")
        except Exception as e:
            logger.error(f"Screenshot capture failed: {str(e)}", exc_info=True)
            return False                       

        # タスク実行方法の選択
        template_prompt_name = 'select_best_method_for_task_run'                       # プロンプト名を設定
        logger.debug(f"Selecting execution method using prompt: {template_prompt_name}")
        selected_prompt = prompt_manager.select_prompt(template_prompt_name)            # プロンプトを選択
        merged_prompt = prompt_manager.merge_prompt(                                    # プロンプトを結合
            template_prompt_name, selected_prompt, task
        )
        logger.debug(f"Merged prompt for execution method: {merged_prompt}")
        
        plan_for_task_run = llm_interface.run(prompt=merged_prompt, image_path=screenshot_path)
        logger.info(f"Selected execution method: {plan_for_task_run}")

        if plan_for_task_run == 'Python_file':                                         # Pythonファイルでの実行の場合
            logger.info("Executing task using Python file method")
            # Pythonスクリプトの生成と実行
            template_prompt_name = 'task_run_with_Python_file'                         # プロンプト名を設定
            selected_prompt = prompt_manager.select_prompt(template_prompt_name)        # プロンプトを選択
            merged_prompt = prompt_manager.merge_prompt(                                # プロンプトを結合
                template_prompt_name, selected_prompt, task
            )
            logger.debug(f"Merged prompt for Python script generation: {merged_prompt}")
            
            program_code_txt = llm_interface.run(prompt=merged_prompt, image_path=screenshot_path)
            logger.debug(f"Generated Python code: {program_code_txt}")

            # スクリプトの生成と保存
            logger.debug("Generating script from code")
            script = script_generator.generate_script(                                  # スクリプトを生成
                program_code_txt, script_type='python'
            )
            script_dir = os.path.join(ROOT_DIR, 'data', 'scripts', 'python')
            os.makedirs(script_dir, exist_ok=True)
            script_path = os.path.join(script_dir, f'generated_script_{task_id}.py')
            logger.debug(f"Saving script to: {script_path}")
            
            with open(script_path, 'w') as f:                                          # スクリプトを保存
                f.write(script)
                logger.debug("Script saved successfully")

            # スクリプト実行
            logger.info("Executing script with retry mechanism")
            execution_success = retry_mechanism.execute_with_retry(                     # スクリプトを実行
                script_runner.run_script, 
                script_path, 
                'python'
            )
            logger.debug(f"Script execution result: {execution_success}")

            if execution_success:                                                       # 実行成功の場合
                logger.debug("Script executed successfully, checking task progress")
                # タスクの進行状況を確認
                if feedback_checker.check_task_progress(screenshot_path, task):         # タスクの進行を確認
                    logger.info(f"Task {task_id} executed successfully")                # 成功ログを出力
                    return True                                                         # 成功を返却
            
            logger.warning(f"Task {task_id} execution failed")                         # 失敗ログを出力
            return False                                                               # 失敗を返却

        else:                                                                          # 他の実行方法の場合
            logger.error(f"Unsupported execution method: {plan_for_task_run}")         # エラーログを出力
            return False                                                               # 失敗を返却

    def execute_tasks(task_list, execution_status):                                    # タスク実行のメイン関数
        logger.info("Starting execution of task list")
        updated_task_list = task_list.copy()
        logger.debug(f"Initial task list: {updated_task_list}")
        i = 0

        while i < len(updated_task_list):
            task_id, task = updated_task_list[i]
            logger.info(f"Processing task {task_id}: {task}")

            execution_status.initialize_task(task_id)
            logger.debug(f"Initialized status for task {task_id}")

            while True:
                try:
                    logger.debug(f"Attempting to execute task {task_id}")
                    success = execute_single_task(task, task_id)
                    logger.debug(f"Execution result for task {task_id}: {success}")
                    
                    if success:
                        execution_status.update_status(task_id, "completed")
                        logger.info(f"Task {task_id} completed successfully")
                        i += 1
                        break
                    
                    if not execution_status.increment_retry(task_id):
                        logger.warning(f"Max retries exceeded for task {task_id}")
                        logger.debug("Breaking down task into subtasks")
                        new_subtasks = recursive_task_breakdown(task, task_id)
                        logger.debug(f"Generated new subtasks: {new_subtasks}")
                        
                        updated_task_list.pop(i)
                        for j, new_task in enumerate(new_subtasks):
                            updated_task_list.insert(i + j, new_task)
                        logger.info(f"Updated task list with new subtasks")
                        
                        break

                except Exception as e:
                    logger.error(f"Error executing task {task_id}: {str(e)}", exc_info=True)
                    execution_status.update_status(task_id, "failed")
                    logger.debug(f"Updated task {task_id} status to failed")
                    
                    if not execution_status.increment_retry(task_id):
                        logger.warning(f"Max retries exceeded for task {task_id}, sending notification")
                        notification_manager.send_notification(
                            recipient_email=config['notification_recipient_email'],
                            subject=f'Task {task_id} Failure',
                            message=f'Task {task_id} failed after maximum retries: {str(e)}'
                        )
                        logger.debug("Notification sent for task failure")
                        i += 1
                        break

        logger.debug(f"Final updated task list: {updated_task_list}")
        return updated_task_list

    execution_status = TaskExecutionStatus()
    
    try:
        updated_task_list = execute_tasks(final_task_list, execution_status)
        
        successful_tasks = execution_status.successful_tasks_count
        total_tasks = len(final_task_list)
        
        logger.info(
            f"Execution completed. "
            f"{successful_tasks}/{total_tasks} tasks successful "
            f"({(successful_tasks/total_tasks)*100:.1f}%)"
        )
        
    except Exception as e:
        logger.error(f"Execution failed: {str(e)}")
        notification_manager.send_notification(
            recipient_email=config['notification_recipient_email'],
            subject='Task Execution Failed',
            message=f'The task execution has failed: {str(e)}'
        )
        raise






if __name__ == '__main__':
    main()



