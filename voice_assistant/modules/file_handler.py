"""
文件整理模块
支持文件搜索、移动、删除和自动整理
"""

import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from ..utils.logger import get_logger


class FileOrganizer(FileSystemEventHandler):
    """文件整理事件处理器"""
    
    def __init__(self, file_handler):
        """初始化文件整理器"""
        self.file_handler = file_handler
        self.logger = get_logger('FileOrganizer')
    
    def on_created(self, event):
        """文件创建事件"""
        if event.is_directory:
            return
        
        self.logger.info(f"检测到新文件: {event.src_path}")
        
        # 应用整理规则
        self.file_handler.apply_rules(event.src_path)


class FileHandler:
    """文件处理器"""
    
    def __init__(self, app_controller):
        """初始化文件处理器"""
        self.app = app_controller
        self.config = app_controller.config
        self.logger = get_logger('FileHandler')
        
        # 文件监控器
        self.observer = Observer()
        self.organizer = FileOrganizer(self)
        
        # 启动监控
        self._start_watching()
        
        self.logger.info("文件处理器初始化完成")
    
    def _start_watching(self):
        """启动文件监控"""
        watch_folders = self.config.get('file.watch_folders', [])
        
        for folder in watch_folders:
            if Path(folder).exists():
                self.observer.schedule(self.organizer, folder, recursive=False)
                self.logger.info(f"开始监控文件夹: {folder}")
        
        if watch_folders:
            self.observer.start()
    
    def search_files(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """搜索文件"""
        filename = params.get('filename', '')
        file_type = params.get('type', '')
        location = params.get('location', 'C:/')
        modified_days = params.get('modified_days')
        
        try:
            self.logger.info(f"搜索文件: {filename}, 类型: {file_type}, 位置: {location}")
            
            # 构建搜索模式
            if file_type:
                pattern = f"*.{file_type}"
            elif filename:
                pattern = f"*{filename}*"
            else:
                pattern = "*"
            
            # 搜索文件
            root_path = Path(location)
            if not root_path.exists():
                return {
                    'success': False,
                    'message': f'路径不存在: {location}',
                    'files': []
                }
            
            files = []
            
            # 使用 rglob 递归搜索
            for file_path in root_path.rglob(pattern):
                if file_path.is_file():
                    # 时间过滤
                    if modified_days:
                        threshold = datetime.now() - timedelta(days=modified_days)
                        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if mtime > threshold:
                            continue
                    
                    files.append({
                        'path': str(file_path),
                        'name': file_path.name,
                        'size': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                    })
                    
                    # 限制结果数量
                    if len(files) >= 100:
                        break
            
            # 构建返回消息
            if files:
                message = f"找到 {len(files)} 个文件。"
                if filename:
                    message += f"名为'{filename}'的文件："
                message += f"第一个是 {files[0]['name']}"
            else:
                message = "没有找到符合条件的文件。"
            
            return {
                'success': True,
                'message': message,
                'files': files
            }
            
        except Exception as e:
            self.logger.error(f"搜索文件失败: {e}", exc_info=True)
            return {
                'success': False,
                'message': f'搜索文件失败: {str(e)}',
                'files': []
            }
    
    def move_files(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """移动文件"""
        source = params.get('source')
        destination = params.get('destination')
        file_type = params.get('type')
        
        try:
            source_path = Path(source)
            dest_path = Path(destination)
            
            if not source_path.exists():
                return {
                    'success': False,
                    'message': f'源路径不存在: {source}'
                }
            
            # 确保目标目录存在
            dest_path.mkdir(parents=True, exist_ok=True)
            
            # 移动文件
            moved_count = 0
            
            if source_path.is_file():
                # 移动单个文件
                shutil.move(str(source_path), str(dest_path / source_path.name))
                moved_count = 1
            else:
                # 移动目录中的文件
                pattern = f"*.{file_type}" if file_type else "*"
                for file_path in source_path.glob(pattern):
                    if file_path.is_file():
                        shutil.move(str(file_path), str(dest_path / file_path.name))
                        moved_count += 1
            
            return {
                'success': True,
                'message': f'已移动 {moved_count} 个文件到 {destination}'
            }
            
        except Exception as e:
            self.logger.error(f"移动文件失败: {e}", exc_info=True)
            return {
                'success': False,
                'message': f'移动文件失败: {str(e)}'
            }
    
    def delete_files(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """删除文件（需要确认）"""
        path = params.get('path')
        confirmed = params.get('confirmed', False)
        
        try:
            file_path = Path(path)
            
            if not file_path.exists():
                return {
                    'success': False,
                    'message': f'路径不存在: {path}'
                }
            
            # 二次确认
            if not confirmed:
                return {
                    'success': False,
                    'message': f'确认要删除 {path} 吗？请说"确认删除"',
                    'requires_confirmation': True
                }
            
            # 执行删除
            if file_path.is_file():
                file_path.unlink()
                message = f'已删除文件: {path}'
            else:
                shutil.rmtree(path)
                message = f'已删除文件夹: {path}'
            
            self.logger.info(message)
            
            return {
                'success': True,
                'message': message
            }
            
        except Exception as e:
            self.logger.error(f"删除文件失败: {e}", exc_info=True)
            return {
                'success': False,
                'message': f'删除文件失败: {str(e)}'
            }
    
    def apply_rules(self, file_path: str):
        """应用文件整理规则"""
        rules = self.config.get('file.rules', [])
        
        for rule in rules:
            try:
                if self._match_rule(file_path, rule):
                    self._execute_rule(file_path, rule)
                    break  # 只应用第一个匹配的规则
            except Exception as e:
                self.logger.error(f"应用规则失败: {e}")
    
    def _match_rule(self, file_path: str, rule: Dict[str, Any]) -> bool:
        """检查文件是否匹配规则"""
        path = Path(file_path)
        
        # 文件类型匹配
        if 'file_types' in rule:
            if path.suffix.lower() not in [f".{ft.lower()}" for ft in rule['file_types']]:
                return False
        
        # 文件名模式匹配
        if 'name_pattern' in rule:
            if rule['name_pattern'] not in path.name:
                return False
        
        return True
    
    def _execute_rule(self, file_path: str, rule: Dict[str, Any]):
        """执行文件整理规则"""
        action = rule.get('action')
        
        if action == 'move':
            destination = rule.get('destination')
            if destination:
                dest_path = Path(destination)
                dest_path.mkdir(parents=True, exist_ok=True)
                shutil.move(file_path, str(dest_path / Path(file_path).name))
                self.logger.info(f"根据规则移动文件: {file_path} -> {destination}")
        
        elif action == 'delete':
            # 自动删除需要额外的安全检查
            days_old = rule.get('days_old', 0)
            if days_old > 0:
                mtime = datetime.fromtimestamp(Path(file_path).stat().st_mtime)
                if (datetime.now() - mtime).days >= days_old:
                    Path(file_path).unlink()
                    self.logger.info(f"根据规则删除文件: {file_path}")
    
    def add_rule(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """添加文件整理规则"""
        try:
            # 生成规则 ID
            import uuid
            rule['id'] = str(uuid.uuid4())
            
            # 保存规则
            self.config.add_file_rule(rule)
            
            return {
                'success': True,
                'message': '文件整理规则已添加'
            }
        except Exception as e:
            self.logger.error(f"添加规则失败: {e}")
            return {
                'success': False,
                'message': f'添加规则失败: {str(e)}'
            }
    
    def stop(self):
        """停止文件处理器"""
        self.logger.info("停止文件监控...")
        self.observer.stop()
        self.observer.join()
