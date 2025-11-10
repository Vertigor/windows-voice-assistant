# LLM 配置指南

本文档详细说明如何配置不同的 LLM 服务提供商。

## 支持的提供商

Windows Voice Assistant 支持两种类型的 LLM 服务：

1. **Ollama**（本地运行）
2. **OpenAI 兼容 API**（云服务）

## Ollama 配置（推荐）

### 优势
- ✅ 完全本地运行，保护隐私
- ✅ 无需 API Key
- ✅ 无使用次数限制
- ✅ 响应速度快（本地网络）

### 安装步骤

1. **下载 Ollama**
   - 访问：https://ollama.com/download
   - 下载 Windows 版本安装程序
   - 运行安装程序

2. **下载模型**
   ```bash
   ollama pull qwen2.5:3b
   ```

3. **启动服务**
   ```bash
   ollama serve
   ```

### 配置示例

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

### 推荐模型

| 模型 | 大小 | 特点 | 适用场景 |
|------|------|------|---------|
| `qwen2.5:3b` | ~2GB | 平衡性能和速度 | 推荐，日常使用 |
| `qwen2.5:7b` | ~4.7GB | 更高准确率 | 高性能机器 |
| `llama3.2:3b` | ~2GB | 英文优秀 | 英文环境 |
| `gemma2:2b` | ~1.6GB | 轻量快速 | 低配置机器 |

## OpenAI 兼容 API 配置

### 优势
- ✅ 无需本地部署
- ✅ 模型性能强大
- ✅ 支持多种提供商

### 劣势
- ❌ 需要 API Key
- ❌ 有使用成本
- ❌ 需要网络连接

---

## 1. OpenAI 官方

### 获取 API Key

1. 访问：https://platform.openai.com/api-keys
2. 登录账户
3. 创建新的 API Key
4. 复制并保存

### 配置示例

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

### 推荐模型

- `gpt-3.5-turbo`: 性价比高，速度快
- `gpt-4o-mini`: 更强性能，成本适中
- `gpt-4o`: 最强性能，成本较高

---

## 2. DeepSeek（推荐）

### 优势
- 🌟 价格便宜（比 OpenAI 便宜 90%+）
- 🌟 中文理解优秀
- 🌟 API 兼容 OpenAI

### 获取 API Key

1. 访问：https://platform.deepseek.com/
2. 注册账户
3. 在控制台创建 API Key

### 配置示例

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

---

## 3. 通义千问（阿里云）

### 获取 API Key

1. 访问：https://dashscope.aliyun.com/
2. 登录阿里云账户
3. 开通 DashScope 服务
4. 创建 API Key

### 配置示例

```json
{
  "llm": {
    "provider": "openai",
    "model": "qwen-turbo",
    "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "api_key": "sk-...",
    "temperature": 0.7,
    "max_tokens": 500
  }
}
```

### 可用模型

- `qwen-turbo`: 快速响应
- `qwen-plus`: 平衡性能
- `qwen-max`: 最强性能

---

## 4. 智谱 AI（GLM）

### 获取 API Key

1. 访问：https://open.bigmodel.cn/
2. 注册账户
3. 创建 API Key

### 配置示例

```json
{
  "llm": {
    "provider": "openai",
    "model": "glm-4",
    "api_base": "https://open.bigmodel.cn/api/paas/v4",
    "api_key": "...",
    "temperature": 0.7,
    "max_tokens": 500
  }
}
```

---

## 5. 月之暗面（Moonshot）

### 获取 API Key

1. 访问：https://platform.moonshot.cn/
2. 注册账户
3. 创建 API Key

### 配置示例

```json
{
  "llm": {
    "provider": "openai",
    "model": "moonshot-v1-8k",
    "api_base": "https://api.moonshot.cn/v1",
    "api_key": "sk-...",
    "temperature": 0.7,
    "max_tokens": 500
  }
}
```

---

## 配置参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `provider` | LLM 提供商，`ollama` 或 `openai` | `ollama` |
| `model` | 模型名称 | `qwen2.5:3b` |
| `api_base` | API 基础 URL | `http://localhost:11434` |
| `api_key` | API 密钥（OpenAI 类型必需） | 空 |
| `temperature` | 生成温度，0-1 之间，越高越随机 | `0.7` |
| `max_tokens` | 最大生成 token 数（仅 OpenAI 类型） | `500` |

## 性能对比

| 提供商 | 延迟 | 成本 | 中文能力 | 隐私 | 推荐度 |
|--------|------|------|---------|------|--------|
| Ollama | ⭐⭐⭐⭐⭐ | 免费 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| DeepSeek | ⭐⭐⭐⭐ | 极低 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| OpenAI | ⭐⭐⭐ | 高 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| 通义千问 | ⭐⭐⭐⭐ | 中 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 智谱 GLM | ⭐⭐⭐⭐ | 中 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Moonshot | ⭐⭐⭐⭐ | 中 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |

## 推荐方案

### 个人用户
**推荐：Ollama + qwen2.5:3b**
- 完全免费
- 保护隐私
- 性能足够

### 企业用户
**推荐：DeepSeek**
- 成本极低
- 中文优秀
- API 稳定

### 高性能需求
**推荐：OpenAI gpt-4o**
- 性能最强
- 理解准确
- 响应稳定

## 故障排除

### Ollama 连接失败

**问题**: `连接被拒绝` 或 `无法连接到 Ollama`

**解决方案**:
1. 确保 Ollama 服务正在运行：`ollama serve`
2. 检查端口是否被占用
3. 确认 `api_base` 配置正确

### OpenAI API 调用失败

**问题**: `401 Unauthorized` 或 `API Key 无效`

**解决方案**:
1. 检查 API Key 是否正确
2. 确认 API Key 有足够余额
3. 检查 `api_base` 是否正确

### 响应超时

**问题**: `请求超时`

**解决方案**:
1. 检查网络连接
2. 尝试更换模型
3. 增加超时时间（修改代码中的 `timeout` 参数）

## 切换提供商

您可以随时在配置文件中切换 LLM 提供商，无需重新安装。只需：

1. 编辑配置文件：`%APPDATA%\VoiceAssistant\config.json`
2. 修改 `llm` 部分的配置
3. 重启应用

应用会自动使用新的配置。
