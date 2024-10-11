import logging

def setup_logger(log_file='logs/execution.log'):
    """システム全体のログ管理を行うロガーをセットアップ"""
    logger = logging.getLogger('PC_Auto_Operation_System')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

