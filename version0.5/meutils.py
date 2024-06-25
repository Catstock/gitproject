import os
from functools import wraps

def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_message = f'Error in {func.__name__}: {e}\n'
            print(error_message)
            # 在这里可以执行其他的异常处理逻辑

            # 检查日志文件是否存在，如果不存在则创建它
            if not os.path.exists('log.txt'):
                with open('log.txt', 'w'):
                    pass
            # 写入异常信息到日志文件
            with open('log.txt', 'a') as f:
                f.write(error_message)
    return wrapper