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
            message = log_queue.get(timeout=1)  # 设置超时时间
            if message is None:
                continue  # 如果获取到 None，继续循环
            socket.send_string(message)
            log_queue.task_done()
        except queue.Empty:
            continue  # 如果队列为空，继续循环
    socket.close()
    context.term()

class loger:
    @staticmethod
    def _log(level, message):
        if not log_thread_started:
            start_log_thread()
        caller_frame = inspect.currentframe().f_back                
        sender = caller_frame.f_code.co_filename.split('\\')[-1]
        sender += "." + caller_frame.f_code.co_name + ': '
        now = datetime.now()
        ts = now.strftime("%Y-%m-%d %H:%M:%S") + ".{:03}".format(now.microsecond // 1000)
        message = json.dumps({"ts": ts, "cmd": level, "log_name": sender, "log_content": message})
        log_queue.put(message)

    @staticmethod
    def info(message):
        loger._log("INFO", message)

    @staticmethod
    def debug(message):
        loger._log("DEBUG", message)

    @staticmethod
    def error(message):
        loger._log("ERROR", message)

    @staticmethod
    def warning(message):
        loger._log("WARNING", message)

    @staticmethod
    def critical(message):
        loger._log("CRITICAL", message)

def main():    
    loger.info("This is an info message.")
    loger.error("This is an error message.")

def test_log_performance():

    loger.info("Starting performance test.")
    start_time = time.time()
    times = []

    for i in range(1000):
        start = time.time()
        loger.info(f"Test log message.{i}")
        end = time.time()
        times.append(end - start)

    end_time = time.time()
    total_time = end_time - start_time
    average_time = total_time / 1000
    max_time = max(times)

    print(f"Total time: {total_time:.6f} seconds")
    print(f"Average time: {average_time:.6f} seconds")
    print(f"Max time: {max_time:.6f} seconds")

if __name__ == "__main__":
    main()
    #test_log_performance()  # 添加测试函数调用

