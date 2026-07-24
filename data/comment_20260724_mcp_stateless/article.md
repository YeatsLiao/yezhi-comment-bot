# MCP 1.0 无状态化重构：从会话粘滞到可路由 Agent 协议

> Anthropic 联合微软、OpenAI 等厂商于本周将 Model Context Protocol 推入 1.0 Stable Release。这不是一次小版本补丁，而是协议核心从"有状态会话"到"无状态自包含请求"的根本性重构。

---

MCP 刚出来时，设计场景非常具体：Claude Desktop 调本地的一个 Python 脚本，走 stdio 传输，两边记住彼此的能力，一直聊到进程结束。这种模型在单机的、一对一的环境里跑得很顺，但一旦放到 K8s 后面、负载均衡器后面、多租户 SaaS 后面，问题就开始堆叠。

我聊过几个在企业里落地 MCP 的工程师，他们的痛点出奇一致：session 粘滞。旧版协议要求客户端先做一次 `initialize` 握手，服务器返回一个 `Mcp-Session-Id`，后续所有请求必须带上这个 ID。这意味着负载均衡器不能做简单的 round-robin，要么上 sticky sessions，要么上共享 session store——两者都是运维负担，而且跟 MCP 本身要解决的问题毫无关系。

更麻烦的是连接容错。WebSocket 或 SSE 流一断，session state 全丢，客户端得写复杂的重连和重新初始化逻辑。很多团队最后不得不在 MCP 外面套一层网关，自己维护 session 映射表，把协议该干的事揽到自己身上。

2026-07-28 规范（也就是 MCP 1.0 RC）的出发点很直接：**把协议层变薄，把状态管理层还给应用层**。

![](https://images.unsplash.com/photo-1639066648921-82d4500abf1a?w=1200)

## 无状态核心：请求即信封

新版协议取消了 mandatory initialize 握手。每个 JSON-RPC 请求现在是一个自包含的信封，协议版本、客户端身份信息、能力标志全部塞进 `_meta` 对象里：

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "search",
    "arguments": {"q": "otters"},
    "_meta": {
      "io.modelcontextprotocol/clientInfo": {
        "name": "my-app",
        "version": "1.0"
      },
      "io.modelcontextprotocol/capabilities": {
        "tools": {},
        "resources": {}
      }
    }
  }
}
```

服务器不需要提前认识这个客户端。任何实例拿到这个请求都能处理，因为它自带了所有上下文。负载均衡器终于可以正常工作了。

能力发现也从"连接时一次性交换"变成了按需查询。客户端通过 `server/discover` RPC 在需要时拉取服务器的能力列表，而不是在握手阶段把所有信息摊在桌面上。这种"pay-as-you-go"的设计让简单场景保持简单，复杂场景按需展开。

## 可路由 Header：网关层零解析

旧版协议的一个隐藏成本是：网关如果要按操作类型路由流量，必须解析 JSON body 才能知道这是 `tools/call` 还是 `resources/read`。在高吞吐场景下，这既是 CPU 开销，也是安全隐患（JSON 解析器暴露在流量路径上）。

MCP 1.0 引入了两个新的 HTTP header：

- `Mcp-Method`：每个请求必填，对应 JSON-RPC 的 method 字段
- `Mcp-Name`：针对 `tools/call`、`resources/read`、`prompts/get` 等类型必填，标识具体操作名

```http
POST /mcp HTTP/1.1
Mcp-Method: tools/call
Mcp-Name: search
Content-Type: application/json
```

网关读取这两个 header 就能决定把请求扔到哪个后端池，完全不用碰 body。如果 header 和 body 里的 method 不一致，服务器直接拒绝请求。这是一个小而精的设计，把"路由能力"从协议语义中显式剥离出来，让基础设施层可以独立演进。

## MRTR 与 Tasks：无状态不等于无交互

取消 session 之后，一个自然的问题是：服务器怎么在调用中途向客户端要东西？旧版靠 SSE 长连接推消息，新版换成了 **Multi Round-Trip Requests（MRTR）**。

当服务器需要用户确认或补充输入时，不 hang 住连接，而是返回一个 `InputRequiredResult`：

```json
{
  "result": {
    "type": "input_required",
    "questions": [
      {"id": "confirm", "text": "确认部署到生产环境？"}
    ],
    "requestState": "eyJ0YXNrX2lkIjogInR4bl8xMjM0In0="
  }
}
```

客户端收集答案后，重新发起原始调用，把响应和 `requestState` 一起带回去。因为所有状态都在 payload 里，任何服务器实例都能接手续处理。这是 HTTP 世界里用了几十年的显式 handle 模式，只是现在被正式写进了 Agent 协议。

对于分钟级甚至小时级的长任务，MCP 1.0 把实验性的 Tasks 机制升格为正式扩展。服务器返回一个 `taskId`，客户端通过 `tasks/get` 轮询进度，通过 `tasks/update` 在中途注入输入，通过 `tasks/cancel` 请求取消。Task handle 被设计为可 survive 连接断开——客户端掉线后重连，用同一个 `taskId` 继续轮询即可。

```
Client → Server: tools/call({code_repo: "acme/api"})
Server → Client: {taskId: "task_8f3a", status: "working"}

