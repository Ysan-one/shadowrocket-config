# Shadowrocket 配置

这是用于 iPhone、iPad 和 Apple Vision Pro 的 Shadowrocket 远程配置。

## 配置地址

```text
https://raw.githubusercontent.com/Ysan-one/shadowrocket-config/main/Shadowrocket.conf
```

## 在设备中安装

1. 复制上面的配置地址。
2. 打开 Shadowrocket，进入“配置”。
3. 点击右上角“+”，粘贴地址并下载。
4. 点击下载后的 `Shadowrocket.conf`，选择“使用配置”。
5. 在 Shadowrocket 的“设置 → 自动更新 → 配置”中开启自动后台更新。
6. 在苹果系统“设置 → 通用 → 后台 App 刷新”中允许 Shadowrocket 后台刷新。

## 使用原则

- 广告和跟踪域名继续使用 `REJECT`。
- GFW 黑名单中的站点使用 `PROXY`。
- ChatGPT/OpenAI 的登录、接口、静态资源、WebSocket、iOS 设备校验和 Google 登录链路统一使用 `PROXY` 与远程 DNS，避免规则模式下混用大陆直连 IP 和代理 IP。
- iOS 系统认证网页会话不再旁路 Shadowrocket；`auth.openai.com`、`setup.auth.openai.com`、`auth0.openai.com` 以及当前 Cloudflare 别名均有最优先代理兜底。
- Claude/Anthropic 的登录、推理、文件、功能开关、连接器与 WebSocket 使用父域名级 `PROXY` 保护，并启用远程 DNS；新增的 Anthropic 子域名也会自动匹配。
- Gemini、Google 登录及常用图片、视频和资源域名统一使用 `PROXY` 与远程 DNS。
- Apple Intelligence 和 Siri 的官方核心域名走 `PROXY`，并使用远程 `RULE-SET` 补充更新；使用相关功能时请在 Shadowrocket 首页选择美国节点。
- Apple TV、App Store、苹果系统更新以及 iCloud 照片和文件内容使用 `DIRECT`，避免大流量下载消耗代理额度。
- 国内 App 开屏广告和常见广告 SDK 使用 AdvertisingLite 远程规则在本机 `REJECT`，不启用 MITM、不安装解密证书。
- 未匹配的站点最终使用 `DIRECT`。
- 百度、哔哩哔哩、高德、淘宝、微信、京东、国内视频、夸克等常用国内服务设置了显式 `DIRECT` 保护。

Apple AI 远程规则由 `xpdigital/Apple-Rule` 维护。配置在远程列表前加入了 Apple TV、App Store、系统更新和 iCloud 大流量域名的直连保护，避免第三方列表把这些内容错误地送入代理。

这里的 Apple TV 直连指苹果自有系统和内容服务。Apple TV 上的 YouTube、Netflix 等第三方应用仍会按照各自域名的规则决定直连或代理。

如果 ChatGPT 在“全局路由 → 配置”下提示 `unsupported_country_region_territory`，请先更新并重新使用本配置，再完全退出 ChatGPT 后重新打开，并继续选择“使用 Google 登录”。若弹窗仍显示旧错误，请在 iOS 的 Safari 网站数据中删除 `openai` 和 `chatgpt` 记录后重试。若同一节点在全局代理下可用、配置模式不可用，请在 Shadowrocket 请求记录中确认 `auth.openai.com` 命中 `PROXY`，而不是 `DIRECT`。

分流配置只能控制网络出口，不能改变或隐藏 Apple ID / Google 账号地区、付款资料、手机号码、App Store 商店区、系统定位权限或服务商自己的风控记录。对于有地区限制的服务，完整代理规则只能降低因域名漏配而混用大陆直连 IP 的风险，不能保证账号不会被限制。

广告规则不会专门处理 YouTube 视频广告，也不包含 YouTube、Googlevideo 或 YTImg 等正常播放域名。命中广告规则的请求会在设备本地拒绝，不会消耗代理流量。个别 App 如果因误拦出现登录、支付或页面加载异常，应为对应域名增加直连白名单。

## 安全说明

本仓库不应加入机场订阅地址、节点密码、UUID、私钥或其他敏感凭据。节点订阅应继续在每台设备的 Shadowrocket 中单独管理。
