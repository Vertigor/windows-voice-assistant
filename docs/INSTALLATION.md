# 安装指南

本文档详细说明如何在 Windows 系统上安装和配置 Windows Voice Assistant。

## 系统要求

- **操作系统**: Windows 10/11 (64位)
- **Python**: 3.9 - 3.11
- **内存**: 建议 8GB 以上
- **存储**: 至少 5GB 可用空间（用于模型文件）
- **硬件**: 建议使用支持 CUDA 的 NVIDIA 显卡（可选，用于加速）

## 安装步骤

### 1. 安装 Python

如果您还没有安装 Python，请访问 [Python 官网](https://www.python.org/downloads/) 下载并安装 Python 3.9-3.11 版本。

**注意**: 安装时请勾选 "Add Python to PATH" 选项。

### 2. 安装 Ollama

Ollama 用于本地运行大语言模型，是意图理解功能的核心组件。

1. 访问 [Ollama 官网](https://ollama.com/download)
2. 下载 Windows 版本安装程序
3. 运行安装程序，按提示完成安装
4. 安装完成后，打开命令提示符，运行以下命令下载模型：

```bash
ollama pull qwen2.5:3b
```

**注意**: 模型文件约 2GB，下载可能需要一些时间。

### 3. 克隆项目

打开命令提示符或 PowerShell，执行：

```bash
git clone https://github.com/Vertigor/windows-voice-assistant.git
cd windows-voice-assistant
```

### 4. 创建虚拟环境（推荐）

```bash
python -m venv venv
venv\Scripts\activate
```

### 5. 安装依赖

```bash
pip install -r requirements.txt
```

**注意**: 
- 安装过程可能需要 10-20 分钟
- 如果遇到网络问题，可以使用国内镜像：
  ```bash
  pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
  ```

### 6. 下载 Whisper 模型

首次运行时，Whisper 模型会自动下载。如果您想手动下载，可以运行：

```python
import whisper
whisper.load_model("base")
```

### 7. 下载 TTS 模型

首次运行时，TTS 模型也会自动下载。如果您想手动下载，可以运行：

```python
from TTS.api import TTS
tts = TTS("tts_models/zh-CN/baker/tacotron2-DDC")
```

## 配置

### 首次运行

首次运行应用时，会自动创建默认配置文件：

```bash
python -m voice_assistant
```

配置文件位于：`%APPDATA%\VoiceAssistant\config.json`

### 配置邮箱账户

编辑配置文件，添加邮箱账户信息：

```json
{
  "email": {
    "enabled": true,
    "accounts": [
      {
        "name": "我的 Gmail",
        "type": "imap",
        "email": "your.email@gmail.com",
        "password": "your_password",
        "server": "imap.gmail.com",
        "port": 993,
        "ssl": true
      }
    ]
  }
}
```

**安全提示**: 
- Gmail 需要使用"应用专用密码"，不能使用账户密码
- 密码会在保存时自动加密

### 配置文件整理规则

在配置文件中添加自动整理规则：

```json
{
  "file": {
    "enabled": true,
    "watch_folders": [
      "C:\\Users\\YourName\\Downloads"
    ],
    "rules": [
      {
        "id": "rule1",
        "name": "整理图片",
        "file_types": ["jpg", "png", "gif"],
        "action": "move",
        "destination": "C:\\Users\\YourName\\Pictures\\Auto"
      }
    ]
  }
}
```

## 验证安装

运行以下命令验证安装：

```bash
python -m voice_assistant
```

如果看到 "应用已启动！" 消息，说明安装成功。

## 常见问题

### Q: 提示找不到模块

**A**: 确保已激活虚拟环境，并正确安装了所有依赖。

### Q: Ollama 连接失败

**A**: 确保 Ollama 服务正在运行。可以在命令提示符中运行 `ollama serve` 启动服务。

### Q: 语音识别不工作

**A**: 
1. 检查麦克风权限
2. 确保 Whisper 模型已正确下载
3. 查看日志文件获取详细错误信息

### Q: 邮件连接失败

**A**: 
1. 检查邮箱服务器地址和端口
2. 确认使用了正确的密码（Gmail 需要应用专用密码）
3. 检查防火墙设置

## 下一步

安装完成后，请阅读 [使用指南](USAGE.md) 了解如何使用应用。
