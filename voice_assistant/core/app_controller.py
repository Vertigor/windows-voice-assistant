"""
主应用控制器
负责协调各个模块，管理应用生命周期
"""

import threading
import queue
from typing import Dict, Any, Optional
from ..config.config_manager import ConfigManager
from ..utils.logger import get_logger


class AppController:
    """主应用控制器"""
    
    def __init__(self):
        """初始化应用控制器"""
        self.logger = get_logger('AppController')
        self.config = ConfigManager()
        
        # 应用状态
        self.running = False
        self.listening = False
        
        # 任务队列
        self.task_queue = queue.Queue()
        
        # 对话上下文
        self.conversation_context = {
            'last_intent': None,
            'last_entities': {},
            'last_email_id': None,
            'last_file_path': None
        }
        
        # 模块引用（延迟初始化）
        self.voice_pipeline = None
        self.task_executor = None
        self.tray_icon = None
        
        self.logger.info("应用控制器初始化完成")
    
    def start(self):
        """启动应用"""
        self.logger.info("正在启动应用...")
        self.running = True
        
        try:
            # 初始化各个模块
            self._initialize_modules()
            
            # 启动任务处理线程
            self.task_thread = threading.Thread(target=self._task_processor, daemon=True)
            self.task_thread.start()
            
            self.logger.info("应用启动成功")
            
        except Exception as e:
            self.logger.error(f"应用启动失败: {e}", exc_info=True)
            raise
    
    def stop(self):
        """停止应用"""
        self.logger.info("正在停止应用...")
        self.running = False
        
        # 停止各个模块
        if self.voice_pipeline:
            self.voice_pipeline.stop()
        
        self.logger.info("应用已停止")
    
    def _initialize_modules(self):
        """初始化各个模块"""
        self.logger.info("正在初始化模块...")
        
        # 这里会在后续步骤中导入和初始化各个模块
        # from ..modules.voice_pipeline import VoicePipeline
        # from ..modules.task_executor import TaskExecutor
        # 
        # self.voice_pipeline = VoicePipeline(self)
        # self.task_executor = TaskExecutor(self)
        
        self.logger.info("模块初始化完成")
    
    def _task_processor(self):
        """任务处理线程"""
        self.logger.info("任务处理线程已启动")
        
        while self.running:
            try:
                # 从队列获取任务（超时1秒）
                task = self.task_queue.get(timeout=1)
                
                # 处理任务
                self._process_task(task)
                
                # 标记任务完成
                self.task_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"任务处理出错: {e}", exc_info=True)
        
        self.logger.info("任务处理线程已停止")
    
    def _process_task(self, task: Dict[str, Any]):
        """处理单个任务"""
        task_type = task.get('type')
        self.logger.info(f"处理任务: {task_type}")
        
        try:
            if task_type == 'voice_command':
                self._handle_voice_command(task)
            elif task_type == 'email':
                self._handle_email_task(task)
            elif task_type == 'file':
                self._handle_file_task(task)
            else:
                self.logger.warning(f"未知任务类型: {task_type}")
        
        except Exception as e:
            self.logger.error(f"任务执行失败: {e}", exc_info=True)
            # 通过语音反馈错误
            self.speak(f"抱歉，执行任务时出现错误: {str(e)}")
    
    def _handle_voice_command(self, task: Dict[str, Any]):
        """处理语音指令"""
        text = task.get('text', '')
        self.logger.info(f"语音指令: {text}")
        
        # 调用意图理解
        if self.voice_pipeline:
            intent_result = self.voice_pipeline.understand_intent(text)
            
            # 更新对话上下文
            self.conversation_context['last_intent'] = intent_result.get('intent')
            self.conversation_context['last_entities'] = intent_result.get('entities', {})
            
            # 分发到相应的任务执行器
            if self.task_executor:
                result = self.task_executor.execute(intent_result)
                
                # 语音反馈结果
                self.speak(result.get('message', '已完成'))
    
    def _handle_email_task(self, task: Dict[str, Any]):
        """处理邮件任务"""
        self.logger.info(f"邮件任务: {task}")
        # 具体实现将在邮件模块中完成
    
    def _handle_file_task(self, task: Dict[str, Any]):
        """处理文件任务"""
        self.logger.info(f"文件任务: {task}")
        # 具体实现将在文件模块中完成
    
    def on_voice_activated(self):
        """语音激活回调"""
        self.logger.info("语音已激活")
        self.listening = True
        # 可以播放提示音或显示状态
    
    def on_voice_transcribed(self, text: str):
        """语音转录完成回调"""
        self.logger.info(f"语音转录: {text}")
        
        # 将语音指令添加到任务队列
        self.task_queue.put({
            'type': 'voice_command',
            'text': text
        })
    
    def speak(self, text: str):
        """语音播报"""
        self.logger.info(f"语音播报: {text}")
        
        if self.voice_pipeline:
            self.voice_pipeline.speak(text)
    
    def get_context(self, key: str) -> Any:
        """获取对话上下文"""
        return self.conversation_context.get(key)
    
    def set_context(self, key: str, value: Any):
        """设置对话上下文"""
        self.conversation_context[key] = value
