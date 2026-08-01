# Shadowrocket 配置

这是用于 iPhone、iPad 和 Apple Vision Pro 的 Shadowrocket 远程配置。

## 配置地址

### 稳定版

稳定版保留原来的大型静态规则，已经在现有设备上验证可用：

```text
https://raw.githubusercontent.com/Ysan-one/shadowrocket-config/main/Shadowrocket.conf
```

### V2 测试版（推荐先在一台 iPhone 上使用）

V2 使用分层结构和持续维护的远程规则，补齐 ChatGPT Voice、TikTok、Telegram、Notion、1Password 等容易被旧名单漏掉的流量，同时继续让 Apple 地图、FaceTime、iMessage、Apple Music、Apple TV、Apple 播客、iCloud、App Store、哔哩哔哩、夸克和其他中国大陆服务直连：

```text
https://raw.githubusercontent.com/Ysan-one/shadowrocket-config/main/Shadowrocket-v2.conf
```

V2 不会覆盖稳定版，两份配置可以同时保存在 Shadowrocket 中。建议先在一台 iPhone 上试用两到三天，再让 iPad 和 Apple Vision Pro 切换。

## 在设备中安装 V2

1. 复制上面的 V2 配置地址。
2. 打开 Shadowrocket，进入“配置”。
3. 点击右上角“+”，粘贴地址并下载。
4. 点击下载后的 `Shadowrocket-v2.conf`，选择“使用配置”。
5. 在 Shadowrocket 的“设置 → 自动更新 → 配置”中开启自动后台更新。
6. 在苹果系统“设置 → 通用 → 后台 App 刷新”中允许 Shadowrocket 后台刷新。

V2 中的 ChatGPT Voice IP 来自 OpenAI 官方 `chatgpt-voice.json`。GitHub Actions 每天检查一次；只有官方 IP 发生变化时才会更新 `rules/ChatGPT-Voice.list`。语音优先使用 UDP 3478，代理节点需要支持 UDP 才能获得更好的通话质量。

## 使用原则

- 广告和跟踪域名继续使用 `REJECT`。
- GFW 黑名单中的站点使用 `PROXY`。
- ChatGPT/OpenAI 的登录、接口、静态资源、WebSocket、iOS 设备校验和 Google 登录链路统一使用 `PROXY` 与远程 DNS，避免规则模式下混用大陆直连 IP 和代理 IP。
- GitHub 云端配置和远程规则使用的 `raw.githubusercontent.com`、`*.githubusercontent.com` 精确走 `PROXY`，避免大陆直连 GitHub Raw 时更新偶发失败；普通 GitHub 网站不会因此全部消耗代理流量。
- iOS 系统认证网页会话不再旁路 Shadowrocket；`auth.openai.com`、`setup.auth.openai.com`、`auth0.openai.com` 以及当前 Cloudflare 别名均有最优先代理兜底。
- Claude/Anthropic 的登录、推理、文件、功能开关、连接器与 WebSocket 使用父域名级 `PROXY` 保护，并启用远程 DNS；新增的 Anthropic 子域名也会自动匹配。
- Gemini、Google 登录及常用图片、视频和资源域名统一使用 `PROXY` 与远程 DNS。
- Riot Mobile（拳头 App）只将国际账号登录、配置、社交和战绩等小流量接口交给 `PROXY`；中国 App Store 的《英雄联盟手游》资源包、腾讯游戏下载域名以及 Riot/LoL 公共静态资源优先 `DIRECT`，不再使用会误伤国服下载的整个 `riotgames.com` 父域名代理。
- Apple Intelligence 和 Siri 的官方核心域名走 `PROXY`，地区判断主机 `gspe1-ssl.ls.apple.com` 也精确走代理；`mask.icloud.com`、`mask-h2.icloud.com`、`mask-api.icloud.com` 三个 iCloud Private Relay 主机按用户选择固定走代理。使用相关功能时请在 Shadowrocket 首页选择稳定的美国节点。
- Apple 地图的已确认主机使用 `DIRECT`，但不会把整个 `ls.apple.com` 放行，避免未来未知的 Siri AI 主机从大陆出口连接。
- FaceTime、iMessage、Apple 推送和 Apple 的 `17.0.0.0/8` 网络使用 `DIRECT`。配置没有使用 UDP 3478 端口级直连，因为 ChatGPT Voice 也会使用这个端口。
- Apple TV、App Store、苹果系统更新以及 iCloud 照片和文件内容使用 `DIRECT`，避免大流量下载消耗代理额度。
- Apple Music 的歌曲、无损音频、资料和苹果 CDN 使用 `DIRECT`；切换中区或美区 Apple ID 不会改变分流结果。QQ 音乐、网易云、酷狗等国内音乐服务继续由国内规则直连。
- Apple 播客的苹果目录、封面、进度同步、苹果 CDN 和常见第三方节目托管平台使用 `DIRECT`；播客广告规则仍然优先于平台直连规则。
- 神州租车、雪球、主要中国大陆银行、银联和互联网银行的核心域名放在广告规则之前显式 `DIRECT`；雪球另有专用远程列表补充相关证券和基金域名。
- 国内 App 开屏广告和常见广告 SDK 使用 AdvertisingLite 远程规则在本机 `REJECT`，并为闲鱼、淘宝固定补充优酷广告、淘宝广告统计和活动弹层域名；不启用 MITM、不安装解密证书。
- 未匹配的站点最终使用 `DIRECT`。
- 百度、哔哩哔哩、高德、淘宝、微信、京东、国内视频、夸克等常用国内服务设置了显式 `DIRECT` 保护。

