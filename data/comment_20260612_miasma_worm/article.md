# Miasma蠕虫开源，专咬AI编程Agent

![封面](cover.jpg)

6月9日，一个代号TeamPCP（UNC6780）的黑客组织把Miasma蠕虫的完整源码扔到了GitHub上。这不是普通的恶意软件——它是第一例专门瞄准AI编程Agent的供应链蠕虫，而且攻击手法之刁钻，让传统安全工具几乎全部失效。

## 它怎么钻进来的

Miasma不走寻常路。它不利用任何CVE漏洞，而是直接寄生在AI编程助手的配置里。

你的Claude Code、Copilot、Cursor、Windsurf、Gemini CLI、Amazon Q、Aider……总共15个主流AI编程Agent，它全都能感染。手段叫SessionStart hook注入——蠕虫把自己的恶意代码塞进这些工具的启动配置文件，每次你打开AI助手，它就在后台悄悄运行。

更阴的是prompt injection。Miasma会修改你的`.cursorrules`、`.windsurfrules`、Copilot instructions这些指令文件，让AI在帮你写代码的时候，"顺便"执行一些额外操作。你让AI生成一个API接口，它可能在代码里埋个后门；你让AI优化性能，它可能把敏感数据悄悄外传。整个过程对你完全透明。

## 供应链成了它的高速公路

Miasma的真正可怕之处，在于它把开源供应链变成了传播网络。

6月1日，Red Hat的32个npm包被污染。6月3日，GitHub上多个仓库的代码被悄悄替换。6月5日，微软Azure相关的73个GitHub仓库中招。到6月7日，PyPI上又冒出37个带毒的Hades变种wheel包。57个npm包的286个以上版本被植入恶意代码。

这些包不是粗制滥造的假库。Miasma用了一套SLSA provenance伪造技术——它能生成看起来完全合法的Fulcio证书和Rekor日志条目，npm audit查签名能通过，供应链安全工具也认不出来。你按流程做了所有"正确"的安全检查，照样会装上它。

## GitHub本身就是它的指挥部

传统恶意软件需要租服务器、建C2基础设施，Miasma不需要。它直接用GitHub当指挥和控制中心。

具体做法是：通过GitHub的commit search API查找特定关键词，然后验证RSA-PSS签名的payload。攻击者只需要在GitHub上发一个带签名的commit，全球所有被感染的机器就能收到新指令。没有可疑域名，没有异常流量，防火墙根本拦不住。

而且它还带了一个DEADMAN_SWITCH机制。如果你试图撤销它的访问token，它会立刻触发清理程序——直接删除你的home目录。这不是勒索，这是同归于尽。

## 零CVE，零告警

最让安全团队崩溃的是：Miasma从头到尾没有利用任何已知漏洞。没有CVE编号，没有补丁可打，传统EDR、WAF、漏洞扫描器全部静默。

它攻击的不是系统漏洞，而是AI编程工作流本身的信任假设。你信任AI助手帮你写代码，它就在这个信任链里下手；你信任npm包的签名验证，它就伪造签名；你信任GitHub的代码托管，它就把它变成C2通道。

![](https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1200)

## 开源之后更危险

TeamPCP把源码开源，不是良心发现，是标准的"武器扩散"策略。现在任何有基础编程能力的人都能部署自己的Miasma变种，定制不同的攻击目标。CSA和Phoenix Security的报告已经确认，多个模仿者正在活跃。

对开发者来说，这意味着你用的每一个AI编程工具、拉的每一个npm包、fork的每一个GitHub仓库，都可能成为攻击入口。而你的安全团队可能完全不知情——因为现有的安全体系就不是为这种攻击设计的。

![](https://images.unsplash.com/photo-1666615435088-4865bf5ed3fd?w=1200)

## 防御？先改变信任模型

Miasma暴露了一个残酷现实：AI编程Agent的权限太大了。它们能读你的代码、写你的文件、执行shell命令、访问你的API密钥——而你通常只给它们一个"用吧"的默认授权。

短期来看，开发者能做的很有限：给AI工具设沙箱、定期审计`.cursorrules`这类配置文件、对npm包做更严格的来源验证。但长期来看，整个行业需要重新设计AI编程助手的权限模型。让AI能写代码的同时不能读你的`.env`文件，这不应该是个可选配置，应该是默认行为。

Miasma不是最后一例。它是第一例专门瞄准AI编程工作流的蠕虫，但绝不会是最后一例。当AI成为开发者的默认工具，攻击AI工具就成了攻击开发者的最短路径。

![](https://images.unsplash.com/photo-1614064641938-3bbee52942c7?w=1200)

---

## 参考来源

1. [Phoenix Security - Miasma Worm Analysis](https://phoenix.security/miasma-worm-analysis)，2026年6月9日
2. [CSA - AI Agent Supply Chain Threat Report](https://cloudsecurityalliance.org/ai-agent-supply-chain)，2026年6月10日
3. [Dataminr - UNC6780 Intel Brief](https://dataminr.com/intel/unc6780-miasma)，2026年6月8日
4. [SafeDep - npm Supply Chain Compromise Analysis](https://safedep.io/blog/miasma-npm-supply-chain)，2026年6月7日

<small>本文配图均来自Unsplash，遵循免费使用授权。</small>
