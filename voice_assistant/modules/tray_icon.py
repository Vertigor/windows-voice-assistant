"""
系统托盘图标模块
"""

from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
from ..utils.logger import get_logger


class TrayIcon:
    """系统托盘图标"""
    
    def __init__(self, app_controller):
        """初始化托盘图标"""
        self.app = app_controller
        self.config = app_controller.config
        self.logger = get_logger('TrayIcon')
        
        # 创建图标
        self.icon = None
        self.create_icon()
        
        self.logger.info("系统托盘图标初始化完成")
    
    def create_icon(self):
        """创建托盘图标"""
        # 创建简单的图标图像
        image = self._create_icon_image()
        
        # 创建菜单
        menu = Menu(
            MenuItem('启动监听', self._on_start_listening, default=True),
            MenuItem('停止监听', self._on_stop_listening),
            Menu.SEPARATOR,
            MenuItem('设置', self._on_settings),
            MenuItem('查看日志', self._on_view_logs),
            Menu.SEPARATOR,
            MenuItem('关于', self._on_about),
            MenuItem('退出', self._on_quit)
        )
        
        # 创建图标
        self.icon = Icon(
            'VoiceAssistant',
            image,
            '语音助手',
            menu
        )
    
    def _create_icon_image(self):
        """创建图标图像"""
        # 创建一个简单的圆形图标
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        
        # 绘制圆形
        draw.ellipse([8, 8, 56, 56], fill='#4CAF50', outline='#2E7D32')
        
        # 绘制麦克风图标（简化版）
        draw.rectangle([28, 20, 36, 35], fill='white')
        draw.ellipse([26, 35, 38, 42], fill='white')
        draw.line([32, 42, 32, 48], fill='white', width=2)
        
        return image
    
    def run(self):
        """运行托盘图标"""
        self.logger.info("启动系统托盘图标...")
        self.icon.run()
    
    def stop(self):
        """停止托盘图标"""
        if self.icon:
            self.icon.stop()
    
    def update_status(self, status: str):
        """更新托盘图标状态"""
        status_text = {
            'idle': '语音助手 - 空闲',
            'listening': '语音助手 - 监听中',
            'processing': '语音助手 - 处理中'
        }
        
        if self.icon:
            self.icon.title = status_text.get(status, '语音助手')
    
    # 菜单回调函数
    def _on_start_listening(self, icon, item):
        """启动监听"""
        self.logger.info("用户点击：启动监听")
        if self.app.voice_pipeline:
            self.app.voice_pipeline.start_listening()
            self.update_status('listening')
    
    def _on_stop_listening(self, icon, item):
        """停止监听"""
        self.logger.info("用户点击：停止监听")
        if self.app.voice_pipeline:
            self.app.voice_pipeline.stop_listening()
            self.update_status('idle')
    
    def _on_settings(self, icon, item):
        """打开设置"""
        self.logger.info("用户点击：设置")
        # 这里可以打开一个设置窗口或配置文件
        import os
        os.startfile(self.config.config_file)
    
    def _on_view_logs(self, icon, item):
        """查看日志"""
        self.logger.info("用户点击：查看日志")
        import os
        from ..utils.logger import Logger
        log_dir = Logger().log_dir
        os.startfile(log_dir)
    
    def _on_about(self, icon, item):
        """关于"""
        self.logger.info("用户点击：关于")
        # 可以显示一个关于对话框
        print("Windows Voice Assistant v0.1.0")
        print("一个功能强大的语音助手")
    
    def _on_quit(self, icon, item):
        """退出应用"""
        self.logger.info("用户点击：退出")
        self.app.stop()
        self.stop()