V2 还将本地 DNS 换成阿里和腾讯的加密 DoH，并补充局域网 IPv6 绕过；它只保留一份 AdvertisingLite 广告规则，不再重复加载旧配置中的 16,000 余条静态广告名单。通用中国大陆规则放在通用海外代理规则之前，最终仍然使用 `FINAL,DIRECT` 控制代理流量成本。

原先引用的 `xpdigital/Apple-Rule` 仓库已无法访问。它最后公开的 Apple AI 精简规则所包含的 `guzzoni.apple.com`、`*.smoot.apple.com`、三个 Apple Relay 主机、`cp4.cloudflare.com` 和 `gspe1-ssl.ls.apple.com` 已全部固化在本配置中，因此移除了会返回 404 的远程依赖。三个指定的 iCloud Private Relay 主机继续代理；已确认的 Apple 地图主机以及 Apple TV、FaceTime、iMessage、Apple 播客、App Store、系统更新和 iCloud 大流量域名继续优先直连。未识别的 `*.ls.apple.com` 仍保守走代理，以兼顾新版 Siri AI。

这里的 Apple TV 直连指苹果自有系统和内容服务。Apple TV 上的 YouTube、Netflix 等第三方应用仍会按照各自域名的规则决定直连或代理。

Apple 播客与 Apple TV 不同：公开播客的 RSS 和音频文件可以由节目发行方放在任意服务器。本仓库的 `Apple-Podcasts-Direct.list` 覆盖苹果服务和常见播客托管平台；若某个特定节目使用自己的独立音频域名，它仍可能按照通用规则连接，需要结合 Shadowrocket 请求记录补充该节目实际使用的域名。

如果 ChatGPT 在“全局路由 → 配置”下提示 `unsupported_country_region_territory`，请先更新并重新使用本配置，再完全退出 ChatGPT 后重新打开，并继续选择“使用 Google 登录”。若弹窗仍显示旧错误，请在 iOS 的 Safari 网站数据中删除 `openai` 和 `chatgpt` 记录后重试。若同一节点在全局代理下可用、配置模式不可用，请在 Shadowrocket 请求记录中确认 `auth.openai.com` 命中 `PROXY`，而不是 `DIRECT`。

分流配置只能控制网络出口，不能改变或隐藏 Apple ID / Google 账号地区、付款资料、手机号码、App Store 商店区、系统定位权限或服务商自己的风控记录。对于有地区限制的服务，完整代理规则只能降低因域名漏配而混用大陆直连 IP 的风险，不能保证账号不会被限制。

广告规则不会专门处理 YouTube 视频广告，也不包含 YouTube、Googlevideo 或 YTImg 等正常播放域名。命中广告规则的请求会在设备本地拒绝，不会消耗代理流量。个别 App 如果因误拦出现登录、支付或页面加载异常，应为对应域名增加直连白名单。

闲鱼和淘宝的纯域名广告规则不会封锁 `acs.m.goofish.com`、`acs.m.taobao.com` 等主业务接口，因此不会为了去广告牺牲商品、聊天、登录和下单功能。代价是通过这些第一方接口下发或已经缓存到设备里的开屏广告无法保证完全去除；这是“不安装解密证书”模式的能力边界。

## 检测到代理的国内 App

`DIRECT` 只能让网络请求使用本地出口，不能隐藏 iOS 顶部的 VPN 状态或小火箭创建的隧道。神州租车和部分银行 App 如果直接检测 VPN 是否开启，即使其全部域名均为 `DIRECT`，仍可能显示“检测到手机打开了代理”。

可以使用苹果“快捷指令”中的“设置 VPN”操作自动处理：

1. 新建个人自动化，触发条件选择“App”，勾选神州租车和需要使用的银行 App，选择“已打开”。
2. 添加“设置 VPN”操作，选择断开 Shadowrocket，并设为立即运行。
3. 再创建一条相同 App 的“已关闭”自动化，添加“设置 VPN”并重新连接 Shadowrocket。
4. 如果系统的“设置 VPN”中没有显示 Shadowrocket，可使用 Shadowrocket 的 `shadowrocket://disconnect` 和 `shadowrocket://connect` URL 方案作为备选。

## 安全说明

本仓库不应加入机场订阅地址、节点密码、UUID、私钥或其他敏感凭据。节点订阅应继续在每台设备的 Shadowrocket 中单独管理。
