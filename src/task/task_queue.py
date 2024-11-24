
# task_queue.py
import queue

class TaskQueueManager:
    def __init__(self):
        self.task_queue = queue.Queue()
        self.processing_tasks = set()

    def add_task(self, task):
        self.task_queue.put(task)

    def get_next_task(self):
        if not self.task_queue.empty():
            task = self.task_queue.get()
            self.processing_tasks.add(task['id'])
            return task
        return None

    def mark_completed(self, task_id):
        if task_id in self.processing_tasks:
            self.processing_tasks.remove(task_id)

    def is_empty(self):
        return self.task_queue.empty() and not self.processing_tasks