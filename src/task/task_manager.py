# task_manager.py
from src.llm.interface import LLMInterface
from src.task.task_status import TaskExecutionStatus
from src.task.task_queue import TaskQueueManager
from src.prompt.prompt_manager import PromptManager
import logging

class TaskManager:
    def __init__(self):
        self.logger = logging.getLogger('PC_Auto_Operation_System')
        self.task_status = TaskExecutionStatus()
        self.task_queue = TaskQueueManager()
        self.prompt_manager = PromptManager()
        self.llm_interface = LLMInterface()

    def create_task(self, task_description):
        task_id = len(self.task_status.status) + 1
        task = {
            'id': task_id,
            'description': task_description
        }
        self.task_status.initialize_task(task_id)
        self.task_queue.add_task(task)
        return task_id

    def process_next_task(self):
        task = self.task_queue.get_next_task()
        if task:
            success = self._execute_task(task)
            if success:
                self.task_status.update_status(task['id'], "completed")
                self.task_queue.mark_completed(task['id'])
            return success
        return None

    def _execute_task(self, task):
        try:
            prompt = self.prompt_manager.select_prompt("task_execution")
            result = self.llm_interface.run(prompt=prompt)
            return result.get('success', False)
        except Exception as e:
            self.logger.error(f"Task execution failed: {str(e)}")
            return False