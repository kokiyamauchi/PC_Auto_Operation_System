class TaskExecutionStatus:
    def __init__(self):
        self.status = {}
        self.max_retries = 3
        self.current_retries = {}

    def initialize_task(self, task_id):
        self.status[task_id] = "pending"
        self.current_retries[task_id] = 0

    def update_status(self, task_id, status):
        self.status[task_id] = status

    def increment_retry(self, task_id):
        self.current_retries[task_id] = self.current_retries.get(task_id, 0) + 1
        return self.current_retries[task_id] <= self.max_retries

    @property
    def successful_tasks_count(self):
        return sum(1 for status in self.status.values() 
                  if status == "completed")

    def get_task_status(self, task_id):
        return self.status.get(task_id, "unknown")

    def get_retry_count(self, task_id):
        return self.current_retries.get(task_id, 0)