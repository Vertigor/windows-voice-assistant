# Windows Voice Assistant

一个功能强大的 Windows 平台语音助手，支持邮件查看和文件整理的智能语音对话应用。

## 功能特性

### 语音交互
- ✅ 实时语音输入（延迟 ≤1 秒）
- ✅ 唤醒词激活（支持自定义）
- ✅ 快捷键激活（如 Win+V）
- ✅ 自然语音播报
- ✅ 多轮对话支持

### 邮件处理
- ✅ 支持 IMAP/POP3（Gmail、QQ、163 等）
- ✅ 支持 Exchange/Office 365
- ✅ 按时间、发件人、状态筛选邮件
- ✅ 邮件标记、删除、移动
- ✅ 附件下载

### 文件整理
- ✅ 智能文件搜索
- ✅ 按规则自动分类
- ✅ 文件移动、复制、删除
- ✅ 自定义整理规则
- ✅ 实时文件监控

## 技术栈

- **语音识别**: RealtimeSTT + Whisper
- **语音合成**: Coqui TTS
- **意图理解**: Ollama + 本地 LLM / OpenAI 兼容 API
- **邮件处理**: IMAPClient + exchangelib
- **文件操作**: pathlib + shutil + watchdog
- **系统集成**: pystray + pynput

## 安装

### 前置要求

1. **Python 3.9-3.11**
2. **LLM 服务**（二选一）：
   - **方案一：Ollama**（本地运行）
     - 下载：https://ollama.com/download
     - 安装后运行：`ollama pull qwen2.5:3b`
   - **方案二：OpenAI 兼容 API**（云服务）
     - 支持 OpenAI、DeepSeek、通义千问等提供商
     - 需要 API Key

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/Vertigor/windows-voice-assistant.git
cd windows-voice-assistant

# 安装依赖
pip install -r requirements.txt

# 首次运行配置
python -m voice_assistant.setup
```

## 使用方法

### 启动应用

```bash
python -m voice_assistant
```

应用将在系统托盘中运行。

### 激活方式

1. **快捷键**: 按 `Win+V`
2. **唤醒词**: 说出"小助手"

### 示例指令

**邮件相关**:
- "查看今天的未读邮件"
- "读一下张三发来的邮件"
- "删除垃圾邮件"

**文件相关**:
- "把下载文件夹里的 PDF 移到文档库"
- "搜索电脑里名为'项目计划'的 Excel"
- "删除桌面上 30 天前的临时文件"

## 配置

首次运行时，应用会引导您完成配置：

1. 邮箱账户设置
2. 文件整理规则
3. 唤醒词和快捷键
4. LLM 服务配置

配置文件位于：`%APPDATA%/VoiceAssistant/config.json`

### LLM 配置示例

**使用 Ollama（本地）**：
```json
{
  "llm": {
    "provider": "ollama",
    "model": "qwen2.5:3b",
    "api_base": "http://localhost:11434",
    "temperature": 0.7
  }
}
```

**使用 OpenAI**：
```json
{
  "llm": {
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "api_base": "https://api.openai.com/v1",
    "api_key": "sk-...",
    "temperature": 0.7,
    "max_tokens": 500
  }
}
```

**使用 DeepSeek**：
```json
{
  "llm": {
    "provider": "openai",
    "model": "deepseek-chat",
    "api_base": "https://api.deepseek.com/v1",
    "api_key": "sk-...",
    "temperature": 0.7,
    "max_tokens": 500
  }
}
```

## 安全性

- ✅ 邮箱密码加密存储
- ✅ 危险操作二次确认
- ✅ 完整操作日志
- ✅ 本地离线运行

## 开发

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest tests/

# 代码格式化
black voice_assistant/
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 致谢

本项目基于以下优秀的开源项目：
- [RealtimeSTT](https://github.com/KoljaB/RealtimeSTT)
- [Whisper](https://github.com/openai/whisper)
- [Coqui TTS](https://github.com/coqui-ai/TTS)
- [Ollama](https://ollama.com)
- [IMAPClient](https://github.com/mjs/imapclient)
- [exchangelib](https://github.com/ecederstrand/exchangelib)
