import zmq
import json
from datetime import datetime
import inspect
import threading
import queue
import time  # 添加时间模块，用于记录时间

log_queue = queue.Queue()

log_thread = None
log_thread_started = False

def start_log_thread():
    global log_thread, log_thread_started
    if not log_thread_started:
        log_thread = threading.Thread(target=log_worker)
        log_thread.daemon = True
        log_thread.start()
        log_thread_started = True

def log_worker():
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.connect("tcp://localhost:5555")
    while True:
        try:
            if log_queue.empty():
                time.sleep(0.001)  # 如果队列为空，等待一段时间再检查
                continue
            message = log_queue.get(timeout=1)  # 设置超时时间
            if message is None:
                continue  # 如果获取到 None，继续循环
            socket.send_string(message)
            log_queue.task_done()
        except queue.Empty:
            continue  # 如果队列为空，继续循环
    socket.close()
    context.term()

class logger:
    @staticmethod
    def _log(sender,level, message):
        if not log_thread_started:
            start_log_thread()
        now = datetime.now()
        ts = now.strftime("%Y-%m-%d %H:%M:%S") + ".{:03}".format(now.microsecond // 1000)
        message = json.dumps({"ts": ts, "cmd": level, "log_name": sender, "log_content": message})
        log_queue.put(message)

    @staticmethod
    def info(message):
        caller_frame = inspect.currentframe().f_back                
        sender = caller_frame.f_code.co_filename.split('\\')[-1]
        sender += f"[{caller_frame.f_code.co_firstlineno}] " + caller_frame.f_code.co_name + ': '           
        logger._log(sender,"INFO", message)

    @staticmethod
    def debug(message):
        caller_frame = inspect.currentframe().f_back                
        sender = caller_frame.f_code.co_filename.split('\\')[-1]
        sender += f"[{caller_frame.f_code.co_firstlineno}] " + caller_frame.f_code.co_name + ': '    
        logger._log(sender,"DEBUG", message)

    @staticmethod
    def error(message):
        caller_frame = inspect.currentframe().f_back                
        sender = caller_frame.f_code.co_filename.split('\\')[-1]
        sender += f"[{caller_frame.f_code.co_firstlineno}] " + caller_frame.f_code.co_name + ': '    
        logger._log(sender,"ERROR", message)

    @staticmethod
    def warning(message):
        caller_frame = inspect.currentframe().f_back                
        sender = caller_frame.f_code.co_filename.split('\\')[-1]
        sender += f"[{caller_frame.f_code.co_firstlineno}] " + caller_frame.f_code.co_name + ': '    
        logger._log(sender,"WARNING", message)

    @staticmethod
    def critical(message):
        caller_frame = inspect.currentframe().f_back                
        sender = caller_frame.f_code.co_filename.split('\\')[-1]
        sender += f"[{caller_frame.f_code.co_firstlineno}] " + caller_frame.f_code.co_name + ': '    
        logger._log(sender,"CRITICAL", message)

    @staticmethod
    def show(target, data):
        caller_frame = inspect.currentframe().f_back                
        sender = caller_frame.f_code.co_filename.split('\\')[-1]
        sender += f"[{caller_frame.f_code.co_firstlineno}] " + caller_frame.f_code.co_name + ': '    
        logger._log(sender,"SHOW", {"target": target, "data": data})

def main():    
    logger.info("This is an info message.")
    logger.error("This is an error message.")

def test_log_performance():

    logger.info("Starting performance test.")
    start_time = time.time()
    times = []

    for i in range(10):
        start = time.time()
        logger.info(f"Test log message.{i}")
        end = time.time()
        times.append(end - start)

    end_time = time.time()
    total_time = end_time - start_time
    average_time = total_time / 10
    max_time = max(times)

    print(f"Total time: {total_time:.6f} seconds")
    print(f"Average time: {average_time:.6f} seconds")
    print(f"Max time: {max_time:.6f} seconds")

    print("show test")
    logger.show("test_target", "testdata")

if __name__ == "__main__":
    main()
    test_log_performance()  # 添加测试函数调用

    time.sleep(5)

