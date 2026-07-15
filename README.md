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
- 未匹配的站点最终使用 `DIRECT`。
- 百度、哔哩哔哩、高德、淘宝、微信、京东、国内视频、夸克等常用国内服务设置了显式 `DIRECT` 保护。

## 安全说明

本仓库不应加入机场订阅地址、节点密码、UUID、私钥或其他敏感凭据。节点订阅应继续在每台设备的 Shadowrocket 中单独管理。
