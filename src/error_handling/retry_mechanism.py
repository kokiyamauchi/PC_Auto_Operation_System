class RetryMechanism:
    def __init__(self, max_retries=5):
        self.max_retries = max_retries

    def execute_with_retry(self, func, *args, **kwargs):
        """指定された関数を最大リトライ回数まで実行し、成功するか確認"""
        
        return 