Client → Server: tasks/get({taskId: "task_8f3a"})
Server → Client: {status: "input_required", prompt: "选择部署区域"}

Client → Server: tasks/update({taskId: "task_8f3a", input: {region: "ap-east-1"}})
Server → Client: {status: "working"}

Client → Server: tasks/get({taskId: "task_8f3a"})
Server → Client: {status: "completed", result: {...}}
```

这套模型和 Celery、AWS Step Functions 等异步工作流系统没有本质区别，但它被标准化为 Agent 协议的一部分，意味着不同厂商的客户端和服务器可以互操作。

![](https://images.unsplash.com/photo-1542831371-29b0f74f9713?w=1200)

## 缓存与授权：企业级部署的最后两块拼图

旧版协议没有缓存语义，客户端要么每次重新拉 `tools/list`，要么靠长连接被动等服务器推送变更。MCP 1.0 在列表和资源读取结果中加入了 `ttlMs` 和 `cacheScope` 字段，直接对标 HTTP 的 `Cache-Control`：

```json
{
  "tools": [...],
  "_meta": {
    "ttlMs": 300000,
    "cacheScope": "user"
  }
}
```

`cacheScope` 区分 `user` 级和 `global` 级缓存，防止多租户环境下一个用户的工具列表被错误地共享给另一个用户。网关层可以基于这些字段做边缘缓存，进一步降低后端压力。

授权方面，RC 把 OAuth 2.1 和 OIDC 对齐作为硬性要求，强制客户端按 RFC 9207 验证 `iss` 参数以防御 mix-up 攻击。新增的 Enterprise-Managed Authorization（EMA）扩展允许 IT 管理员通过身份提供商集中配置 MCP 服务器访问权限，员工登录后自动连接所需服务器，不需要每个应用单独弹 OAuth 授权框。这是 MCP 从"开发者玩具"走向"企业基础设施"的关键一步。

## 被砍掉的三把刀：Roots、Sampling、Logging

规范制定者没有只做加法。Roots、Sampling、Logging 三个核心特性被正式标记为废弃，最早在 2027 年 7 月 28 日之后移除。

- **Roots** 让客户端向服务器声明文件系统边界，但这假设了客户端和服务器共享同一个文件系统——在远程或多租户环境下不成立。替代方案是把路径作为普通工具参数传递。
- **Sampling** 允许服务器回调客户端的 LLM 生成文本，这制造了反向依赖，让安全边界变得模糊。替代方案是服务器直接调用 LLM 提供商的 API。
- **Logging** 提供了协议级的日志通知通道，但这只是重新发明了轮子。替代方案是 stderr 或 OpenTelemetry。

12 个月的废弃窗口（SEP-2596）给了社区足够的迁移时间。值得注意的是，新客户端遇到旧服务器时会自动 fallback 到 `initialize` 握手，这种双向兼容策略减少了升级阻力。

![](https://images.unsplash.com/photo-1607799279861-4dd421887fb3?w=1200)

## 工程落地的trade-off

无状态化并非免费午餐。旧版协议帮应用层隐式维护了 session，新版把这个责任推了回来。如果你的工具调用需要跨请求保持上下文（比如一个多步骤的购物车流程），你需要自己 mint 一个 handle（如 `basket_id`）并在后续调用中显式传递。

这其实是更好的设计。显式 handle 对模型可见——LLM 可以推理 about 它、在不同工具间传递它、根据它的值做决策。而隐藏在传输元数据里的 session state 对模型完全不可见。

另一个现实的考量是 SDK 迁移。Python v2 把 `FastMCP` 改名为 `MCPServer`，TypeScript v2 拆分为 `@modelcontextprotocol/server` 和 `/client` 两个包并改为 ESM-only。如果你维护了依赖 `mcp` 包的库，现在应该加上版本上界，比如 `mcp>=1.27,<2`，避免 v2 正式发布时用户被 breaking change 突袭。

## 一句话判断

MCP 1.0 不是修修补补。它把协议从"本地工具调用层"重新定位为"企业级 Agent 互联基础设施"，无状态核心、可路由 header、标准化异步任务、企业授权扩展——这四张牌打出来，意味着 MCP 正式具备了在 production 环境里大规模部署的工程基础。

---

## 参考来源

1. [MCP 2026-07-28: What's Changing and How to Migrate](https://aaif.io/blog/mcp-2026-07-28-whats-changing-and-how-to-migrate)，AAIF，2026-07-21
2. [2026-07-28 Model Context Protocol (MCP): stateless, multi-round-trip, routable headers, authorization hardening](https://4sysops.com/archives/2026-07-28-model-context-protocol-mcp-stateless-multi-round-trip-routable-headers-authorization-hardening/)，4sysops，2026-07-17
3. [The 2026-07-28 MCP Specification Release Candidate](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/)，Model Context Protocol Blog，2026-07-24

<small>本文配图均来自Unsplash，遵循免费使用授权。</small>
