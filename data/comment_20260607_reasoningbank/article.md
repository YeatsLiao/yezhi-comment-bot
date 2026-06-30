# Google给Agent装了本错题本

![封面](cover.jpg)

Google最近开源了一个叫ReasoningBank的东西，说白了就是让Agent学会记笔记——而且专门记自己是怎么搞砸的。

这事听起来不性感，但数据很硬：在软件工程基准测试上，装了这套记忆系统的Agent，成功率比 baseline 高了34.2%，交互步骤还少了16%。不是模型变大了，不是训练数据变多了，就是加了个错题本。

## 为什么现有的Agent像金鱼

现在的Agent有个通病：做完任务就忘。你让它查个"首次购买日期"，它盯着"Recent Orders"表格就报了最近一笔，完全没看见旁边还有个"View All"。你纠正完，第二天换个人问同样的问题，它犯一模一样的错。

Google Research在WebArena测试里测过，没有记忆的Agent在多网站任务上成功率只有40.5%。不是模型不够聪明，是它根本不从经验里学习。

市面上也不是没有记忆方案。Trajectory Memory存完整操作记录，Workflow Memory只存成功案例。但这俩有个共同毛病：它们记的是"做了什么"，不是"为什么这么做"，更不是"下次怎么避免搞砸"。

就像一个学生抄了一整本笔记，但从不总结错题。

![电路板与大脑](https://images.unsplash.com/photo-1677442135136-760c813028c0?w=1200)

## 错题本长什么样

ReasoningBank的核心设计很简洁：每次任务结束，Agent自己评判刚才干得怎么样。成功了，提炼一条可复用的策略；失败了，提炼一条预防性教训。然后存进一个结构化记忆库。

每条记忆就三行：

- Title：策略名称，比如"先验证页面标识再点Load More"
- Description：一句话说清什么时候用
- Content：具体怎么做，为什么上次栽了

关键是抽象层次。它既不存原始点击序列（太具体，换个页面就废了），也不提炼成"要认真仔细"这种废话。它存的是策略级知识—— transferable reasoning patterns，能在相似场景里复用的推理模式。

Google用了gemini-embedding-001做检索，新任务进来先搜相关记忆，把最匹配的一条塞进提示词里。Agent带着"上次在这栽过"的觉悟去干活，犯错率自然下来。

## 从失败里挖金子

ReasoningBank最反常识的设计，是主动从失败里提取价值。

传统记忆系统几乎只记成功案例，失败就当噪音扔了。但Google团队发现，失败的信息密度往往比成功高。成功可能靠运气，失败却实打实暴露了策略的边界条件和陷阱。

举个例子。Agent在网页浏览时掉进了无限滚动陷阱，传统系统记录"任务失败"就完了。ReasoningBank会提炼出这样一条记忆：

> 遇到"Load More"别急着点。先检查页面URL或标题变没变，确认自己没在循环加载里打转。

这种"预防性知识"构成了Agent的战略护栏。WebArena Admin子集测试里，ReasoningBank成功率51.1%，只存成功案例的AWM是46.7%。4.4%的差距，在真实业务里就是每100次任务多完成4-5个，换算成客服、运维、编程场景，直接就是钱。

更扎心的是，AWM在跨网站知识的Multi子集上，性能反而从44.1%掉到40.8%。说明只记成功案例的记忆，泛化能力是有硬伤的。

![代码编辑器](https://images.unsplash.com/photo-1619410283995-43d9134e7656?w=1200)

## 测试时扩展的第三条路

ReasoningBank还搭了个叫MaTTS的模块，Memory-aware Test-Time Scaling。

测试时扩展（TTS）在数学推理里已经验证过了：给模型更多推理时间，多跑几次选最优答案。但Agent场景里，传统TTS有个巨大浪费——探索过程中的轨迹全扔了，只留最终答案。

MaTTS的思路是：这些被扔掉的轨迹，恰恰是记忆提炼的富矿。

具体做法是在测试时并行跑多次尝试，生成大量多样化的成功和失败轨迹。这些轨迹提供了丰富的对比信号——A为什么成了B为什么栽了——从而让记忆提炼的质量大幅提升。

Google把这叫"记忆驱动的经验扩展"，跟参数扩展、数据扩展并列，当成Agent系统的第三条扩展维度。实验显示MaTTS在SWE-Bench上带来了最高34.2%的相对提升。

这意味着Agent不仅更聪明，还更高效。它不需要反复试探，因为记忆已经告诉它"这条路之前走过，不通"。

## 开源了，但企业用还得再想想

ReasoningBank已经开源（github.com/google-research/reasoning-bank），代码围绕WebArena和SWE-Bench两个基准搭了完整流水线。记忆以JSONL格式存，人类可读、可编辑、可审计，不是黑盒权重更新。

这体现了Google Research的务实：与其追求端到端梯度优化，不如做个可解释、可干预的记忆系统。对企业部署来说，这确实是更现实的路径。

但有几个坑还没填。

记忆膨胀是第一个。当前实现简单追加，没有遗忘机制。跑了几万个任务之后，检索质量和推理效率怎么保持？

评判噪声是第二个。LLM-as-a-judge的自我评估并不总是准的，虽然论文说对噪声有一定鲁棒性，但长期累积效应没人测过。

记忆整合是第三个。相似策略要不要合并成更通用的规则？这需要更复杂的整合算法，论文里明确说留待未来工作。

最后一个问题更微妙：如果Agent从恶意构造的失败案例里学到了有害策略怎么办？记忆注入的安全过滤，目前还是空白。

![黑色电路板](https://images.unsplash.com/photo-1576400883215-7083980b6193?w=1200)

## 

ReasoningBank的真正价值，不是让Agent成功率高了几个点。是它证明了：智能的关键不是记住所有细节，而是提炼可复用的策略；不是只庆祝成功，而是从失败里汲取教训。

当Agent开始拥有"长期记忆"，它就不再是每次调用都从零开始的工具，而是一个能从经验里成长的学习者。

Google给它取名叫Bank，挺准的。存进去的不是数据，是经验。取出来的不是回忆，是智慧。

---

## 参考来源

1. [ReasoningBank: Enabling agents to learn from experience](https://www.research.google/blog/reasoningbank-enabling-agents-to-learn-from-experience/)，Google Research Blog，2026年4月21日
2. [ReasoningBank: Scaling Agent Self-Evolving with Reasoning Memory](https://arxiv.org/abs/2509.25140)，arXiv，ICLR论文
3. [从失败中学习：Google 提出 ReasoningBank 让 LLM 智能体真正"吃一堑长一智"](https://www.51cto.com/article/827306.html)，51CTO，2025年10月16日
4. [Google's ReasoningBank: How AI Agents Learn on the Fly](https://legacy.thenextgentechinsider.com/googles-reasoningbank-how-ai-agents-learn-on-the-fly/)，The Next Gen Tech Insider

<small>本文配图均来自Unsplash，遵循免费使用授权。</small>
