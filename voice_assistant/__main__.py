"""
主程序入口
"""

import sys
from .core.app_controller import AppController
from .modules.tray_icon import TrayIcon
from .modules.voice_pipeline import VoicePipeline
from .modules.task_executor import TaskExecutor
from .utils.logger import get_logger


def main():
    """主函数"""
    logger = get_logger('Main')
    logger.info("=" * 50)
    logger.info("Windows Voice Assistant 启动中...")
    logger.info("=" * 50)
    
    try:
        # 创建应用控制器
        app = AppController()
        
        # 检查是否首次运行
        if app.config.is_first_run():
            logger.info("检测到首次运行，请先进行配置")
            print("\n欢迎使用 Windows Voice Assistant!")
            print("这是您第一次运行本应用，请先完成基本配置。")
            print(f"配置文件位于: {app.config.config_file}")
            print("\n请参考 README.md 完成配置后再次运行。\n")
            
            # 保存默认配置
            app.config.save_config()
            return
        
        # 初始化模块
        logger.info("初始化语音管道...")
        app.voice_pipeline = VoicePipeline(app)
        app.voice_pipeline.initialize()
        
        logger.info("初始化任务执行器...")
        app.task_executor = TaskExecutor(app)
        
        logger.info("初始化系统托盘...")
        app.tray_icon = TrayIcon(app)
        
        # 启动应用
        app.start()
        
        # 运行托盘图标（阻塞）
        logger.info("应用已就绪，运行在系统托盘中")
        print("\n应用已启动！")
        print("- 系统托盘图标已显示")
        print("- 右键点击托盘图标查看菜单")
        print("- 按 Ctrl+C 退出\n")
        
        app.tray_icon.run()
        
    except KeyboardInterrupt:
        logger.info("收到退出信号")
        print("\n正在退出...")
    except Exception as e:
        logger.error(f"应用运行出错: {e}", exc_info=True)
        print(f"\n错误: {e}")
        sys.exit(1)
    finally:
        logger.info("应用已退出")


if __name__ == '__main__':
    main()
