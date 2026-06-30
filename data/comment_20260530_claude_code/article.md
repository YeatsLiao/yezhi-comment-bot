# Claude Code占GitHub 4%提交：AI正在悄悄接管代码

> 来源: SemiAnalysis / claudescode.dev | 热点: Claude Code占GitHub 4%提交
> 日期: 2026年5月30日
> 封面: cover.jpg

![代码屏幕](inline_代码屏幕.jpg)

---

一个数据让我停下了手里的咖啡杯。

根据SemiAnalysis的研究，**Claude Code已经占GitHub全部公开代码提交的4%**。不是4个，是4%。每25次提交里，就有一次是Anthropic的AI写的。

更离谱的是，这个数字还在以每周8%的速度增长。按这个节奏，年底可能冲到20%。

## 15.8 million commits，90天

有个叫claudescode.dev的社区仪表盘，专门追踪Claude Code在GitHub上的公开足迹。过去90天的数据：

- **1580万次提交**
- **307亿行代码**
- **84.4万个活跃仓库**
- **每周新增11.4万个仓库**

什么概念？GitHub上每天大约有300万次公开提交，Claude Code每天贡献13.5万次。而且这个数字每61天翻一倍。

## 90%的仓库没人用？那又怎样

Hacker News上有条热帖炸了："90%的Claude代码都进了没人用的仓库（<2星）"。

评论区最高赞的回复很冷静："98%的GitHub仓库本来就没超过2星。"

这才是真相。GitHub早就不是开源项目的展示橱窗了，它变成了开发者的**个人草稿本**——存一些自己用的小工具、自动化脚本、一次性解决方案。

Claude Code让这种"为自己写代码"的成本趋近于零。以前写一个个人记账工具要半天，现在几分钟。这些代码不需要Star，它们只需要解决一个人的具体问题。

## TypeScript占34.8%，Python 18.9%

语言分布很有意思：

- **TypeScript 34.8%**
- **Python 18.9%**
- **JavaScript 10.2%**

全是Web和自动化语言。这说明Claude Code的主力用户不是在做底层系统，而是在做**实用工具**——网页、脚本、数据处理。

最活跃的单个仓库，90天内快2万次提交。平均每天200+次提交，这节奏人类开发者根本做不到。

## MCP：AI的USB-C接口

Claude Code能这么猛，背后有个关键基础设施：**MCP（Model Context Protocol）**。

这是Anthropic 2024年11月开源的协议，现在月下载量已经冲到**9700万次**，支持1万+公开服务器。Google、Microsoft、AWS、OpenAI全都支持。

简单说，MCP就是AI和外部工具之间的"USB-C"。以前每个AI模型连每个工具都要写定制代码，现在写一次MCP服务器，所有AI都能用。

有个技术团队说，他们从自定义函数调用切到MCP后，每个新工具的集成时间从2天降到4小时。

## Anthropic内部：90-95%的代码是AI写的

Anthropic的CPO Mike Krieger说，**Claude Code本身的代码，90-95%是Claude Code写的**。

Boris Cherny（Claude Code负责人）更激进："从11月起，我没手写过一行代码。"

当然，有分析师质疑这个数字。Redwood Research估计，Anthropic实际merged的代码里，AI写的比例大概是50%。但即便如此，这也是个惊人的数字。

![程序员工作](inline_程序员工作.jpg)

## 这意味着什么

4%不是终点，是起点。

如果年底真的冲到20%，软件开发的定义就要变了。不再是"人写代码，AI辅助"，而是"AI写代码，人做决策"。

GitHub Stars会变得毫无意义。真正重要的指标会变成：这段代码解决了什么问题？谁在用它？

对开发者来说，好消息是：写代码的门槛没了。坏消息是：写代码的价值也在消失。

未来的工程师，核心竞争力不再是语法熟练度，而是**定义问题**和**判断结果**的能力。

---

## 参考来源

1. [Claude Code just hit 15M commits — 90% go to repos nobody uses](https://aiforautomation.io/news/2026-03-26-claude-code-15-million-commits-90-percent-repos-nobody-uses)，2026年3月26日
2. [4% Of GitHub Commits Are Now Made By Claude Code: SemiAnalysis Report](https://officechai.com/ai/4-of-github-commits-are-now-made-by-claude-code-semianalysis-report/)，2026年2月7日
3. [MCP at 97 Million Installs: The Protocol That Became AI's TCP/IP](https://luonghongthuan.com/en/blog/mcp-97-million-linux-foundation-ai-infrastructure/)，2026年4月7日

## 图片说明

本文配图均来自Unsplash，遵循免费使用授权。

---

*叶芝说 · 科技评论*
*2026年5月30日*
