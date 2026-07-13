# NVIDIA Vera CPU架构拆解：为什么Agent时代需要重新设计CPU

![封面](cover.jpg)

2026年7月7日，NVIDIA发布了一篇博文，标题很直白：Vera是可规模化单线程最强CPU。

这个说法听起来有点反直觉。NVIDIA不是做GPU的吗？为什么要专门设计一款CPU？而且为什么强调单线程，不是多核并行？

答案藏在Agent AI的工作方式里。当AI从回答问题变成主动执行任务，CPU从后台辅助变成了关键路径上的瓶颈。NVIDIA做Vera不是因为想进CPU市场，而是因为现有的CPU拖了GPU的后腿。

## 问题定义：Agent AI为什么卡在CPU上

理解Vera的设计逻辑，先要理解Agent AI的执行流程。

一个AI Agent完成一次任务，不是模型一次推理就搞定的。它要走一个多步循环：模型推理 → 工具调用 → 代码执行 → 结果分析 → 再推理。GPU负责模型推理部分，但两步推理之间的所有串行工作，全是CPU的活。

```
Agent AI执行循环
├─ 步骤1：模型推理（GPU）
│   └── 模型生成下一步操作指令
│
├─ 步骤2：工具调用执行（CPU）← 瓶颈在这里
│   ├── 启动沙箱环境
│   ├── 克隆代码仓库
│   ├── 编译和运行测试套件
│   ├── 查询数据库
│   ├── 执行Python脚本
│   └── 检索文件和上下文
│
├─ 步骤3：结果返回模型（CPU → GPU）
│   └── CPU把执行结果送回GPU进行下一轮推理
│
└─ 循环往复，直到任务完成
```

问题出在步骤2。这些工具调用、代码执行、沙箱操作都是串行的——必须前一步完成才能进行下一步。GPU在等CPU干完活才能继续推理，CPU干得慢，GPU就闲着。

这不是小问题。NVIDIA的数据显示，在强化学习（RL）训练中，传统CPU可能只有45%的评估任务能在时间窗口内完成，剩下的55%因为CPU太慢来不及跑完，GPU就只能拿到不完整的训练信号。模型学习效率直接打折。

这就是NVIDIA说的Amdahl定律在Agent AI上的体现：系统整体性能被串行部分限制，再强的GPU也救不了慢CPU。

## Olympus核心：为串行控制流而生的架构

Vera的核心是NVIDIA自研的Olympus处理器核心。88个Olympus核心，176线程，基于Arm v9.2指令集。

Olympus的设计哲学和传统服务器CPU不同。传统CPU追求多核密度——塞更多核心，提高总吞吐。Olympus追求单核极致性能——让每个核心在满载情况下仍然跑得快。

具体架构参数：

```
Olympus核心架构
├─ 前端
│   ├── 10-wide指令获取和解码（每周期处理10条指令）
│   ├── 神经分支预测器（每周期评估两条taken分支）
│   └── 深度乱序执行（绕过长延迟操作，减少停顿）
│
├─ 执行单元
│   ├── 6 × 128b SVE2（可伸缩向量扩展，AI推理加速）
│   ├── FP8支持（低精度浮点，直接跑AI推理计算）
│   └── MPAM支持（内存系统资源分配，多租户隔离）
│
├─ 缓存
│   ├── 2 MB L2缓存（每核心独享）
│   └── 共享L3缓存（通过SCF互联）
│
└─ 指令集
    └── Arm v9.2全兼容（现有Arm软件生态直接可用）
```

几个关键设计值得展开说。

**神经分支预测器**。传统分支预测器基于历史模式预测分支走向，但在Agent工作负载中，代码的控制流非常复杂——Python解释器、模拟器、奖励逻辑、工具调用，分支模式不规则且难以预测。Olympus用神经网络做分支预测，每周期可以评估两条taken分支，保持流水线在复杂控制流中持续运转。这对RL工作负载特别重要，因为RL的环境模拟代码充满了不规则分支。

**10-wide解码前端**。主流服务器CPU的解码宽度通常是4-6条指令每周期。Olympus做到10-wide，意味着每周期喂给执行单元的指令更多，吞吐更高。在串行任务中，这意味着每个步骤完成得更快。

**FP8支持**。这是直接面向AI推理的设计。传统CPU做AI推理需要先把FP8权重转换成FP32或FP16，Olympus原生支持FP8计算，可以在CPU上直接跑轻量AI推理，不需要GPU介入。

## 单片计算裸片：拒绝Chiplet税

Vera最大胆的架构选择是用单片计算裸片（monolithic die），而不是现在流行的Chiplet多芯片封装。

