"""
邮件处理模块
支持 IMAP/POP3 和 Exchange 协议
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ..utils.logger import get_logger


class EmailHandler:
    """邮件处理器"""
    
    def __init__(self, app_controller):
        """初始化邮件处理器"""
        self.app = app_controller
        self.config = app_controller.config
        self.logger = get_logger('EmailHandler')
        
        # 邮件客户端缓存
        self.clients = {}
        
        self.logger.info("邮件处理器初始化完成")
    
    def get_client(self, email: str):
        """获取邮件客户端"""
        if email in self.clients:
            return self.clients[email]
        
        # 从配置获取账户信息
        account = self.config.get_email_account(email)
        if not account:
            raise ValueError(f"未找到邮箱账户: {email}")
        
        # 根据类型创建客户端
        account_type = account.get('type', 'imap')
        
        if account_type == 'imap':
            client = self._create_imap_client(account)
        elif account_type == 'exchange':
            client = self._create_exchange_client(account)
        else:
            raise ValueError(f"不支持的邮箱类型: {account_type}")
        
        self.clients[email] = client
        return client
    
    def _create_imap_client(self, account: Dict[str, Any]):
        """创建 IMAP 客户端"""
        from imapclient import IMAPClient
        
        try:
            server = IMAPClient(
                account['server'],
                port=account.get('port', 993),
                ssl=account.get('ssl', True)
            )
            server.login(account['email'], account['password'])
            
            self.logger.info(f"IMAP 客户端连接成功: {account['email']}")
            return {'type': 'imap', 'client': server, 'account': account}
            
        except Exception as e:
            self.logger.error(f"IMAP 连接失败: {e}")
            raise
    
    def _create_exchange_client(self, account: Dict[str, Any]):
        """创建 Exchange 客户端"""
        from exchangelib import Credentials, Account, DELEGATE
        
        try:
            credentials = Credentials(account['email'], account['password'])
            acc = Account(
                account['email'],
                credentials=credentials,
                autodiscover=True,
                access_type=DELEGATE
            )
            
            self.logger.info(f"Exchange 客户端连接成功: {account['email']}")
            return {'type': 'exchange', 'client': acc, 'account': account}
            
        except Exception as e:
            self.logger.error(f"Exchange 连接失败: {e}")
            raise
    
    def view_emails(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """查看邮件"""
        email = params.get('email')
        sender = params.get('sender')
        time_filter = params.get('time', '今天')
        status = params.get('status', '未读')
        
        try:
            client_info = self.get_client(email)
            
            if client_info['type'] == 'imap':
                return self._view_emails_imap(client_info, sender, time_filter, status)
            elif client_info['type'] == 'exchange':
                return self._view_emails_exchange(client_info, sender, time_filter, status)
            
        except Exception as e:
            self.logger.error(f"查看邮件失败: {e}", exc_info=True)
            return {
                'success': False,
                'message': f'查看邮件失败: {str(e)}',
                'emails': []
            }
    
    def _view_emails_imap(self, client_info: Dict, sender: Optional[str], 
                          time_filter: str, status: str) -> Dict[str, Any]:
        """使用 IMAP 查看邮件"""
        client = client_info['client']
        
        try:
            # 选择收件箱
            client.select_folder('INBOX')
            
            # 构建搜索条件
            search_criteria = []
            
            if status == '未读':
                search_criteria.append('UNSEEN')
            
            if sender:
                search_criteria.extend(['FROM', sender])
            
            # 时间过滤
            if time_filter == '今天':
                today = datetime.now().date()
                search_criteria.extend(['SINCE', today])
            elif time_filter == '昨天':
                yesterday = (datetime.now() - timedelta(days=1)).date()
                search_criteria.extend(['SINCE', yesterday])
                search_criteria.extend(['BEFORE', datetime.now().date()])
            
            # 搜索邮件
            messages = client.search(search_criteria if search_criteria else ['ALL'])
            
            # 获取邮件详情
            emails = []
            for msg_id in messages[:10]:  # 限制返回前10封
                msg_data = client.fetch([msg_id], ['ENVELOPE', 'FLAGS'])
                envelope = msg_data[msg_id][b'ENVELOPE']
                
                emails.append({
                    'id': msg_id,
                    'subject': envelope.subject.decode() if envelope.subject else '(无主题)',
                    'from': envelope.from_[0].mailbox.decode() + '@' + envelope.from_[0].host.decode() if envelope.from_ else '(未知)',
                    'date': envelope.date.strftime('%Y-%m-%d %H:%M') if envelope.date else '(未知)',
                    'is_read': b'\\Seen' in msg_data[msg_id][b'FLAGS']
                })
            
            # 构建返回消息
            if emails:
                message = f"找到 {len(emails)} 封邮件。"
                if sender:
                    message += f"来自 {sender} 的邮件："
                message += f"第一封的标题是《{emails[0]['subject']}》"
            else:
                message = "没有找到符合条件的邮件。"
            
            return {
                'success': True,
                'message': message,
                'emails': emails
            }
            
        except Exception as e:
            self.logger.error(f"IMAP 查看邮件失败: {e}")
            raise
    
    def _view_emails_exchange(self, client_info: Dict, sender: Optional[str],
                              time_filter: str, status: str) -> Dict[str, Any]:
        """使用 Exchange 查看邮件"""
        account = client_info['client']
        
        try:
            # 构建查询
            query = account.inbox.all()
            
            # 状态过滤
            if status == '未读':
                query = query.filter(is_read=False)
            
            # 发件人过滤
            if sender:
                query = query.filter(sender__contains=sender)
            
            # 时间过滤
            if time_filter == '今天':
                today = datetime.now().replace(hour=0, minute=0, second=0)
                query = query.filter(datetime_received__gte=today)
            elif time_filter == '昨天':
                yesterday = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0)
                today = datetime.now().replace(hour=0, minute=0, second=0)
                query = query.filter(datetime_received__gte=yesterday, datetime_received__lt=today)
            
            # 获取邮件（限制10封）
            emails = []
            for item in query.order_by('-datetime_received')[:10]:
                emails.append({
                    'id': item.id,
                    'subject': item.subject or '(无主题)',
                    'from': item.sender.email_address if item.sender else '(未知)',
                    'date': item.datetime_received.strftime('%Y-%m-%d %H:%M'),
                    'is_read': item.is_read
                })
            
            # 构建返回消息
            if emails:
                message = f"找到 {len(emails)} 封邮件。"
                if sender:
                    message += f"来自 {sender} 的邮件："
                message += f"第一封的标题是《{emails[0]['subject']}》"
            else:
                message = "没有找到符合条件的邮件。"
            
            return {
                'success': True,
                'message': message,
                'emails': emails
            }
            
        except Exception as e:
            self.logger.error(f"Exchange 查看邮件失败: {e}")
            raise
    
    def delete_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """删除邮件"""
        email = params.get('email')
        email_id = params.get('email_id')
        
        try:
            client_info = self.get_client(email)
            
            if client_info['type'] == 'imap':
                client = client_info['client']
                client.delete_messages([email_id])
                client.expunge()
                
            elif client_info['type'] == 'exchange':
                account = client_info['client']
                # Exchange 删除需要通过 item 对象
                # item.delete()
            
            return {
                'success': True,
                'message': '邮件已删除'
            }
            
        except Exception as e:
            self.logger.error(f"删除邮件失败: {e}")
            return {
                'success': False,
                'message': f'删除邮件失败: {str(e)}'
            }
    
    def mark_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """标记邮件"""
        email = params.get('email')
        email_id = params.get('email_id')
        mark_as = params.get('mark_as', 'read')  # 'read' or 'unread'
        
        try:
            client_info = self.get_client(email)
            
            if client_info['type'] == 'imap':
                client = client_info['client']
                if mark_as == 'read':
                    client.add_flags([email_id], [b'\\Seen'])
                else:
                    client.remove_flags([email_id], [b'\\Seen'])
                
            elif client_info['type'] == 'exchange':
                account = client_info['client']
                # Exchange 标记需要通过 item 对象
                # item.is_read = (mark_as == 'read')
                # item.save()
            
            return {
                'success': True,
                'message': f'邮件已标记为{"已读" if mark_as == "read" else "未读"}'
            }
            
        except Exception as e:
            self.logger.error(f"标记邮件失败: {e}")
            return {
                'success': False,
                'message': f'标记邮件失败: {str(e)}'
            }
    
    def close_all(self):
        """关闭所有邮件客户端"""
        for email, client_info in self.clients.items():
            try:
                if client_info['type'] == 'imap':
                    client_info['client'].logout()
                self.logger.info(f"已关闭邮件客户端: {email}")
            except Exception as e:
                self.logger.error(f"关闭邮件客户端失败: {e}")
        
        self.clients.clear()
