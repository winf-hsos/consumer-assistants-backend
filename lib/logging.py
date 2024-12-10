import inspect
from datetime import datetime
from colorama import Fore, Style, init
init()

from lib.config import configure
LOGFILE = configure("logging.log_file")
PRINT_LOG = configure("logging.print_log")
LOG_LEVEL = configure("logging.log_level")

DEBUG = 4
INFO = 3
WARNING = 2
ERROR = 1

def log_error(text, prompt="NA"):
    log(ERROR, text, prompt)

def log_warning(text, prompt="NA"):
    log(WARNING, text, prompt)

def log_info(text, prompt="NA"):
    log(INFO, text, prompt)

def log_debug(text, prompt="NA"):  
    log(DEBUG, text, prompt)

def log(level, text, prompt="NA"):

    if LOG_LEVEL < level:
        return
    
    frame = inspect.currentframe()
    caller_frame = frame.f_back.f_back
    filename = caller_frame.f_code.co_filename
    function_name = caller_frame.f_code.co_name
    line_number = caller_frame.f_lineno
    source = f"[{filename}:{function_name}:{line_number}]"

    # Get current timestamp in ISO format
    timestamp = datetime.now().isoformat()
    # Open the log file in append mode
    
    log_entry = f'{timestamp} - {source} - {level}: {text} | {prompt}'

    if PRINT_LOG:
        if(level == ERROR):
            print(Fore.RED + log_entry + Style.RESET_ALL)
        elif(level == WARNING):
            print(Fore.YELLOW + log_entry + Style.RESET_ALL)
        elif(level == INFO):
            print(Fore.GREEN + log_entry + Style.RESET_ALL)
        elif(level == DEBUG):
            print(Fore.CYAN  + log_entry + Style.RESET_ALL)

    with open(LOGFILE, 'a', encoding="utf-8") as file:
        # Write the log entry to the file
        file.write(log_entry + '\n')

def reset_log():
    with open(LOGFILE, "w", encoding="utf-8") as file:
        file.write("")