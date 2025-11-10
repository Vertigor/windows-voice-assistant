"""
语音处理管道
整合语音识别、意图理解和语音合成
"""

import threading
import requests
from typing import Dict, Any, Optional, Callable
from ..utils.logger import get_logger


class VoicePipeline:
    """语音处理管道"""
    
    def __init__(self, app_controller):
        """初始化语音管道"""
        self.app = app_controller
        self.config = app_controller.config
        self.logger = get_logger('VoicePipeline')
        
        # 语音识别器
        self.stt_engine = None
        # 语音合成器
        self.tts_engine = None
        
        # 运行状态
        self.running = False
        
        self.logger.info("语音管道初始化完成")
    
    def initialize(self):
        """初始化语音引擎"""
        self.logger.info("正在初始化语音引擎...")
        
        try:
            # 初始化 STT
            self._initialize_stt()
            
            # 初始化 TTS
            self._initialize_tts()
            
            self.running = True
            self.logger.info("语音引擎初始化成功")
            
        except Exception as e:
            self.logger.error(f"语音引擎初始化失败: {e}", exc_info=True)
            raise
    
    def _initialize_stt(self):
        """初始化语音识别"""
        self.logger.info("初始化 STT 引擎...")
        
        try:
            # 注意：RealtimeSTT 需要在实际 Windows 环境中运行
            # 这里提供接口框架
            # from RealtimeSTT import AudioToTextRecorder
            # 
            # self.stt_engine = AudioToTextRecorder(
            #     model=self.config.get('voice.stt_model', 'base'),
            #     language='zh',
            #     on_recording_start=self._on_recording_start,
            #     on_recording_stop=self._on_recording_stop,
            #     on_transcription_start=self._on_transcription_start,
            #     on_realtime_transcription_update=self._on_realtime_update,
            #     on_realtime_transcription_stabilized=self._on_transcription_stabilized
            # )
            
            self.logger.info("STT 引擎初始化成功（模拟模式）")
            
        except Exception as e:
            self.logger.error(f"STT 引擎初始化失败: {e}")
            raise
    
    def _initialize_tts(self):
        """初始化语音合成"""
        self.logger.info("初始化 TTS 引擎...")
        
        try:
            # 注意：Coqui TTS 需要在实际环境中安装
            # from TTS.api import TTS
            # 
            # model_name = self.config.get('voice.tts_model')
            # self.tts_engine = TTS(model_name)
            
            self.logger.info("TTS 引擎初始化成功（模拟模式）")
            
        except Exception as e:
            self.logger.error(f"TTS 引擎初始化失败: {e}")
            raise
    
    def start_listening(self):
        """开始监听"""
        if not self.running:
            self.logger.warning("语音引擎未初始化")
            return
        
        self.logger.info("开始监听...")
        
        # 启动 STT 录音
        # if self.stt_engine:
        #     self.stt_engine.start()
    
    def stop_listening(self):
        """停止监听"""
        self.logger.info("停止监听...")
        
        # 停止 STT 录音
        # if self.stt_engine:
        #     self.stt_engine.stop()
    
    def understand_intent(self, text: str) -> Dict[str, Any]:
        """理解用户意图"""
        self.logger.info(f"分析意图: {text}")
        
        try:
            llm_config = self.config.get('llm', {})
            provider = llm_config.get('provider', 'ollama')
            
            # 构建 Prompt
            prompt = self._build_intent_prompt(text)
            
            # 根据提供商调用不同的 API
            if provider == 'openai':
                intent_text = self._call_openai_api(prompt, llm_config)
            else:  # ollama
                intent_text = self._call_ollama_api(prompt, llm_config)
            
            # 解析意图结果
            return self._parse_intent_response(intent_text)
        
        except Exception as e:
            self.logger.error(f"意图理解失败: {e}", exc_info=True)
            return {'intent': 'unknown', 'entities': {}}
    
    def _call_ollama_api(self, prompt: str, config: Dict[str, Any]) -> str:
        """调用 Ollama API"""
        api_base = config.get('api_base', 'http://localhost:11434')
        model = config.get('model', 'qwen2.5:3b')
        
        response = requests.post(
            f"{api_base}/api/generate",
            json={
                'model': model,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': config.get('temperature', 0.7)
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', '')
        else:
            self.logger.error(f"Ollama API 调用失败: {response.status_code}")
            return ''
    
    def _call_openai_api(self, prompt: str, config: Dict[str, Any]) -> str:
        """调用 OpenAI 兼容 API"""
        from openai import OpenAI
        
        api_base = config.get('api_base', 'https://api.openai.com/v1')
        api_key = config.get('api_key', '')
        model = config.get('model', 'gpt-3.5-turbo')
        
        if not api_key:
            self.logger.error("OpenAI API Key 未配置")
            return ''
        
        try:
            client = OpenAI(
                api_key=api_key,
                base_url=api_base
            )
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "你是一个智能语音助手的意图识别系统。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=config.get('temperature', 0.7),
                max_tokens=config.get('max_tokens', 500)
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            self.logger.error(f"OpenAI API 调用失败: {e}")
            return ''
    
    def _build_intent_prompt(self, text: str) -> str:
        """构建意图理解的 Prompt"""
        prompt = f"""你是一个智能语音助手的意图识别系统。请分析用户的语音指令，识别意图和关键实体。

支持的意图类型：
- view_email: 查看邮件
- delete_email: 删除邮件
- mark_email: 标记邮件
- search_file: 搜索文件
- move_file: 移动文件
- delete_file: 删除文件
- organize_file: 整理文件
- unknown: 无法识别

用户指令: {text}

请以 JSON 格式返回结果，包含 intent（意图）和 entities（实体）字段。
例如：
{{"intent": "view_email", "entities": {{"sender": "张三", "time": "今天", "status": "未读"}}}}

返回："""
        
        return prompt
    
    def _parse_intent_response(self, response: str) -> Dict[str, Any]:
        """解析意图识别结果"""
        import json
        import re
        
        try:
            # 尝试提取 JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result
            else:
                self.logger.warning(f"无法解析意图响应: {response}")
                return {'intent': 'unknown', 'entities': {}}
        
        except Exception as e:
            self.logger.error(f"解析意图响应失败: {e}")
            return {'intent': 'unknown', 'entities': {}}
    
    def speak(self, text: str):
        """语音播报"""
        self.logger.info(f"TTS: {text}")
        
        try:
            # 使用 TTS 引擎合成语音
            # if self.tts_engine:
            #     # 合成音频
            #     audio_path = self.tts_engine.tts_to_file(
            #         text=text,
            #         file_path="temp_speech.wav"
            #     )
            #     
            #     # 播放音频
            #     import sounddevice as sd
            #     import soundfile as sf
            #     data, samplerate = sf.read(audio_path)
            #     sd.play(data, samplerate)
            #     sd.wait()
            
            # 模拟模式：仅记录日志
            self.logger.info(f"[TTS 播报] {text}")
            
        except Exception as e:
            self.logger.error(f"语音播报失败: {e}", exc_info=True)
    
    def stop(self):
        """停止语音管道"""
        self.logger.info("停止语音管道...")
        self.running = False
        self.stop_listening()
    
    # STT 回调函数
    def _on_recording_start(self):
        """录音开始"""
        self.logger.debug("录音开始")
        self.app.on_voice_activated()
    
    def _on_recording_stop(self):
        """录音停止"""
        self.logger.debug("录音停止")
    
    def _on_transcription_start(self):
        """转录开始"""
        self.logger.debug("转录开始")
    
    def _on_realtime_update(self, text: str):
        """实时转录更新"""
        self.logger.debug(f"实时转录: {text}")
    
    def _on_transcription_stabilized(self, text: str):
        """转录稳定（最终结果）"""
        self.logger.info(f"转录完成: {text}")
        self.app.on_voice_transcribed(text)