```
单片die vs Chiplet设计对比
├─ Chiplet设计（AMD EPYC、Intel Xeon等）
│   ├── 结构：多个小计算芯片通过封装互联
│   ├── 优势：良率高、成本低、可灵活组合核心数
│   ├── 劣势：跨芯片通信延迟高、带宽不均匀
│   └── 问题：核心到内存的距离不一致
│       ├── 靠近内存控制器的核心：延迟低、带宽高
│       └── 远离内存控制器的核心：延迟高、带宽低
│       └── 结果：满载时性能波动大，tail latency高
│
└─ Vera单片die设计
    ├── 结构：88个核心在同一块计算裸片上
    ├── 优势：核心间距离均匀、内存带宽统一
    ├── 核心间带宽：3.4 TB/s（二分带宽）
    └── 每核心均匀分得：14 GB/s内存带宽
        └── 结果：满载时性能稳定，tail latency低
```

为什么这对Agent AI很重要？

Agent工作负载的特点是高并发+不可预测的内存访问模式。一个CPU socket上可能同时跑几千个沙箱环境，每个沙箱在做不同的事情——编译代码、查询数据库、执行脚本。这些任务的内存访问路径完全不可预测。

在Chiplet设计中，如果一个任务的内存访问跨芯片，就会产生额外的跨die延迟。而且不同核心到内存的距离不同，导致性能不一致——有些核心快，有些核心慢。在Agent场景下，慢的核心会拖慢整个Agent循环。

Vera的单片设计让每个核心到内存的距离完全相同，每核心均匀分得14 GB/s带宽，大约是传统数据中心CPU的3倍。这意味着不管哪个核心在跑什么任务，性能表现一致。满载时仍能保持超过90%的峰值内存带宽。

NVIDIA管这个叫"避免Chiplet税"。Chiplet省了制造成本，但付出了延迟和一致性的代价。对于Agent工作负载，这个代价不值得。

## Spatial Multithreading：重新定义超线程

传统CPU的超线程（SMT，Simultaneous Multithreading）是时间共享的——两个线程共享一个核心的执行资源，通过快速切换让两个线程都在跑。问题是，当一个线程占满了执行单元时，另一个线程的性能会下降。

NVIDIA搞了一个叫Spatial Multithreading（空间多线程）的东西。具体实现细节没有完全公开，但从描述来看，它不是传统的时分共享，而是给每个线程分配独立的空间资源。

```
传统SMT vs NVIDIA Spatial Multithreading
├─ 传统SMT
│   ├── 两个线程共享执行单元
│   ├── 时间片轮转，频繁上下文切换
│   ├── 问题：一个线程繁忙时另一个变慢
│   └── 性能波动大，tail latency不可控
│
└─ NVIDIA SMT
    ├── 每线程获得稳定的性能保障
    ├── 更强的隔离性（线程间互不干扰）
    ├── 可预测的tail latency
    └── 运行时可选择：性能优先 vs 线程数优先
```

这个设计的价值在Agent场景下很明确。当几千个沙箱同时跑在一个socket上时，每个沙箱的性能不能因为其他沙箱繁忙就下降。Spatial Multithreading保证了每个线程在满载下仍有稳定性能，这对于维持SLA至关重要。

## 内存子系统：LPDDR5X进数据中心

Vera的内存选择也很不传统。它用LPDDR5X——原本为手机和笔记本设计的低功耗内存——而不是数据中心标准的DDR5。

```
Vera内存子系统架构
├─ 内存类型：LPDDR5X（SOCAMM模块）
│   ├── 总带宽：1.2 TB/s
│   ├── 总容量：最高1.5 TB
│   ├── 功耗：< 40W（不到传统DDR的一半）
│   └── 模块形态：SOCAMM（Small Outline Compression-Attached Memory Module）
│       └── 可拆卸升级，不是焊死在板上的
│
├─ 每核心带宽：14 GB/s（传统CPU的3倍）
│
├─ 互联架构：第二代Scalable Coherency Fabric（SCF）
│   ├── 核心间二分带宽：3.4 TB/s
│   ├── 共享L3缓存
│   └── 满载下保持90%+峰值带宽
│
└─ 设计取舍
    ├── 选LPDDR5X：功耗低、带宽高、成本可控
    ├── 牺牲单条容量：LPDDR5X密度低于DDR5
    └── 用SOCAMM解决可维护性：可拆卸更换
```

