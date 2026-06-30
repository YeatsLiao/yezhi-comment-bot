# Hermes Agent 14万星：AI助手开始自我进化

![数字大脑网络](https://images.unsplash.com/photo-1531746790731-6c087fecd65a?w=1200)

---

OpenRouter的榜单变天了。

5月9日，一个名叫Hermes Agent的开源项目以单日2710亿Token的消耗量，把长期霸榜的OpenClaw挤到了第二。这不是刷数据，是实打实的用户用量——累计Token消耗已经突破6.37万亿。

更夸张的是它的GitHub增速：2月25日发布，现在14万星。3个月，13个重大版本，864次提交，588个合并请求。

## 会自己写技能的AI

用过ChatGPT的人都知道最头疼的事：聊到后面忘了前面，每次新开对话都要重新解释背景。

Hermes解决了这个问题，而且解决得很彻底。它有一套四层记忆架构：

- **Prompt记忆**（热）：当前对话的上下文快照
- **会话存档**（温）：SQLite数据库存储所有历史对话，支持全文搜索
- **外部提供者**（冷）：可选集成Mem0、Honcho等长期记忆服务
- **程序性技能**（核心）：自动生成可复用的技能文件

最狠的是第四层。Hermes完成复杂任务后，会自动生成一个SKILL.md文件，记录完整的处理流程。下次遇到类似任务，直接加载技能，还能根据新情况持续优化。

有用户实测：连续使用一个月后，同类任务的工具调用次数从20多次压缩到8-10次。

## 不是RAG，是自主学习

很多人把Hermes的记忆系统当成RAG（检索增强生成），其实完全不是一回事。

RAG是从数据库里检索相关片段，拼到提示词里。Hermes的技能是程序性的——它记录的是"怎么做"，不是"是什么"。

举个例子：你让Hermes搭建一个React+TypeScript项目。它做完后生成一个技能文件，里面包含：
- 确切的命令顺序
- 文件夹结构
- 常见错误和修复方法
- 你个人的偏好设置（比如喜欢用Vite而不是CRA）

下次再要搭React项目，Hermes不会重新推理，而是直接执行技能。执行过程中遇到新情况，再更新技能文件。

这才是真正的"越用越聪明"。

## OpenClaw vs Hermes：两条路线

OpenClaw和Hermes代表了AI Agent的两个方向。

OpenClaw走"广度"路线：50+消息平台、44000+社区技能、最大化集成覆盖。你想在哪用AI，它都能接入。

Hermes走"深度"路线：20个平台、自主技能生成、持续自我优化。它不关心覆盖多少场景，只关心在你常用的场景里做到最好。

从OpenRouter的数据看，开发者正在用脚投票。Hermes的日Token消耗已经超过OpenClaw，增速还在加快。

## 为什么是现在

Hermes的爆发不是偶然。

2026年的AI行业，模型能力已经卷到头了。GPT-5、Claude 4、Gemini 2——各家大模型的差距越来越小，单纯"更聪明"已经不够打动人。

下一个战场是"更懂你"。谁能记住用户的习惯、偏好、历史上下文，谁就能赢得开发者。

Hermes的 bets 很简单：AI Agent不应该是 Stateless 的聊天机器人，而应该是 Persistent 的系统——运行时间越长，对你的价值越大。

![AI技术抽象](https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1200)

## 这意味着什么

如果Hermes的模式被验证，整个AI Agent的架构都要重写。

现在的Agent大多是" Stateless 服务"：接收请求、处理、返回、忘掉。Hermes证明，Agent可以是" Stateful 应用"：持续运行、持续学习、持续积累价值。

这对开发者是好消息：你不需要再反复解释同一个需求。对AI公司也是好消息：用户粘性会大幅提升。

但这也带来新问题：隐私怎么保护？技能文件怎么迁移？不同用户的技能能不能共享？

这些问题没有标准答案。但至少，Hermes把"自我进化的AI"从科幻变成了现实。

---

*参考来源：*
- [GitHub 5月热点：Claude Code生态大爆发](https://blog.csdn.net/wang_yu_shun/article/details/161062517)，CSDN，2026年5月29日
- [What Is Hermes Agent? Nous Research's Self-Improving AI Framework](https://techjacksolutions.com/ai-tools/hermes/hermes-breakdown/)，TechJack Solutions，2026年5月14日
- [OpenClaw vs Hermes Agent: Why Nous Research's Self-Improving Agent Now Leads OpenRouter's Global Rankings](https://www.marktechpost.com/2026/05/10/openclaw-vs-hermes-agent-why-nous-researchs-self-improving-agent-now-leads-openrouters-global-rankings/)，MarkTechPost，2026年5月10日
- [反超龙虾!HermesAgent登顶全球](http://m.toutiao.com/group/7638149400904073755/)，今日头条，2026年5月

<small>本文配图均来自Unsplash，遵循免费使用授权。</small>
