import time
from datetime import datetime
from colorama import Fore, Style, init
from threading import Lock

init()

class NovaLogger:
    _lock = Lock()
    _log_file = None
    _debug_mode = False

    
    _SYMBOLS = {
        'note': '[◈]',   
        'event': '[▷]',  
        'alert': '[△]',  
        'fail': '[⨯]',   
        'win': '[✓]',    
        'trace': '[◎]'   
    }
    _COLORS = {
        'timestamp': Fore.LIGHTBLACK_EX,
        'note': Fore.LIGHTCYAN_EX,  
        'event': Fore.LIGHTMAGENTA_EX,  
        'alert': Fore.LIGHTYELLOW_EX,  
        'fail': Fore.LIGHTRED_EX,  
        'win': Fore.LIGHTGREEN_EX,  
        'trace': Fore.WHITE
    }

    @classmethod
    def config(cls, debug=False, log_file=None):
        cls._debug_mode = debug
        if log_file:
            cls._log_file = open(log_file, 'a', encoding='utf-8')

    @classmethod
    def close(cls):
        with cls._lock:
            if cls._log_file:
                cls._log_file.close()
                cls._log_file = None

    @classmethod
    def _write(cls, message):
        """Thread-safe logging"""
        with cls._lock:
            if cls._log_file:
                
                clean_message = cls._strip_colors(message)
                cls._log_file.write(clean_message + '\n')
                cls._log_file.flush()
            print(message + Style.RESET_ALL)

    @classmethod
    def _strip_colors(cls, message):
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', message)

    @classmethod
    def _format(cls, level, message, **ctx):
        timestamp = datetime.now().strftime("%H:%M:%S")
        base = (
            f"{cls._COLORS['timestamp']}[{timestamp}] "
            f"{cls._COLORS[level]}{cls._SYMBOLS[level]} "
            f"{cls._COLORS[level]}{message}"  
        )
        if ctx:
            
            details = " ".join(f"{k}={v}" for k, v in ctx.items())
            base += f" {Fore.LIGHTBLACK_EX}▸ {details}"
        return base

    @classmethod
    def note(cls, message, **ctx):
        cls._write(cls._format('note', message, **ctx))

    @classmethod
    def event(cls, message, **ctx):
        cls._write(cls._format('event', message, **ctx))

    @classmethod
    def alert(cls, message, **ctx):
        cls._write(cls._format('alert', message, **ctx))

    @classmethod
    def fail(cls, message, **ctx):
        cls._write(cls._format('fail', message, **ctx))

    @classmethod
    def win(cls, message, **ctx):
        cls._write(cls._format('win', message, **ctx))

    @classmethod
    def trace(cls, message, **ctx):
        if cls._debug_mode:
            cls._write(cls._format('trace', message, **ctx))