传统DDR5的功耗很高，在AI工厂的机架级部署中，内存功耗会吃掉大量电力预算。LPDDR5X的功耗不到DDR5的一半，但带宽更高。代价是单条容量小，但NVIDIA通过SOCAMM模块化设计弥补了这一点——可以插拔升级，不像手机LPDDR是焊死的。

这个选择反映了Vera的设计优先级：**带宽和能效优先于容量**。Agent工作负载需要快速搬运大量数据（沙箱状态、KV缓存、工具输出），对带宽的需求远大于对容量的需求。

## 性能数据：三个维度的提升

NVIDIA公布了Vera对比x86 CPU（AMD EPYC Turin和Intel Xeon 6 Granite Rapids）的性能数据。

```
Vera vs x86性能对比
├─ 维度1：单核持续性能
│   ├── 满载下单核性能：x86的1.8倍
│   ├── Agent沙箱性能：x86的1.5倍
│   ├── 并发沙箱启动速度：x86的1.9倍
│   └── 意义：Agent循环中的串行步骤更快
│
├─ 维度2：延迟与一致性
│   ├── 满载峰值延迟：比x86低40%
│   ├── 原因：单片die消除跨芯片延迟
│   └── 意义：SLA更稳定，用户体验更一致
│
└─ 维度3：数据负载
    ├── Starburst SQL分析：x86的3倍速度
    ├── Redpanda流处理延迟：降至x86的1/6
    └── 意义：数据处理不再是瓶颈
```

这些性能提升对AI工厂的实际影响有三个层面：

**RL训练层面**：CPU更快意味着更多环境评估能在时间窗口内完成。传统CPU完成45%的评估，Vera可以完成85%。GPU拿到更完整的训练信号，模型学得更快更准。

**Agent推理层面**：工具调用执行更快，用户等待时间更短。GPU利用率更高，不用闲着等CPU。

**KV缓存层面**：这个容易被忽略但很重要。Agent在两步GPU推理之间有一段CPU工作时间。这段时间里GPU不会闲着——它会接其他用户的请求。如果CPU太慢，原来的用户请求回来时，它的KV缓存可能已经被挤掉了，GPU就得重新计算整个上下文。Vera压缩了CPU工作时间，缩短了KV缓存的暴露窗口，减少了昂贵的重计算。

## 机架级部署：一个机架22500个沙箱

Vera不只是颗CPU，它是一套机架级系统。

```
Vera CPU机架架构
├─ 物理规格
│   ├── 每个机架：256颗Vera CPU
│   ├── 每个CPU：88核心 / 176线程
│   ├── 机架总核心数：22,528个
│   └── 沙箱容量：22,500+个并发沙箱
│
├─ 冷却方式：液冷
│   └── 与NVL72 GPU机架共享冷却基础设施
│
├─ 网络集成
│   ├── BlueField-4 SmartNIC（每颗Vera配一块）
│   ├── SmartNIC内含Grace核心做管理卸载
│   └── Vera的计算资源100%用于Agent任务
│
├─ 效率对比（vs x86机架）
│   ├── 沙箱密度：4倍
│   ├── 每瓦性能：2倍
│   └── 意义：同样空间和电力，4倍的Agent处理能力
│
└─ 部署模式
    ├── 独立CPU机架（纯Agent任务）
    ├── Vera Rubin NVL72（与Rubin GPU紧耦合）
    │   └── 通过NVLink-C2C连接，共享统一内存
    ├── 单/双路服务器（企业级部署）
    └── HGX Rubin NVL8（PCIe GPU配对）
```

机架级设计的核心逻辑是：AI工厂按机架而不是按服务器来规划容量。Vera CPU机架和NVL72 GPU机架使用相同的电力、冷却和空间规划，可以快速混部。

Oracle Cloud Infrastructure已经计划从2026年开始部署数十万个Vera CPU，成为首个超大规模部署Vera的云厂商。

## 竞争格局：三种CPU设计哲学的碰撞

Vera的出现让数据中心CPU市场变成三条路线的竞争：

| 维度 | NVIDIA Vera | AMD EPYC Venice | Intel Xeon 6 |
|:---|:---|:---|:---|
| **制程** | 未披露（推测台积电N5/N3） | 台积电2nm | Intel 3 |
| **核心数** | 88核Olympus | 最高256核（Zen 6c） | 最高128核 |
| **设计哲学** | 单核极致性能 | 多核密度优先 | 均衡路线 |
| **裸片设计** | 单片计算die | Chiplet | Chiplet |
| **内存** | LPDDR5X 1.2TB/s | DDR5（16通道） | DDR5/MCDMA |
| **指令集** | Arm v9.2 | x86 | x86 |
| **目标场景** | Agent AI专用 | 通用服务器+AI | 通用服务器+AI |
| **核心优势** | 串行性能、能效 | 核心数、生态兼容 | 生态成熟度 |
| **核心劣势** | Arm生态适配 | 满载性能波动 | 单核性能落后 |

