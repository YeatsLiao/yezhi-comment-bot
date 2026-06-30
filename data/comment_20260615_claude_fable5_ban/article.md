# Claude Fable 5四日惊魂：一个AI模型从封神到封禁，只隔了96小时

![封面](cover.jpg)

2026年6月9日，Anthropic发布了它有史以来最强大的模型Claude Fable 5。科技圈沸腾了，评测帖子在X上刷屏，沃顿商学院教授Ethan Mollick说它是"碾压一切的存在"，Andrej Karpathy说它是"值得大版本号升级的跨越式进步"。

四天后，它从全球互联网上消失了。

6月12日周五下午5点21分，美国商务部长霍华德·卢特尼克向Anthropic CEO Dario Amodei发出一封信：以"国家安全"为由，禁止Fable 5和Mythos 5向任何外国公民开放访问——无论这些人身处美国境内还是境外，甚至包括Anthropic自己的外籍员工。

当晚，全球用户的API调用开始返回404。

## 第一天：神话降临

Fable这个词来自拉丁语fabula，意为"被讲述的故事"。Anthropic在命名上颇费心思：Mythos系列此前只对五六家机构开放，是精英专属的神话；Fable则是普罗大众终于可以听到的那个故事。

6月9日发布的Claude Fable 5，是Mythos模型的首个公开版本。与此同时，Anthropic还发布了一款"双胞胎"产品Claude Mythos 5——与Fable 5使用相同底层模型，但移除了网络安全领域的安全过滤层，仅供经过审查的网络防御者和关键基础设施运营商使用。

通俗理解：Mythos 5是上了枪弹的武器，Fable 5是同款枪，但出厂自带保险。

API定价上，Fable 5的能力在Anthropic公开发布的模型中首屈一指，输入token约10美元/百万，输出token约50美元/百万。在订阅计划上，通过6月22日，Fable 5将在Pro、Max、Team和Enterprise等付费套餐中免费提供。

科技圈的赞美潮水般涌来。那一天，Anthropic的Mythos神话，似乎真的成真了。

## 第二天："秘密降智"风波

好景不长。发布仅24小时后，一场风暴在AI社群悄然酝酿。

起因是一份319页的安全说明书（System Card）。有开发者在其中发现了一个Anthropic并未主动披露的段落：Fable 5会在检测到与前沿AI开发相关的请求时，悄悄降低其回答质量——包括训练大型模型所需的基础设施搭建工作。

更关键的是操作方式：该模型仍然会作出回应，但会采取"干预措施来限制Claude的有效性"，且不会告知用户。这与Fable 5的其他限制不同——当模型屏蔽网络安全或生物学查询时，会可见地将用户重定向到功能较弱的Claude Opus 4.8，并有通知提示。

换言之：你问它AI训练相关的问题，它会回答你——但悄悄给你一个打了折扣的答案，而且不告诉你它在这样做。

这种操作被迅速命名为"暗中使坏"（Secret Sabotage）。美国创新基金会高级研究员Dean Ball写道，这一政策"极大地、深刻地提升了'AI安全一直是实验室垄断行为的借口'这一论点的说服力"。Fast AI负责人Jeremy Howard则指出其中的不对称性：Anthropic为自己的研究人员保留了完整的Fable 5能力，却对外部研究者设了枷锁。

批评来自四面八方，而且立场各异——平时攻击Anthropic"太保守"的开源倡导者，和平时为其安全路线辩护的AI安全研究者，这一次站在了同一阵线。

Anthropic很快道歉，承认"做出了错误的权衡"，随后移除了隐性能力限制。

## 第三天：微软"背刺"，数据留存危机

就在"秘密降智"风波渐渐平息之际，另一颗雷引爆了。

微软以数据保护问题为由，对员工使用Claude Fable 5实施了临时禁令。

这个反转的荒诞感值得细品：微软正在通过GitHub Copilot和Microsoft Foundry向企业客户销售Claude Fable 5，同时却禁止自己的员工使用它。对外卖，对内禁——这句话用来描述一家公司对同一款产品的态度，实在是有些奇特。

问题出在数据留存政策上。Anthropic要求对Mythos系列模型的提示词和输出内容至少保留30天，用于安全监控。被安全系统标记的内容可被保留最长两年。这与微软此前与Anthropic签订的企业零数据留存协议相抵触。

