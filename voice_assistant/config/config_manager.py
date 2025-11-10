"""
配置管理模块
负责应用配置的加载、保存和验证
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
import base64


class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        """初始化配置管理器"""
        # 配置文件路径
        self.config_dir = Path(os.getenv('APPDATA')) / 'VoiceAssistant'
        self.config_file = self.config_dir / 'config.json'
        self.credentials_file = self.config_dir / 'credentials.enc'
        self.key_file = self.config_dir / '.key'
        
        # 确保配置目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载或生成加密密钥
        self._encryption_key = self._load_or_create_key()
        self._cipher = Fernet(self._encryption_key)
        
        # 默认配置
        self.default_config = {
            'version': '0.1.0',
            'general': {
                'language': 'zh-CN',
                'auto_start': False,
                'log_level': 'INFO'
            },
            'voice': {
                'wake_word': '小助手',
                'hotkey': 'win+v',
                'activation_method': 'both',  # 'wake_word', 'hotkey', 'both'
                'stt_model': 'base',  # Whisper 模型大小
                'tts_model': 'tts_models/zh-CN/baker/tacotron2-DDC',
                'speech_rate': 1.0,
                'volume': 0.8
            },
            'email': {
                'enabled': False,
                'accounts': []
            },
            'file': {
                'enabled': True,
                'watch_folders': [],
                'rules': []
            },
            'llm': {
                'provider': 'ollama',  # 'ollama' 或 'openai'
                'model': 'qwen2.5:3b',
                'api_base': 'http://localhost:11434',
                'api_key': '',  # OpenAI 兼容接口的 API Key
                'temperature': 0.7,
                'max_tokens': 500
            }
        }
        
        # 加载配置
        self.config = self.load_config()
    
    def _load_or_create_key(self) -> bytes:
        """加载或创建加密密钥"""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            # 设置文件为只读
            os.chmod(self.key_file, 0o600)
            return key
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 合并默认配置（处理新增配置项）
                return self._merge_config(self.default_config, config)
            except Exception as e:
                print(f"加载配置失败: {e}，使用默认配置")
                return self.default_config.copy()
        else:
            return self.default_config.copy()
    
    def save_config(self) -> bool:
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def _merge_config(self, default: Dict, user: Dict) -> Dict:
        """合并默认配置和用户配置"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项（支持点号分隔的路径）"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any, save: bool = True) -> bool:
        """设置配置项（支持点号分隔的路径）"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        
        if save:
            return self.save_config()
        return True
    
    def encrypt_credential(self, data: str) -> str:
        """加密凭据"""
        return self._cipher.encrypt(data.encode()).decode()
    
    def decrypt_credential(self, encrypted_data: str) -> str:
        """解密凭据"""
        return self._cipher.decrypt(encrypted_data.encode()).decode()
    
    def save_email_account(self, account_data: Dict[str, Any]) -> bool:
        """保存邮箱账户（加密密码）"""
        try:
            # 加密密码
            if 'password' in account_data:
                account_data['password'] = self.encrypt_credential(account_data['password'])
            
            # 添加到账户列表
            accounts = self.get('email.accounts', [])
            
            # 检查是否已存在（根据邮箱地址）
            existing_index = None
            for i, acc in enumerate(accounts):
                if acc.get('email') == account_data.get('email'):
                    existing_index = i
                    break
            
            if existing_index is not None:
                accounts[existing_index] = account_data
            else:
                accounts.append(account_data)
            
            self.set('email.accounts', accounts)
            return True
        except Exception as e:
            print(f"保存邮箱账户失败: {e}")
            return False
    
    def get_email_account(self, email: str) -> Optional[Dict[str, Any]]:
        """获取邮箱账户（解密密码）"""
        accounts = self.get('email.accounts', [])
        for account in accounts:
            if account.get('email') == email:
                # 解密密码
                if 'password' in account:
                    account_copy = account.copy()
                    account_copy['password'] = self.decrypt_credential(account['password'])
                    return account_copy
        return None
    
    def add_file_rule(self, rule: Dict[str, Any]) -> bool:
        """添加文件整理规则"""
        rules = self.get('file.rules', [])
        rules.append(rule)
        return self.set('file.rules', rules)
    
    def remove_file_rule(self, rule_id: str) -> bool:
        """删除文件整理规则"""
        rules = self.get('file.rules', [])
        rules = [r for r in rules if r.get('id') != rule_id]
        return self.set('file.rules', rules)
    
    def is_first_run(self) -> bool:
        """检查是否首次运行"""
        return not self.config_file.exists()
