"""
配置管理模块测试
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from voice_assistant.config.config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    """配置管理器测试"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        
        # 临时修改配置路径（实际使用时需要更好的方式）
        # 这里仅作示例
    
    def tearDown(self):
        """测试后清理"""
        # 删除临时目录
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_default_config(self):
        """测试默认配置"""
        config = ConfigManager()
        
        # 检查默认配置项
        self.assertIsNotNone(config.get('version'))
        self.assertEqual(config.get('general.language'), 'zh-CN')
        self.assertEqual(config.get('voice.wake_word'), '小助手')
    
    def test_get_set_config(self):
        """测试配置的读写"""
        config = ConfigManager()
        
        # 设置配置
        config.set('test.key', 'test_value', save=False)
        
        # 读取配置
        value = config.get('test.key')
        self.assertEqual(value, 'test_value')
    
    def test_encrypt_decrypt(self):
        """测试加密解密"""
        config = ConfigManager()
        
        # 加密
        original = "test_password_123"
        encrypted = config.encrypt_credential(original)
        
        # 解密
        decrypted = config.decrypt_credential(encrypted)
        
        self.assertEqual(original, decrypted)
        self.assertNotEqual(original, encrypted)


if __name__ == '__main__':
    unittest.main()
