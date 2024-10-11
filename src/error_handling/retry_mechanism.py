class RetryMechanism:
    def __init__(self, max_retries=5):
        self.max_retries = max_retries

    def execute_with_retry(self, func, *args, **kwargs):
        """指定された関数を最大リトライ回数まで実行し、成功するか確認"""
        attempt = 0
        while attempt < self.max_retries:
            try:
                result = func(*args, **kwargs)
                if result:
                    return True  # 成功した場合
            except Exception as e:
                print(f"Attempt {attempt + 1} failed with error: {e}")
            attempt += 1
        return False  # リトライ回数を超えた場合
