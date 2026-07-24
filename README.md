# 叶芝说·实时评论AI助手

> 每天自动抓取科技热点，生成个性化锐评，发布到公众号

## 项目定位

本项目是一个**AI评论生成框架**，提供两种使用模式：

**模式A：AI对话协作（推荐）**
- 你与AI助手对话，由AI完成选题、搜索、写作、配图全流程
- 文章质量高、观点鲜明、可控性强
- 适合对内容质量有要求的个人创作者

**模式B：自动化流水线（框架设计中）**
- 定时抓取热点 → AI自动生成 → 自动发布到公众号
- 代码框架已搭建，部分模块需要自行接入
- 适合追求效率、能接受自动输出质量的用户

## 功能特性

- 🔥 **热点自动抓取**：微博热搜 + 36氪/新闻API，聚焦科技/软件行业
- 🤖 **AI评论生成**：支持 OpenAI / Claude / DeepSeek / 阿里Qwen / 字节豆包 / Gemini 等主流模型
- 📱 **公众号自动发布**：支持草稿箱模式（人工审核后发布）
- 🎨 **风格适配**：基于个人风格生成观点鲜明的锐评，支持热点评论模式和技术解析模式
- ⏰ **定时调度**：每天定时自动执行

## 模型兼容性

本项目基于 OpenAI SDK 的 `base_url` 机制实现多厂商兼容，**无需修改任何代码**，只需在配置文件中切换 `base_url` 和 `model` 名称。

| 厂商 | base_url | 推荐模型 | 备注 |
|:---|:---|:---|:---|
| **OpenAI** | `https://api.openai.com/v1` | `gpt-4o` | 官方，质量最高 |
| **Claude** | `https://api.anthropic.com/v1` | `claude-sonnet-4-20250514` | 原生支持，代码能力强 |
| **DeepSeek** | `https://api.deepseek.com/v1` | `deepseek-chat` | 国产，性价比高 |
| **阿里Qwen** | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-max` | 通义千问，中文强 |
| **字节豆包** | `https://ark.cn-beijing.volces.com/api/v3` | `doubao-pro-32k` | 火山引擎，低成本 |
| **Gemini** | `https://generativelanguage.googleapis.com/v1beta/openai/` | `gemini-1.5-pro` | Google，长上下文 |
| **本地Ollama** | `http://localhost:11434/v1` | `llama3.1:8b` | 本地部署，零成本 |

> 💡 **切换模型只需两步**：改 `base_url` + 改 `model` 名称，Python代码零改动。

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/YeatsLiao/yeats-tech-skill.git
cd yeats-tech-skill
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置

```bash
cp config/config.example.yaml config/config.yaml
# 编辑 config.yaml，填入你的API密钥和偏好配置
```

配置文件中已内置各大模型厂商的示例，取消注释即可使用：

```yaml
ai:
  default_model: "deepseek"  # 切换默认模型
  
  # DeepSeek 示例（取消注释并填入api_key即可使用）
  # deepseek:
  #   api_key: "sk-your-deepseek-key"
  #   model: "deepseek-chat"
  #   base_url: "https://api.deepseek.com/v1"
```

### 4. 运行

```bash
# 单次运行
python -m src.main

# 定时运行（每天早8点）
python -m src.main --schedule
```

## 项目结构

```
yeats-tech-skill/
├── config/
│   ├── config.example.yaml   # 配置模板（含多厂商示例）
│   └── config.yaml           # 你的配置（需自行创建，git忽略）
├── src/
│   ├── __init__.py
│   ├── main.py               # 主入口
│   ├── fetcher/              # 热点抓取模块
│   │   ├── __init__.py
│   │   ├── base.py           # 基类
│   │   ├── weibo.py          # 微博热搜
│   │   └── news.py           # 新闻API
│   ├── generator/            # 评论生成模块
│   │   ├── __init__.py
│   │   ├── base.py           # 基类
│   │   ├── openai_gen.py     # OpenAI兼容生成器（通杀所有厂商）
│   │   └── claude_gen.py     # Claude原生生成器
│   ├── publisher/            # 发布模块
│   │   ├── __init__.py
│   │   └── wechat_mp.py      # 公众号发布
│   ├── scheduler.py          # 定时任务
│   └── utils.py              # 工具函数
├── data/                     # 数据目录（文章、配图、已发布记录）
├── logs/                     # 日志目录
├── requirements.txt
├── README.md
└── SKILL.md                  # AI助手Prompt规范（技术解析模式+热点评论模式）
```

