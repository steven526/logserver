'''
logServer : 日志服务器

功能框架
    使用 ZMQ PULL/PUSH 模式 作为通信协议 
    使用 logunu 作为日志记录

    根据 setting.yaml 文件配置日志记录
    主要目的把记录文件的和终端显示的分流并分级别

    logunu 进行日志文件记录时, 末尾添加 本地时间戳
'''


import asyncio
import zmq
from loguru import logger
from datetime import datetime
import platform
import json 
import yaml  # 添加 yaml 模块导入
import os
import sys

# 获取文件所在目录
import os
root = os.path.dirname(os.path.abspath(__file__))
setting_file_path = root + "\\setting.yaml"
# 读取 setting.yaml 文件
with open(setting_file_path, "r") as f:
    config = yaml.safe_load(f)

logpath = config['logServer']['logpath']
showlevel = config['logServer']['showlevel']
recordlevel = config['logServer']['recordlevel']
filename = config['logServer']['filename']  # 获取文件名配置
port = config['logServer']['port']

log_filename = None
# 记录配置文件的修改时间戳
config_mod_time = os.path.getmtime(setting_file_path)

# 配置 loguru 记录器
def configure_logger():
    global log_filename 
    logger.remove()  # 删除现有记录器
    logger.add(lambda msg: print(msg, end=''), level=showlevel, colorize=True,format="{time} {level} {message}")
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_filename = f"{logpath}{filename}_{current_date}.log"
    logger.add(log_filename, format="{time} {level} {message}", rotation="00:00", level=recordlevel)

configure_logger()

def handle_log_message(message):
    try:
        # 解析 JSON 格式的命令
        data = json.loads(message)
        ts = data.get('ts')
        cmd = data.get('cmd')
        log_name = data.get('log_name')
        log_content = data.get('log_content')
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON format: {message}")
        return
 
    # 根据 cmd 处理不同的日志级别
    if cmd == "INFO":
        logger.info(f"H {ts} {log_name}: {log_content} ")
    elif cmd == "WARNING":
        logger.warning(f"H {ts} {log_name}: {log_content} ")
    elif cmd == "ERROR":
        logger.error(f"H {ts} {log_name}: {log_content} ")
    elif cmd == "DEBUG":
        logger.debug(f"H {ts} {log_name}: {log_content} ")
    else:
        logger.error(f"H{ ts} {log_name}: Unknown command: {cmd}")


def reload_config():
    global logpath, showlevel, recordlevel, filename, logger, config_mod_time
    current_mod_time = os.path.getmtime(setting_file_path)
    if current_mod_time == config_mod_time:
        return 
    
    with open(root+"\\setting.yaml", "r") as f:
        config = yaml.safe_load(f)

    logpath = config['logServer']['logpath']
    showlevel = config['logServer']['showlevel']
    recordlevel = config['logServer']['recordlevel']
    filename = config['logServer']['filename']  # 获取文件名配置
    port = config['logServer']['port']  # 获取端口号配置

    # 重新配置 loguru 记录器
    configure_logger()
    # 更新配置文件的修改时间戳
    config_mod_time = current_mod_time

    
async def check_config_periodically():
    while True:
        reload_config()
        await asyncio.sleep(20)  # 

async def handle_input():
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    loop = asyncio.get_event_loop()
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    
    while True:
        data = await reader.readline()
        command = data.decode().strip().upper()
        if command == 'R':
            logger.info("Restarting logServer...")
            os.execv(sys.executable, ['python'] + sys.argv)
        elif command == 'Q':
            logger.info("Exiting logServer...")
            sys.exit(0)
        elif command == 'CLEAR':
            clear_log_file()
        else:
            logger.warning(f"Unknown command: {command}")

def clear_log_file():
    global log_filename
    try:
        # 删除现有日志文件
        if os.path.exists(log_filename):
            logger.remove()  # 关闭所有 loguru 记录器
            os.remove(log_filename)
            print(f"Log file {log_filename} cleared.")
        
        # 重新配置 loguru 记录器
        reload_config()
    except Exception as e:
        logger.error(f"Failed to clear log file: {e}")

async def handle_input_windows():
    while True:
        data = await asyncio.to_thread(sys.stdin.readline)
        command = data.strip().upper()
        if command == 'R':
            logger.info("Restarting logServer...")
            os.execv(sys.executable, ['python'] + sys.argv)
        elif command == 'Q':
            logger.info("Exiting logServer...")
            sys.exit(0)
        elif command == 'CLEAR':
            clear_log_file()
        else:
            logger.warning(f"Unknown command: {command}")

async def main():
    print(f"logServer is running on port {port}")
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.PULL)
    socket.bind(f"tcp://0.0.0.0:{port}")

    # 启动输入处理任务
    if platform.system() == 'Windows':
        asyncio.create_task(handle_input_windows())
    else:
        asyncio.create_task(handle_input())

    while True:
        message = await socket.recv_string()
        handle_log_message(message)

if __name__ == "__main__":
    # 设置正确的事件循环策略
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())
