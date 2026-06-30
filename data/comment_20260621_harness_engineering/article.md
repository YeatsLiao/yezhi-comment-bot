# 当程序员不再写代码：Harness Engineering正在重新定义"开发"

![封面](cover.jpg)

2026年2月，OpenAI发了一篇博文，标题很平淡：*Harness engineering: leveraging Codex in an agent-first world*。

四个月后，这篇文章重新杀回Hacker News热榜，286个赞，200多条讨论。原因不是OpenAI又吹了什么牛，而是6月4日GitHub发布了Agent Tasks REST API，5月28日Anthropic发布了Claude Opus 4.8，Claude Code更新了动态Agent工作流——生产级工具链终于追上了OpenAI的内部实验。

"Harness Engineering"这个概念，从一家公司的内部实践，变成了全行业可复制的工程方法论。

它的核心主张只有一句话：**人不写代码了，人设计AI写代码的环境。**

![代码屏幕](https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=1200&q=80)

## 100万行代码，零手写

先说OpenAI干了什么。

一个3人团队（后来扩到7人），用5个月时间，从空仓库开始，造了一个有真实用户的产品。代码量约100万行，合并了约1500个PR。平均每个工程师每天合并3.5个PR。

这个吞吐量意味着什么？一个正常的人类开发者，一天能合并0.5到1个PR就算高效。OpenAI的团队做到了3.5个，而且随着团队扩大，吞吐量还在上升——这直接颠覆了布鲁克斯定律（"往延期的项目加人只会更慢"）。唯一能颠覆布鲁克斯定律的条件就是：加的人不是在写代码。

他们确实没有写任何代码。整个产品——应用逻辑、测试、CI配置、文档、监控、内部工具——全部由Codex Agent生成。人类的唯一工作方式是：用自然语言描述任务，Agent打开PR，Agent自己review自己的代码，Agent修复build失败，直到所有Agent reviewer满意，才通知人类。

他们管这个叫"Ralph Wiggum Loop"——Agent审查Agent，循环往复，直到收敛。

人类review变成了可选项，不是必选项。

## 围栏比代码重要

这个实验最有趣的部分不是"AI能写代码"——这已经是2026年的常识了。最有趣的部分是：**为了让AI写好代码，人类花了大量精力构建"围栏"**。

OpenAI把这个围栏叫做Harness（马具/挽具）。它包含四个部分：

**第一，给Agent一张地图，而不是一本百科全书。**

他们试过写一个巨大的`AGENTS.md`文件，把所有规则塞进去。失败了。原因很直觉：上下文窗口是稀缺资源，1000行的指令手册会挤占任务本身的空间。Agent要么遗漏关键约束，要么对所有规则一视同仁，最后什么都没遵守。

解决方案：`AGENTS.md`只写100行，作为目录索引，指向`docs/`目录下的详细文档。Agent从一个小入口开始，按需深入。他们管这叫"渐进式披露"（progressive disclosure）。

**第二，用机械规则强制执行架构。**

每个业务领域都有固定的分层依赖方向：Types → Config → Repo → Service → Runtime → UI。跨领域关注点（认证、遥测、特性开关）只能通过一个叫Providers的接口进入。其他路径全部禁止。

这些规则不是写在文档里靠人遵守的，而是写在自定义linter和结构测试里，由CI强制执行的。Lint的错误信息本身就是给Agent看的修复指令——不是"第42行有错误"，而是"Repo层不能依赖Service层，把调用移到Service/里，或者通过Provider暴露"。

**第三，把"黄金原则"变成自动垃圾回收。**

Agent会复制现有模式，包括坏模式。OpenAI团队最初每周花20%的时间手动清理"AI垃圾"。不可持续。

解决方案：把清理规则编码进仓库，后台Codex任务定期扫描偏差，自动打开重构PR。他们把技术债比作高利贷："几乎总是值得持续偿还，而不是拖延。"

**第四，仓库是Agent的唯一信息源。**

Slack里的讨论、Google Docs里的设计文档、某人脑子里的隐性知识——对Agent来说都不存在。只有仓库里的、版本化的、可发现的文档才是"真实的"。

这个原则倒逼了一个有趣的工程实践：所有决策必须沉淀到仓库里，否则Agent无法利用。这跟"给新员工写入职文档"的逻辑完全一样。

![芯片电路板](https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&q=80)

## 我的判断：这不是"替代程序员"，是"程序员的工作上移了一层"

很多人看到Harness Engineering的第一反应是"程序员要失业了"。

我认为恰恰相反。

仔细看OpenAI团队的日常：他们在设计分层架构、编写自定义linter、构建per-worktree的 observability stack、把Chrome DevTools Protocol接入Agent runtime、设计Agent间的review循环、管理技术债的自动清理流程。这些工作需要的是**更高级的工程判断力**，而不是更少的工程能力。

传统程序员的核心技能是"写代码"。Harness Engineer的核心技能是"设计系统"——设计一个让AI Agent能够安全、高效、可持续地写代码的系统。

