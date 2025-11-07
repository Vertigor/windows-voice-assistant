"""
日志管理模块
"""

import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime


class Logger:
    """日志管理器"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        
        # 日志目录
        self.log_dir = Path(os.getenv('APPDATA')) / 'VoiceAssistant' / 'logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 日志文件
        self.log_file = self.log_dir / f'voice_assistant_{datetime.now().strftime("%Y%m%d")}.log'
        
        # 配置根日志记录器
        self.logger = logging.getLogger('VoiceAssistant')
        self.logger.setLevel(logging.DEBUG)
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            # 文件处理器（自动轮转）
            file_handler = RotatingFileHandler(
                self.log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            
            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter(
                '%(levelname)s: %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            
            # 添加处理器
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def get_logger(self, name: str = None) -> logging.Logger:
        """获取日志记录器"""
        if name:
            return logging.getLogger(f'VoiceAssistant.{name}')
        return self.logger
    
    def set_level(self, level: str):
        """设置日志级别"""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        self.logger.setLevel(level_map.get(level.upper(), logging.INFO))


# 全局日志实例
_logger_instance = Logger()


def get_logger(name: str = None) -> logging.Logger:
    """获取日志记录器"""
    return _logger_instance.get_logger(name)