三种设计哲学的本质区别在于优化目标不同。

Vera优化的是**单核在满载下的持续性能**。它的88个核心每个都能在所有核心同时工作时保持高性能，适合Agent工作负载中大量并发但每个都要求快速响应的串行任务。

Venice优化的是**总吞吐量**。256个核心意味着可以同时处理更多任务，但每个核心的性能可能因为Chiplet跨die通信而波动。适合高吞吐但延迟不敏感的场景。

Xeon 6走中间路线，但在单核性能上已经落后。

这不是说谁好谁坏，而是不同工作负载需要不同的CPU设计。对于传统Web服务、数据库、虚拟化，多核密度更重要。对于Agent AI，单核持续性能更重要。Vera赌的是后一个趋势会越来越大。

## 行业影响：CPU不再是后台基础设施

Vera的发布标志着一个认知转变：在Agent AI时代，CPU不再是后台基础设施，而是AI工厂吞吐量的直接驱动因素。

过去十年，数据中心的叙事是GPU为王，CPU是配角。但当AI从训练走向推理、从推理走向Agent，CPU的工作量急剧增加。每一次工具调用、每一次沙箱启动、每一次代码编译，都是CPU在干活。GPU的利用率越来越受限于CPU的速度。

NVIDIA做Vera的逻辑是闭环的：GPU卖得越好，对配套CPU的要求越高，如果CPU成为瓶颈就会限制GPU的销量。所以自己做CPU，确保整个系统的瓶颈不在CPU端。

这个策略和NVIDIA的GPU+DPU+CPU+网络的全栈布局一脉相承。Vera不是孤立的CPU产品，而是Vera Rubin平台的一部分——和Rubin GPU、BlueField-4 DPU、Spectrum-X网络、MGX机架架构协同设计。通过NVLink-C2C，Vera和Rubin GPU共享统一内存，GPU可以始终保持高利用率。

对行业来说，Vera的出现可能加速Arm在数据中心渗透。之前Arm服务器CPU的故事是成本和能效，Vera加了一个新故事：性能。如果Arm在Agent场景下真的比x86快1.8倍，x86的生态护城河会被进一步压缩。

---

## 参考来源

1. [Vera正式登场：NVIDIA首款专为智能体打造的CPU](https://blogs.nvidia.cn/blog/vera-cpu-delivery/)，NVIDIA博客，2026-05-18
2. [NVIDIA Vera CPU Delivers High Performance, Bandwidth, and Efficiency for AI Factories](https://developer.nvidia.com/blog/nvidia-vera-cpu-delivers-high-performance-bandwidth-and-efficiency-for-ai-factories/)，NVIDIA Developer Blog，2026-03-16
3. [NVIDIA Vera CPU Boosts AI Factory Throughput to Accelerate Agentic Workloads](https://developer.nvidia.com/blog/nvidia-vera-cpu-boosts-ai-factory-throughput-to-accelerate-agentic-workloads/)，NVIDIA Developer Blog，2026-07-07
4. [可规模化单线程最强CPU：英伟达Vera在智能体AI负载下持续性能是x86的1.8倍](https://www.ithome.com/0/970/170.htm)，IT之家，2026-07-08
5. [NVIDIA Vera CPU官方页面](https://www.nvidia.com/en-us/data-center/vera-cpu/)，NVIDIA官网
6. [NVIDIA Vera: Reimagining CPUs for Agents, Reasoning, and What's Next](https://www.nvidia.com/en-us/on-demand/session/gtc26-s82437/)，GTC 2026演讲
7. [From Grace to Vera: NVIDIA's next data center CPU](https://www.nvidia.com/en-us/on-demand/session/gtc26-s81680/)，GTC 2026演讲
8. [NVIDIA Vera CPU Targets Agentic AI Bottleneck](https://theagenttimes.com/articles/nvidia-vera-cpu-targets-agentic-ai-bottleneck-with-max-singl-dc4df490)，The Agent Times，2026-07-07
9. [消息称AMD Venice CPU将于7月22日正式推出](http://m.toutiao.com/group/7661109957743477284/)，环球网，2026-07-11
10. [全球首款2nm高性能计算CPU！AMD官宣Zen 6 EPYC Venice 7月22日发布](https://www.eet-china.com/mp/a508943.html)，电子工程专辑，2026-07-10

<small>本文配图使用AI生成，遵循CC0协议。</small>
