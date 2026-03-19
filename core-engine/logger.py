"""
Sistema de logging do AgentMoney.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from colorama import init, Fore, Style

# Inicializa colorama
init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    """Formatter com cores para terminal."""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA + Style.BRIGHT
    }
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, '')
        reset = Style.RESET_ALL
        record.levelname = f"{color}[{record.levelname}]{reset}"
        return super().format(record)


def get_logger(name: str = "AgentMoney", log_file: bool = True):
    """
    Cria e configura um logger.
    
    Args:
        name: Nome do logger
        log_file: Se True, salva logs em arquivo
        
    Returns:
        Logger configurado
    """
    from .config import Config
    Config.ensure_directories()
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    # Evita handlers duplicados
    if logger.handlers:
        return logger
    
    # Handler para console (colorido)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_format = ColoredFormatter(
        '%(levelname)s %(asctime)s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # Handler para arquivo
    if log_file:
        log_path = Config.LOGS_DIR / f"agentmoney_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger
