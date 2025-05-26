import threading
import time

def repeat_every(interval):
    def decorator(func):
        def wrapper(*args, **kwargs):
            def loop():
                while True:
                    func(*args, **kwargs)
                    time.sleep(interval)
            t = threading.Thread(target=loop, daemon=True)
            t.start()
        return wrapper
    return decorator