## 配置详解

### 模型配置（最重要）

在 `config.yaml` 的 `ai` 段落中配置：

```yaml
ai:
  # 默认使用的模型，对应下方的配置块名称
  default_model: "openai"
  
  openai:
    api_key: "sk-your-openai-key"
    model: "gpt-4o"
    base_url: "https://api.openai.com/v1"
    max_tokens: 2000
    temperature: 0.8
```

**如何切换到其他模型？**

只需复制已有配置块，修改名称、base_url和model即可：

```yaml
ai:
  default_model: "deepseek"  # ← 改这里
  
  deepseek:
    api_key: "sk-your-deepseek-key"
    model: "deepseek-chat"
    base_url: "https://api.deepseek.com/v1"
    max_tokens: 2000
    temperature: 0.8
```

**temperature参数建议**：
- `0.6-0.8`：适合评论写作，有一定创造性但不至于天马行空
- `0.3-0.5`：适合技术解析，更稳定、更确定性
- `0.9-1.0`：适合创意发散，但可能输出不可控

### 热点抓取配置

```yaml
hotspot:
  focus_keywords:  # 关注领域关键词
    - "AI"
    - "人工智能"
    - "大模型"
    - "芯片"
    # ... 更多关键词
  
  weibo:
    enabled: true
    api_url: "https://weibo.com/ajax/side/hotSearch"
    max_items: 50
  
  news:
    enabled: true
    provider: "36kr"
    rss_url: "https://rsshub.app/36kr/hot-list"
    max_items: 30
```

### 评论风格配置

```yaml
comment:
  identity_tags:
    - "物联网技术专家"
    - "科技评论员"
    - "10年+科技行业从业者"
  
  style:
    tone: "犀利但不失温度，有深度但不晦涩"
    perspective: "技术专家视角 + 生活观察者视角"
    structure: "观点先行，论据支撑，结尾升华"
    length: "800-1500字"
```

### 公众号配置

```yaml
wechat_mp:
  enabled: true
  app_id: "your-app-id"
  app_secret: "your-app-secret"
  draft_mode: true  # true=存草稿箱人工审核, false=直接发布
```

## 两种写作模式

本项目在 `SKILL.md` 中定义了两种写作模式，AI助手会根据你的指令自动切换：

| 模式 | 触发方式 | 风格特点 | 适用场景 |
|:---|:---|:---|:---|
| **热点评论** | "来一篇" / "来一篇今天的" | 口语化、有观点、有锐度、去AI化 | 日常科技热点评论 |
| **技术解析** | "来一篇技术解析" / "来一篇大厂技术推文" | 分层架构拆解、工程细节、数据验证 | 技术深度文章、大厂博客风格 |

> 详见 `SKILL.md` 中的"双模式工作流"章节。

## 自定义风格

在 `config.yaml` 中修改以下配置来定制你的评论风格：

```yaml
comment:
  identity_tags:
    - "你的身份标签1"
    - "你的身份标签2"
  style:
    tone: "你的语气风格"
    perspective: "你的观察视角"
```

也可以在 `style_samples` 中提供过往评论作为风格参考。

## 当前状态与待完善项

### 已完善的模块

- ✅ 评论生成核心逻辑（`src/generator/`）
- ✅ 多模型兼容架构（OpenAI SDK统一接口）
- ✅ 配置文件体系（`config/`）
- ✅ AI助手Prompt规范（`SKILL.md`，含双模式定义）

### 需要自行接入的模块

- ⚠️ **热点抓取**：微博/新闻API可能变动，需要根据实际情况调整
- ⚠️ **公众号发布**：需要已认证的公众号并获取API权限
- ⚠️ **配图生成**：当前为AI生成封面图，如需接入Stable Diffusion等需自行扩展

## 注意事项

1. **公众号发布**：需要已认证的服务号，并获取API权限
2. **API费用**：各厂商API调用会产生费用，建议设置用量上限
3. **内容审核**：建议开启草稿箱模式，人工审核后再发布
4. **热点去重**：系统会自动记录已发布热点，避免重复评论
5. **SKILL.md**：这是AI助手的核心Prompt规范，直接决定了文章质量，建议根据实际情况持续迭代

## License

MIT
