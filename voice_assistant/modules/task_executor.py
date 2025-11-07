"""
任务执行器
根据意图调度相应的功能模块
"""

from typing import Dict, Any
from ..utils.logger import get_logger
from .email_handler import EmailHandler
from .file_handler import FileHandler


class TaskExecutor:
    """任务执行器"""
    
    def __init__(self, app_controller):
        """初始化任务执行器"""
        self.app = app_controller
        self.config = app_controller.config
        self.logger = get_logger('TaskExecutor')
        
        # 初始化功能模块
        self.email_handler = EmailHandler(app_controller)
        self.file_handler = FileHandler(app_controller)
        
        self.logger.info("任务执行器初始化完成")
    
    def execute(self, intent_result: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务"""
        intent = intent_result.get('intent')
        entities = intent_result.get('entities', {})
        
        self.logger.info(f"执行任务: {intent}")
        
        try:
            # 邮件相关任务
            if intent == 'view_email':
                return self._execute_view_email(entities)
            elif intent == 'delete_email':
                return self._execute_delete_email(entities)
            elif intent == 'mark_email':
                return self._execute_mark_email(entities)
            
            # 文件相关任务
            elif intent == 'search_file':
                return self._execute_search_file(entities)
            elif intent == 'move_file':
                return self._execute_move_file(entities)
            elif intent == 'delete_file':
                return self._execute_delete_file(entities)
            elif intent == 'add_rule':
                return self._execute_add_rule(entities)
            
            # 未知意图
            else:
                return {
                    'success': False,
                    'message': '抱歉，我不太明白您的意思，请再说一次。'
                }
        
        except Exception as e:
            self.logger.error(f"任务执行失败: {e}", exc_info=True)
            return {
                'success': False,
                'message': f'任务执行失败: {str(e)}'
            }
    
    def _execute_view_email(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """执行查看邮件任务"""
        # 获取默认邮箱账户
        accounts = self.config.get('email.accounts', [])
        if not accounts:
            return {
                'success': False,
                'message': '您还没有配置邮箱账户，请先在设置中添加。'
            }
        
        # 使用第一个账户（或根据实体指定）
        email = entities.get('email', accounts[0].get('email'))
        
        params = {
            'email': email,
            'sender': entities.get('sender'),
            'time': entities.get('time', '今天'),
            'status': entities.get('status', '未读')
        }
        
        result = self.email_handler.view_emails(params)
        
        # 保存上下文
        if result.get('success') and result.get('emails'):
            self.app.set_context('last_email_id', result['emails'][0]['id'])
        
        return result
    
    def _execute_delete_email(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """执行删除邮件任务"""
        # 获取邮件 ID（从上下文或实体）
        email_id = entities.get('email_id') or self.app.get_context('last_email_id')
        
        if not email_id:
            return {
                'success': False,
                'message': '请先查看邮件，然后再删除。'
            }
        
        accounts = self.config.get('email.accounts', [])
        email = entities.get('email', accounts[0].get('email'))
        
        params = {
            'email': email,
            'email_id': email_id
        }
        
        return self.email_handler.delete_email(params)
    
    def _execute_mark_email(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """执行标记邮件任务"""
        email_id = entities.get('email_id') or self.app.get_context('last_email_id')
        
        if not email_id:
            return {
                'success': False,
                'message': '请先查看邮件，然后再标记。'
            }
        
        accounts = self.config.get('email.accounts', [])
        email = entities.get('email', accounts[0].get('email'))
        
        params = {
            'email': email,
            'email_id': email_id,
            'mark_as': entities.get('mark_as', 'read')
        }
        
        return self.email_handler.mark_email(params)
    
    def _execute_search_file(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """执行搜索文件任务"""
        params = {
            'filename': entities.get('filename', ''),
            'type': entities.get('type', ''),
            'location': entities.get('location', 'C:/'),
            'modified_days': entities.get('modified_days')
        }
        
        result = self.file_handler.search_files(params)
        
        # 保存上下文
        if result.get('success') and result.get('files'):
            self.app.set_context('last_file_path', result['files'][0]['path'])
        
        return result
    
    def _execute_move_file(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """执行移动文件任务"""
        params = {
            'source': entities.get('source'),
            'destination': entities.get('destination'),
            'type': entities.get('type')
        }
        
        return self.file_handler.move_files(params)
    
    def _execute_delete_file(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """执行删除文件任务"""
        # 获取文件路径（从上下文或实体）
        file_path = entities.get('path') or self.app.get_context('last_file_path')
        
        if not file_path:
            return {
                'success': False,
                'message': '请先搜索文件，然后再删除。'
            }
        
        params = {
            'path': file_path,
            'confirmed': entities.get('confirmed', False)
        }
        
        return self.file_handler.delete_files(params)
    
    def _execute_add_rule(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """执行添加整理规则任务"""
        rule = {
            'name': entities.get('rule_name', '自定义规则'),
            'file_types': entities.get('file_types', []),
            'action': entities.get('action', 'move'),
            'destination': entities.get('destination'),
            'days_old': entities.get('days_old', 0)
        }
        
        return self.file_handler.add_rule(rule)