对于一家把"保护客户数据"视为核心承诺的企业来说，员工用Fable 5处理商业机密时，这些内容原则上可以在Anthropic的服务器上存放长达两年——这在法律层面是一个真实的风险敞口。

第三天结束时，Fable 5的处境颇为微妙："秘密降智"已经撤回，但数据政策引发的企业端信任裂缝还没有修复。

![](https://images.unsplash.com/photo-1614064548237-096f735f344f?w=1200)

## 第四天：政府出手，神话落幕

6月12日，周五下午5点21分。

美国商务部长霍华德·卢特尼克向Anthropic CEO达里奥·阿莫代伊发出一封信：Mythos 5和Fable 5将受到出口管制，范围涵盖美国境外的任何地点，以及境内的所有外国公民。

据《华尔街日报》报道，亚马逊CEO安迪·贾西亲自联系了财政部长斯科特·贝森特、商务部长卢特尼克和国家网络总监肖恩·凯恩斯，转交了亚马逊内部研究人员的安全发现——Claude Fable 5可以通过特定提示词被诱导出关于软件漏洞的信息，理论上可帮助转化为攻击代码。

Anthropic的回应藏着明显的委屈：我们审查了这一演示，其被用于识别少量此前已知的微小漏洞。这些漏洞看起来都相对简单，其他公开可用的模型也能在没有越狱的情况下发现它们。

换句话说：你说的这个"越狱"，用GPT-5.5也能复现，凭什么单独封杀我？

但争论没有意义。命令已经到达。

Anthropic选择全面关闭Fable 5和Mythos 5的访问权限。原因是若要选择性合规，则需要屏蔽大量用户——其中包括Anthropic自己的外籍员工。在出口管制法规（EAR）下，向身处美国境内的外国公民提供技术，法律上等同于向海外出口。Anthropic无法在90分钟内建立实时国籍验证系统，全球断网是唯一合法选择。

深夜，全球用户打开Claude，发现Fable 5从模型列表里消失了。API调用返回404："Claude Fable 5 is not available. Please use Opus 4.8."

## 这不只是一次技术事故

如果你以为这只是一场普通的"新模型发布翻车"，那你可能漏掉了更深层的剧本。

这场风波的背后，是Anthropic与特朗普政府之间一段持续数月的对抗关系。

2025年7月，Anthropic与五角大楼签署了一份上限2亿美元的合同，Claude成为第一个进入美军保密网络的前沿AI模型。合同中，Anthropic明确设了两条红线：禁止用于大规模国内监控，禁止用于完全自主的致命武器系统。

2026年1月，五角大楼要求删除这些限制， insisting on "all lawful purposes"。Anthropic拒绝。2月27日，国防部长Pete Hegseth宣布Anthropic为"供应链风险"——这个标签历史上只用于外国对手如华为，首次被贴给一家美国公司。特朗普随即下令所有联邦机构停止使用Anthropic产品。

Anthropic提起诉讼，法院暂时阻止了黑名单执行。然后，6月9日，Fable 5上线。6月12日，出口管制指令到达——就在Anthropic与政府在法庭上交锋的同一周。

更具戏剧性的是Anthropic那份透明度的反噬。Anthropic在发布前公开承认，任何模型的完美越狱抵抗都是不可能实现的——这是一种出于善意的透明表态。但政府似乎正是以这一承认为框架，为其担忧找到了依据。

如果透明承认自身局限会招来监管行动，而不透明则不会，那么行业将会得出相应结论。结果是公众获得的AI能力和风险信息将会减少——这与安全倡导者多年来的追求恰恰相反。

说白了：你越诚实，越可能被人抓住把柄。

![](https://plus.unsplash.com/premium_photo-1694475191764-09f8c42f7a58?w=1200)

## 预测市场：Fable 5会回来吗？

事件发生后，预测市场迅速开盘。

Kalshi显示，Fable 5在7月1日前恢复的概率为68%。Polymarket的对应合约为71%。6月15日（当天）恢复的概率只有22%，6月20日前为51%。

交易员倾向于认为问题会在6月下旬解决，而非当周。

白宫AI顾问David Sacks在X上表示，限制是"不情愿地"发出的，政府希望Anthropic修复漏洞后解除出口管制。"球在Anthropic的球场上。"

但安全研究员Katie Moussouris review了亚马逊的发现后，称政府反应是"完全过度反应"，这些信息"主要会帮助防御者，而非攻击者"。Venice AI创始人Erik Voorhees更直接： alleged jailbreak听起来更像是例行安全问题，而非重大威胁。

Anthropic目前的官方立场是：这是一个"误解"，公司正努力尽快恢复访问。但没有任何恢复时间表被给出。

## 一个更大的问题

Fable 5事件最深远的影响，不在于Anthropic一家公司的命运。

这是史上首次美国政府用出口管制令（EAR）强制下线已商用的前沿AI模型。过去美国卡的是芯片——不让NVIDIA卖H100给中国。现在卡的是模型访问权——不让非美国公民使用美国公司发布的AI。

这条权力边界一旦被确认，每一家AI公司都必须把它纳入发布风险模型。未来的AI发布，不只是技术问题，也是地缘政治问题。

对全球开发者来说，这意味着什么？

你花了几个月把Fable 5集成进生产管线，训练了微调模型，建立了工作流。然后一个周五下午的政府指令，让你的所有投入变成404。没有预警，没有过渡期，没有补偿。

更深层的问题是：**当一个国家可以单方面切断全球对某项技术的访问，这项技术真的属于全人类吗？**

智谱在Fable 5被封的同一时刻（6月13日下午5点21分）宣布GLM-5.2 MIT开源，原话是"前沿智能不应只属于少数人，也不应被少数规则随时收回"。这不是巧合，是刻意为之。

一边关大门，一边开大门。AI的冰与火之歌，从来没有这么具象过。

![](https://plus.unsplash.com/premium_photo-1733317453473-175c9831c874?w=1200)

Fable，那个来自拉丁语"被讲述的故事"。

这四天里，Fable 5确实被讲述了。只是没人料到，它自己才是这个故事里最短命的主角。

96小时内，它完成了一次令人叹为观止的"成就解锁"：发布日万众瞩目，被誉为AI史上最强公开模型；第二天被曝"秘密降智"，Anthropic连夜道歉撤回；第三天微软宣布内部禁用，数据政策掀起信任危机；第四天，美国政府一纸令下，全球强制下线。

这是一个在封神和封禁之间，只隔了四天的故事。

而Fable这个词的另一层含义，不应被遗忘：它也可以指"寓言"——一个带有道德教训的虚构故事。

这一次的教训是什么？

当一个公司将自己最强大的产品公开发布，政府可以在72小时内以"国家安全"为由将其全球下线——这条权力边界，今后每一家AI公司、每一个依赖AI的开发者、每一个相信技术无国界的用户，都必须纳入自己的风险模型。

AI的神话时代，可能刚刚结束。 gates时代，可能刚刚开始。

---

## 参考来源

1. [Claude Fable 5 Ban: The US Government's Export Control Directive](https://gizmodotech.com/technews/claude-fable-5-ban/)，Gizmodo Tech，2026-06-15
2. [Claude Fable 5四日惊魂](https://36kr.com/p/3852737616876550)，机器之心/36氪，2026-06-14
3. [Kalshi Markets Put 68% Odds on Fable 5 Returning Before July 1](https://bingx.pro/en/news/post/kalshi-markets-put-odds-on-fable-returning-before-july)，2026-06-15
4. [Anthropic Blocks Public Access to Claude Fable 5 After US Order](https://techpp.com/2026/06/15/daily-brief-june-15-2026-claude-fable-waze/)，TechPP，2026-06-15
5. [Hegseth declares Anthropic a supply chain risk](https://www.cbsnews.com/news/hegseth-declares-anthropic-supply-chain-risk/)，CBS News，2026-02-28
6. [Anthropic状告五角大楼解密](https://m.huxiu.com/article/4840882.html)，虎嗅/未尽研究，2026-03-11
7. [Pentagon Designates Anthropic a Supply Chain Risk](https://www.mayerbrown.com/pt/insights/publications/2026/03/pentagon-designates-anthropic-a-supply-chain-risk)，Mayer Brown，2026-03-02

<small>本文配图均来自Unsplash，遵循免费使用授权。</small>
