import os
from src.screenshot.capture import ScreenshotCapture
from src.llm.interface import LLMInterface
from src.llm.script_generator import ScriptGenerator
from src.execution.runner import ScriptRunner
from src.feedback_loop.checker import FeedbackLoopChecker
from src.task.task_manager import TaskManager
from src.task.task_status import TaskExecutionStatus
from src.prompt.prompt_manager import PromptManager
from src.error_handling.retry_mechanism import RetryMechanism
from src.error_handling.notification import NotificationManager
from src.utils.logger import setup_logger

import yaml

def load_config(file_path='config/settings.yaml'):
    """設定ファイルを読み込む関数"""
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# ロガーのセットアップ
logger = setup_logger()

def main():
    # 設定の読み込み
    config = load_config()
    final_goal = config['goal']

    try:
        # 初期化
        task_manager = TaskManager()                            # タスクを管理するクラス
        prompt_manager = PromptManager()                        # プロンプトを管理するクラス
        screenshot_capturer = ScreenshotCapture()               # スクリーンショットを取ってパスを返すクラス
        llm_interface = LLMInterface()                          # LLMとやり取りするクラス
        script_generator = ScriptGenerator()                    # LLMから結果を受け取りスクリプトファイルを生成するクラス                
        script_runner = ScriptRunner()                          # 生成したファイルを実行するクラス
        feedback_checker = FeedbackLoopChecker()                # タスクが完了したか確認するクラス
        retry_mechanism = RetryMechanism()                      # タスク実行のリトライを管理するクラス
        notification_manager = NotificationManager()            # 通知を管理するクラス
    except Exception as e:
        logger.error(f"Failed to initialize components: {str(e)}")
        raise SystemExit("System initialization failed")



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

    def task_generate(goal):                                                           # 目標を受け取り、タスクリストを生成する関数
        template_prompt_name = 'task_break_down'
        selected_prompt = prompt_manager.select_prompt(template_prompt_name)              # タスク分解用のプロンプトをプロンプトマネージャーから取得
        merged_prompt = prompt_manager.merge_prompt(template_prompt_name, selected_prompt, goal)             # 取得したプロンプトと目標を組み合わせる

        while True:                                                                    # リスト形式で結果が得られるまでループ
            list_tasks = llm_interface.run(prompt=merged_prompt)                       # LLMにプロンプトを送信してタスクリストを取得
            if isinstance(list_tasks, list):                                          # 返却値がリスト形式かチェック
                print("list_tasksはリスト形式です。")                                  # リスト形式の場合はOKとログ出力
                break                                                                  # ループを抜ける
            else:                                                                      # リスト形式でない場合
                print("list_tasksはリスト形式ではありません。")                        # エラーログを出力して再試行

        return list_tasks                                                             # 生成されたタスクリストを返却

    def check_task_pc_level(task):                                                    # タスクがPC操作レベルか確認する関数
        template_prompt_name = 'task_check_pc_level'
        selected_prompt = prompt_manager.select_prompt(template_prompt_name)         # PC操作レベルチェック用のプロンプトを取得
        merged_prompt = prompt_manager.merge_prompt(template_prompt_name, selected_prompt, task)            # プロンプトとタスクを組み合わせる
        result_true_or_false = llm_interface.run(prompt=merged_prompt)               # LLMでタスクのレベルを判定
        
        if result_true_or_false:                                                     # PC操作レベルの場合
            print(f"タスク '{task}' はPC操作レベルです。")                           # OKログを出力
            return True                                                              # Trueを返却
        else:                                                                        # PC操作レベルでない場合
            print(f"タスク '{task}' はPC操作レベルではありません。")                 # NGログを出力
            return False                                                             # Falseを返却

    def recursive_task_breakdown(task, task_id=""):                                  # タスクを再帰的に分解する関数
        if check_task_pc_level(task):                                               # タスクがPC操作レベルかチェック
            return [(task_id, task)] if task_id else [(task,)]                      # PC操作レベルならそのまま返却（IDの有無で形式を変える）
        
        print(f"タスク '{task}' を更に分解します...")                                # 分解開始ログを出力
        subtasks = task_generate(task)                                              # タスクをさらに小さなタスクに分解
        
        final_tasks = []                                                            # 最終的なタスクリストを格納する配列を初期化
        
        for i, subtask in enumerate(subtasks, 1):                                   # 分解された各サブタスクに対してループ処理
            new_task_id = f"{task_id}-{i}" if task_id else str(i)                  # 新しいタスクIDを生成（階層構造を表現）
            decomposed_tasks = recursive_task_breakdown(subtask, new_task_id)       # サブタスクを再帰的に分解
            final_tasks.extend(decomposed_tasks)                                    # 分解されたタスクを結果リストに追加
        
        return final_tasks                                                          # 完全に分解されたタスクリストを返却

    def format_task_list(tasks):                                                    # タスクリストを整形する関数
        formatted_tasks = []                                                        # 整形後のタスクを格納するリストを初期化
        for task_info in tasks:                                                    # 各タスク情報に対してループ
            if len(task_info) == 2:                                                # タスクIDが付与されている場合
                task_id, task = task_info                                          # IDとタスク内容を分離
                formatted_tasks.append(f"{task_id}: {task}")                       # "ID: タスク内容"の形式で追加
            else:                                                                  # タスクIDがない場合
                formatted_tasks.append(f"{task_info[0]}")                          # タスク内容のみ追加
        return formatted_tasks                                                     # 整形されたタスクリストを返却

    def process_tasks(final_goal):                                                 # メインの処理を実行する関数
        initial_tasks = task_generate(goal=final_goal)                            # 最終目標を初期タスクに分解
        
        final_task_list = []                                                      # 最終的なタスクリストを初期化
        
        for i, task in enumerate(initial_tasks, 1):                               # 各初期タスクに対してループ処理
            decomposed_tasks = recursive_task_breakdown(task, str(i))             # タスクを再帰的に分解
            final_task_list.extend(decomposed_tasks)                              # 分解されたタスクを最終リストに追加
        
        formatted_tasks = format_task_list(final_task_list)                       # タスクリストを見やすく整形
        
        print("\n=== 最終的なタスクリスト ===")                                    # 区切り線を出力
        for task in formatted_tasks:                                              # 各タスクを表示
            print(task)                                                           # タスクを1行ずつ出力
        
        return final_task_list                                                    # 最終的なタスクリストを返却

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
        # スクリーンショット取得
        try:
            screenshot_path = screenshot_capturer.capture_screen()
        except Exception as e:
            logger.error(f"Screenshot capture failed: {str(e)}")
            return False                       

        # タスク実行方法の選択
        template_prompt_name = 'select_best_method_for_task_run'                       # プロンプト名を設定
        selected_prompt = prompt_manager.select_prompt(template_prompt_name)            # プロンプトを選択
        merged_prompt = prompt_manager.merge_prompt(                                    # プロンプトを結合
            template_prompt_name, selected_prompt, task
        )
        plan_for_task_run = llm_interface.run_with_screenshot(                         # 実行方法を決定
            screenshot_path, prompt=merged_prompt
        )

        if plan_for_task_run == 'Python_file':                                         # Pythonファイルでの実行の場合
            # Pythonスクリプトの生成と実行
            template_prompt_name = 'task_run_with_Python_file'                         # プロンプト名を設定
            selected_prompt = prompt_manager.select_prompt(template_prompt_name)        # プロンプトを選択
            merged_prompt = prompt_manager.merge_prompt(                                # プロンプトを結合
                template_prompt_name, selected_prompt, task
            )
            program_code_txt = llm_interface.run_with_screenshot(                       # コードを生成
                screenshot_path, prompt=merged_prompt
            )

            # スクリプトの生成と保存
            script = script_generator.generate_script(                                  # スクリプトを生成
                program_code_txt, script_type='python'
            )
            script_path = os.path.join(                                                # スクリプトのパスを設定
                'data/scripts/python/', 
                f'generated_script_{task_id}.py'
            )
            with open(script_path, 'w') as f:                                          # スクリプトを保存
                f.write(script)

            # スクリプト実行
            execution_success = retry_mechanism.execute_with_retry(                     # スクリプトを実行
                script_runner.run_script, 
                script_path, 
                'python'
            )

            if execution_success:                                                       # 実行成功の場合
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
        updated_task_list = task_list.copy()
        i = 0

        while i < len(updated_task_list):
            task_id, task = updated_task_list[i]
            logger.info(f"Processing task {task_id}: {task}")

            execution_status.initialize_task(task_id)

            while True:
                try:
                    success = execute_single_task(task, task_id)
                    
                    if success:
                        execution_status.update_status(task_id, "completed")
                        i += 1
                        break
                    
                    if not execution_status.increment_retry(task_id):
                        logger.warning(f"Max retries exceeded for task {task_id}")
                        new_subtasks = recursive_task_breakdown(task, task_id)
                        
                        updated_task_list.pop(i)
                        for j, new_task in enumerate(new_subtasks):
                            updated_task_list.insert(i + j, new_task)
                        
                        break

                except Exception as e:
                    logger.error(f"Error executing task {task_id}: {str(e)}")
                    execution_status.update_status(task_id, "failed")
                    
                    if not execution_status.increment_retry(task_id):
                        notification_manager.send_notification(
                            recipient_email=config['notification_recipient_email'],
                            subject=f'Task {task_id} Failure',
                            message=f'Task {task_id} failed after maximum retries: {str(e)}'
                        )
                        i += 1
                        break

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











    # # タスクを取得し処理開始
    # for task in final_task_list:
    #     logger.info(f"Processing task: {task}")

    #     # タスクを実行する最適な方法を模索
    #     template_prompt_name = 'select_best_method_for_task_run'
    #     selected_prompt = prompt_manager.select_prompt(template_prompt_name)
    #     merged_prompt = prompt_manager.merge_prompt(template_prompt_name, selected_prompt, task)
    #     plan_for_task_run = llm_interface.run_with_screenshot(screenshot_path, prompt=merged_prompt)

    #     # スクリーンショット取得
    #     screenshot_path = screenshot_capturer.capture_screen()

    #     if plan_for_task_run == 'Python_file':

    #         template_prompt_name = 'task_run_with_Python_file'
    #         selected_prompt = prompt_manager.select_prompt(template_prompt_name)
    #         merged_prompt = prompt_manager.merge_prompt(template_prompt_name, selected_prompt, task)
    #         program_code_txt = llm_interface.run_with_screenshot(screenshot_path, prompt=merged_prompt)

    #         # スクリプトの生成と実行
    #         script = script_generator.generate_script(program_code_txt, script_type='python')
    #         script_path = os.path.join('data/scripts/python/', 'generated_script.py')
    #         with open(script_path, 'w') as f:
    #             f.write(script)

    #         # スクリプト実行と進行状況チェック
    #         if retry_mechanism.execute_with_retry(script_runner.run_script, script_path, 'python'):
    #             logger.info("Task executed successfully.")
    #         else:
    #             logger.error("Task failed after maximum retries.")
    #             notification_manager.send_notification(
    #                 recipient_email=config['notification_recipient_email'],
    #                 subject='Task Failure Notification',
    #                 message='The task has failed after multiple attempts.'
    #             )

    #         # フィードバックループで進行状況確認
    #         if not feedback_checker.check_task_progress(screenshot_path, task):
    #             logger.info("Task needs re-execution.")
    #             # taskを再度実行する