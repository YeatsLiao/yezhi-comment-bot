# 叶芝说·实时评论AI助手

> 每天自动抓取科技热点，生成个性化锐评，发布到公众号

## 功能特性

- 🔥 **热点自动抓取**：微博热搜 + 36氪/新闻API，聚焦科技/软件行业
- 🤖 **AI评论生成**：支持 OpenAI GPT / Claude 双模型
- 📱 **公众号自动发布**：支持草稿箱模式（人工审核后发布）
- 🎨 **风格适配**：基于个人风格生成观点鲜明的锐评
- ⏰ **定时调度**：每天定时自动执行

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置

```bash
cp config/config.example.yaml config/config.yaml
# 编辑 config.yaml，填入你的API密钥和公众号配置
```

### 3. 运行

```bash
# 单次运行
python -m src.main

# 定时运行（每天早8点）
python -m src.main --schedule
```

## 项目结构

```
yezhi-comment-bot/
├── config/
│   ├── config.example.yaml   # 配置模板
│   └── config.yaml           # 你的配置（需自行创建）
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
│   │   ├── openai_gen.py     # OpenAI生成器
│   │   └── claude_gen.py     # Claude生成器
│   ├── publisher/            # 发布模块
│   │   ├── __init__.py
│   │   └── wechat_mp.py      # 公众号发布
│   ├── scheduler.py          # 定时任务
│   └── utils.py              # 工具函数
├── data/                     # 数据目录
│   └── published.json        # 已发布记录
├── logs/                     # 日志目录
├── requirements.txt
└── README.md
```

## 配置说明

### 必填配置

| 配置项 | 说明 |
|--------|------|
| `ai.openai.api_key` | OpenAI API密钥 |
| `ai.claude.api_key` | Claude API密钥（二选一） |
| `wechat_mp.app_id` | 公众号AppID |
| `wechat_mp.app_secret` | 公众号AppSecret |

### 可选配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `ai.default_model` | 默认AI模型 | `openai` |
| `scheduler.hour` | 每日执行时间（小时） | `8` |
| `scheduler.draft_mode` | 草稿箱模式 | `true` |
| `comment.comments_per_run` | 每次生成评论数 | `1` |

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

## 注意事项

1. **公众号发布**：需要已认证的服务号，并获取API权限
2. **API费用**：OpenAI/Claude API调用会产生费用，建议设置用量上限
3. **内容审核**：建议开启草稿箱模式，人工审核后再发布
4. **热点去重**：系统会自动记录已发布热点，避免重复评论

## License

MIT
