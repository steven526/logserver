# Log Server 使用说明

# Log Server and Log Client

## Overview

This repository contains two Python scripts: `logServer.py` and `logClient.py`. The `logServer.py` script acts as a log server that receives log messages over a ZMQ PULL/PUSH protocol and logs them to both the terminal and a file. The `logClient.py` script sends log messages to the log server.

## Components

### logServer.py

#### Functionality

- **ZMQ PULL/PUSH Protocol**: Uses ZMQ to receive log messages.
- **Loguru for Logging**: Logs messages to both the terminal and a file.
- **Configuration Management**: Reads configuration from `setting.yaml` and reloads it periodically.
- **Command Handling**: Supports commands to restart (`R`), quit (`Q`), and clear the log file (`CLEAR`).

#### Configuration

The `setting.yaml` file should be located in the same directory as `logServer.py` and should have the following structure:

```yaml
logServer:
  logpath: ./logs/
  showlevel: INFO
  recordlevel: DEBUG
  filename: server_log
  port: 5555
```
- logpath: Directory where log files will be stored.
- showlevel: Minimum log level for terminal output (e.g., INFO, WARNING, ERROR, DEBUG).
- recordlevel: Minimum log level for file recording (e.g., INFO, WARNING, ERROR, DEBUG).
- filename: Base name for log files.
- port: Port number for ZMQ communication.
  python logServer.py


## Usage
1. Send Log Messages:

bash
---
```bash
python logClient.py
```
The script will send a series of test log messages to the log server.

 ```log 
2024-12-31 13:35:39.417 | WARNING  | __main__:handle_log_message:71 - H2024-12-31 13:35:39 TestLogger: This is a warning message. 
2024-12-31 13:35:39.423 | ERROR    | __main__:handle_log_message:73 - H2024-12-31 13:35:39 TestLogger: This is an error message. 
2024-12-31 13:35:39.617 | WARNING  | __main__:handle_log_message:71 - H2024-12-31 13:35:39 TestLogger: This is a warning message. 
2024-12-31 13:35:39.621 | ERROR    | __main__:handle_log_message:73 - H2024-12-31 13:35:39 TestLogger: This is an error message. 
clear
2024-12-31 13:35:53.316 | ERROR    | __main__:clear_log_file:138 - Failed to clear log file: name 'log_filename' is not defined
2024-12-31 13:36:16.098 | WARNING  | __main__:handle_log_message:71 - H2024-12-31 13:36:16 TestLogger: This is a warning message. 
2024-12-31 13:36:16.103 | ERROR    | __main__:handle_log_message:73 - H2024-12-31 13:36:16 TestLogger: This is an error message. 