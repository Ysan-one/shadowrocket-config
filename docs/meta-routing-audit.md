# Muse / Facebook / Meta 分流核查

核查日期：2026-09-21。适用于 `Shadowrocket-v2.conf`。

## 实际故障证据

用户提供的短时连接日志中，Muse API、Meta Graph 和 Facebook 请求已匹配代理，但 `hatch.metaaivm.com` 四次匹配 `FINAL,DIRECT`。`metaaivm.com` 的父域名规则覆盖这个公共入口及每个用户的随机 VM 子域名。这里仅记录公共服务域名和汇总结论，不保存或发布原始日志、用户 VM 标识或节点信息。

[Meta 的架构说明](https://research.meta.ai/blog/security-and-safety-for-ai-agents-our-approach-with-muse)确认手机和网页客户端直接连接用户的 VM；[Muse 官网](https://muse.ai/)公开前端中的 `FEATHER_VM_HOST_SUFFIX` 为 `.metaaivm.com`。

## 核查来源与覆盖

读取 Muse、Meta 账号、Facebook、Instagram、Threads、Messenger、WhatsApp 的公开页面响应、CSP 和资源地址，并检查 Muse 首页引用的 40 个脚本。另核对本配置引用的广告、中国及通用代理远程名单，以及部分兼容域名的公共 DNS 和短链跳转。

| 功能 | 覆盖范围 | 依据 |
| --- | --- | --- |
| Muse 网页、API、账号和实时连接 | `muse.ai`、`meta.ai`、`meta.com` 及子域名 | Muse 页面、前端脚本和日志 |
| 个人云端 VM | `metaaivm.com` 及子域名 | 实际日志与官方前端常量 |
| 文件、作品与内嵌应用 | `metaaiusercontent.com`、`ecto1usercontent.com`、`meta-agents-apps.workers.dev` 及子域名 | Muse 的图片、框架和资源 CSP |
| Facebook 图片、视频、附件 | `fbcdn.net`、`fbsbx.com`、`facebook.com` 及子域名 | Facebook、Messenger、Muse 的 CSP 和资源地址 |
| 内容兼容域名 | `fbcdn.com`、`fbsbx.net` | Facebook 权威 DNS；裸域 HTTPS 存在证书不匹配，未把它们当成成功加载的业务接口 |
| 视频与私信短链 | `fb.watch`、`fbwat.ch`、`ig.me` | 实际分别跳转到 Facebook / Instagram |
| Instagram、Threads、WhatsApp 内容 | `cdninstagram.com`、`instagram.com`、`threads.com`、`threads.net`、`whatsapp.com`、`whatsapp.net` 等 | 对应官方页面的 CSP 和资源地址 |
| 第三方 GIF 内容 | `giphy.com`、`tenor.com`、`tenor.co` | Facebook、Instagram、Threads、WhatsApp 的图片和媒体 CSP |
| Muse 支付与钱包界面 | `api.stripe.com`、`hooks.stripe.com`、`m.stripe.network`、`js.stripe.com` 及其子域名、`link.com` 及其子域名 | Muse CSP 与 [Stripe 官方集成说明](https://docs.stripe.com/security/guide) |
| 生产身份验证与支付认证 | `api.yoti.com`、`client.cardinaltrusted.com` 及子域名、`centinelapi.cardinalcommerce.com`、`ipification.com`、`paywithmybank.com`、`trustly.one` | Meta 账号、Facebook / Instagram / WhatsApp 的 CSP |
| WhatsApp 验证码 | `iframe.arkoselabs.com`、`whatsapp-api.arkoselabs.com` | WhatsApp 官方页面的 CSP |
| 隐私中继 | Meta 专用 Fastly / Cloudflare 主机 | Muse 公开脚本及官方页面 CSP |

这些功能规则均使用 `PROXY,force-remote-dns`，位于广告、国内和通用分流规则之前。父域名规则能覆盖其下的新子域名。

## 有意保留的边界

- CSP 表示网站允许访问的目标，不等于本次手机实际请求过的域名。已观察到的连接与页面声明的潜在依赖分开记录。
- 部分主机原本已由通用远程名单代理，例如 `workers.dev`、`fbcdn` 和 `fb.watch`；此次显式补充是为了固定优先级和远程 DNS，不能将所有新增规则描述成此前必然直连。
- 新增规则只覆盖 Meta 的 `meta-agents-apps.workers.dev` 账户和已确认的专用中继，未新增整个 `workers.dev`、`cloudflare.com`、`fastly-edge.com` 或 Akamai 的父域名规则。
- 广告和统计目标继续遵循原有拦截规则。`centinelapistag.cardinalcommerce.com` 是测试环境，本地回环地址不是互联网业务依赖，均不加入生产代理白名单。
- `igcdn.com` 的 DNS 查询返回失败；旧 `fbcdn-a.akamaihd.net`、`instagramstatic-a.akamaihd.net` 别名返回 NXDOMAIN。没有仅凭旧名单添加这些地址，也没有把 Meta 员工内网或无关品牌域名加入白名单。
- `www.meta.ai` 本次匿名请求返回 403 客户端挑战，不能据此声称已检查其登录后资源。已保留整个 `meta.ai` 的代理和远程 DNS 覆盖。

## 验证范围

配置格式、重复规则和规则顺序由仓库校验脚本检查。7 个成功读取的官方页面中，108 个声明或引用的生产功能域名均通过了广告规则之前命中 `PROXY,force-remote-dns` 的检查；另外核对了实际日志主机、VM / Workers 随机子域名、Stripe 脚本子域名和短链。

本轮新增 22 条专用规则，并将现有 `js.stripe.com` 精确规则扩展为父域名规则。所有既有 `DIRECT` 规则保持不变；新增匹配范围与本次下载的 AdvertisingLite 域名条目没有新增交集。共享 CDN 的无关主机未因本轮修改获得新的显式代理规则。

这些检查不能替代在用户设备上逐项登录、查看附件、运行工具和使用语音。若仍有失败，应在相同节点下对比配置与全局模式，并用对应时段日志定位实际 `DIRECT` / `REJECT` 目标。用户提供的短时日志不足以证明所有功能均已覆盖。