这不是技能退化，是技能上移。就像编译器发明之后，程序员不再写汇编了，但没有人会说"程序员失业了"——他们只是把注意力从寄存器分配转移到了算法设计。

但这里有一个残酷的分化。

**能完成这个转移的程序员，效率会提升5-10倍。** OpenAI的数据是3.5 PRs/工程师/天，大约是正常人类吞吐的5-10倍。而且这个倍数会随着工具链的成熟而继续增长。

**不能完成这个转移的程序员，确实会面临压力。** 当你的竞争对手用AI Agent一天合并3个PR，而你还在手写代码一天合并0.5个，成本差距是6倍。企业不需要裁人，只需要不再扩招，差距就会在两三年内拉大到不可逆转。

真正的竞争不是"人vs AI"，而是"会用AI的人 vs 还在手写代码的人"。

## 行为围栏：还没人解决

Thoughtworks的Birgitta Böckeler在Martin Fowler的博客上写了一篇非常尖锐的分析。她把Harness分成两类：

**结构围栏**（structural harness）：约束代码怎么组织、怎么分层、怎么lint。OpenAI已经解决了。

**行为围栏**（behavior harness）：验证代码是否真的做了用户需要的事。还没人解决。

这个区分非常关键。一个代码库可以完美通过所有linter、严格遵守所有分层规则、依赖图毫无瑕疵，但仍然在解决错误的问题。Agent写的测试也堵不上这个漏洞——因为写实现和写测试的是同一个Agent，它们共享同样的盲区。

Böckeler提出了一个有用的概念框架：**引导**（guides，事前控制，比如AGENTS.md、架构文档）和**传感器**（sensors，事后反馈，比如linter、类型检查、测试套件）。OpenAI的Harness在结构问题上引导和传感器都很强。但在行为问题上，传感器还是空的。

这意味着什么？意味着2026年的Harness Engineering能保证代码"写得对"，但不能保证代码"做对了"。后者仍然需要人类的判断力——至少目前如此。

我认为这个缺口不会持续太久。方向已经很明确：端到端的用户流程测试、金丝雀部署、生产环境的真实反馈信号。这些"行为传感器"正在被快速工程化。但今天 adoption Harness Engineering的团队必须清楚：结构围栏能买你速度，买不了你正确性。

## MCP为什么被放弃了

一个容易被忽略的细节：OpenAI在构建Codex App Server时，先试了MCP协议，然后放弃了。

原因：MCP的语义无法干净地表达暂停审批、流式工作区diff、更丰富的会话状态。他们最终用了自研的JSON-RPC-lite协议，定义了三个原语：Items（带生命周期事件的原子单元）、Turns（一次Agent工作的输入到输出）、Threads（持久化的对话容器，可分叉、可恢复）。

这对MCP生态是个信号。MCP在"Agent调工具"的场景下很好用，但当Agent需要深度集成到IDE、需要复杂的会话管理、需要暂停/恢复/分叉时，它的表达力不够。

Anthropic主导的MCP和OpenAI自研的App Server协议，可能会在"Agent开发工具"这个赛道上形成新的分化。上次我们聊MCP+A2A时，我说A2A会赢但MCP不会死。现在看来，MCP的生存空间可能比我想的更窄。

![AI机器人](https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=1200&q=80)

## 写在最后

Harness Engineering的本质，是把软件工程的核心约束从"代码质量"转移到了"环境质量"。

这个转移一旦发生，就不会回去了。就像一旦你用了Git就回不去SVN，一旦你用了CI/CD就回不去手动部署，一旦你让Agent一天合并3个PR，你就回不去一天0.5个。

但这也意味着，**2026年最稀缺的工程师，不是最会写代码的人，而是最会设计环境的人**。

理解分层架构、知道该在哪些边界上放linter、能把模糊的产品需求转化为Agent可执行的约束、能判断哪些技术债值得自动清理哪些需要人工介入——这些能力在AI时代不是贬值了，而是升值了。

只不过，拥有这些能力的人，可能不再叫自己"程序员"了。

---

## 参考来源

1. [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/)，OpenAI Blog，2026-02-11
2. [Harness Engineering: What OpenAI Learned Building a Product with Zero Handwritten Code](https://daita.io/en/blog/harness_engineering_zero_handwritten_code)，Daita Blog，2026-04-22
3. [Harness engineering for coding agent users](https://martinfowler.com/articles/harness-engineering.html)，Birgitta Böckeler / Martin Fowler，2026
4. [What Is Harness Engineering? OpenAI's Agent-First Codex Playbook (2026)](https://rohitraj.tech/en/notes/what-is-harness-engineering-codex-2026)，Rohit Raj，2026-06-08
5. [Unlocking the Codex harness: how we built the App Server](https://openai.com/index/unlocking-the-codex-harness/)，OpenAI Blog，2026
6. [GitHub Agent Tasks REST API](https://github.blog/changelog/)，GitHub Blog，2026-06-04

<small>本文配图均来自Unsplash，遵循免费使用授权。</small>
