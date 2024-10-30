import queue

class TaskQueueManager:
    def __init__(self):
        self.task_queue = queue.Queue()

    def add_task(self, task):
        """新しいタスクをキューに追加"""
        self.task_queue.put(task)

    def get_next_task(self):
        """次のタスクを取得して返す"""
        if not self.task_queue.empty():
            return self.task_queue.get()
        return None

    def is_empty(self):
        """キューが空かどうかを確認"""
        return self.task_queue.empty()

