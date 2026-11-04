---
name: homelab-network-readiness
description: homelab 的 VLAN 分段、本地 DNS 過濾（Pi-hole、AdGuard Home）與 WireGuard 類遠端存取的準備度檢查清單。規劃或審查家用網路變更時使用，例如把單一扁平網路切成 trusted、IoT、guest 或 management VLAN、把 DHCP 搬到本地 resolver，或加 VPN 存取，要在動 router、firewall、DHCP 或 VPN 設定之前用。
metadata:
  origin: community
---

# Homelab Network Readiness

在改動家用或小型實驗室網路之前用這個 skill，特別是同時牽涉 VLAN、
Pi-hole 或其他本地 DNS resolver、firewall 規則，以及遠端 VPN 存取的情況。

這是規劃與審查用的 skill。除非目標平台、現有拓撲、回復路徑、console 存取方式
和維護時段全部都已經確定，否則不要把它變成可以直接複製貼上的 router、
firewall 或 VPN 設定。

## When to Use

- 準備把扁平網路切成 trusted、IoT、guest、server 或
  management VLAN。
- 把 DHCP client 搬到 Pi-hole、AdGuard Home、Unbound 或其他本地 DNS
  resolver。
- 加入 WireGuard、Tailscale、ZeroTier、OpenVPN 或 router 內建的 VPN 存取。
- 檢查某個 homelab 變更會不會讓操作者被鎖在 gateway、
  switch、access point、DNS 伺服器或 VPN 伺服器之外。
- 把一個不太正式的家用網路想法，變成有驗證證據的分階段遷移計畫。

## Safety Rules

- 第一次回答要保持唯讀：盤點、風險、分階段計畫、驗證，
  還有回復方式。
- 不要把 gateway 管理介面、DNS resolver、SSH、NAS console 或 VPN
  管理介面直接暴露到公網。
- 沒有確認平台、也沒有回復程序，就不要提供 firewall、NAT、VLAN、DHCP 或 VPN 指令。
- 在改 management VLAN、trunk port、firewall 預設政策，或 DHCP/DNS 設定之前，
  一定要有帶外（out-of-band）或人在現場的 console 存取。
- 在把整個網路指向新的 DNS resolver 或 VPN 路由之前，
  要先保留一條能回到網際網路的可用路徑。
- 在操作者明確選擇別的做法之前，把 IoT、guest、攝影機和實驗室伺服器網路
  都當成不同的信任區。

## Required Inventory

在給出實作步驟之前先收集這些資訊：

| 範圍 | 問題 |
| --- | --- |
| Internet edge | modem 或 ONT 是什麼？ISP 的 router 是 bridge 模式，還是仍然在做路由？ |
| Gateway | 誰負責路由、firewall、DHCP，以及終結 VPN？ |
| Switching | 哪些 switch port 是 uplink、access port、trunk，或是 unmanaged？ |
| Wi-Fi | 哪些 SSID 對應到哪些網路？AP 是有線還是 mesh？ |
| Addressing | 現在有哪些子網？哪些網段會跟 VPN 站點衝突？ |
| DNS/DHCP | 現在是哪個服務在發 lease 和 resolver 位址？ |
| Management | 變更之後，操作者要怎麼連到 gateway、switch 和 AP？ |
| Recovery | 如果 DNS、DHCP、VLAN 或 VPN 路由壞了，本地端能回復什麼？ |

## VLAN And Trust-Zone Plan

先從意圖開始，不要從廠商語法開始。

| 區域 | 典型內容 | 預設政策 |
| --- | --- | --- |
| Trusted | 筆電、手機、管理工作站 | 只有需要時才能存取共用服務和管理介面 |
| Servers | NAS、Home Assistant、實驗室主機、DNS resolver | 只接受來自 trusted client 的狹窄 inbound 流量 |
| IoT | 電視、智慧插座、攝影機、喇叭 | 只有網際網路存取，另外只開明確列出的例外 |
| Guest | 訪客裝置 | 只能上網，連不到 LAN |
| Management | Gateway、switch、AP、controller | 只能從 trusted 的管理裝置連線 |
| VPN | 遠端 client | 存取範圍跟 trusted client 一樣或更窄 |

在建議 VLAN ID 或子網之前，先確認：

1. Gateway 支援 inter-VLAN routing 和 firewall 規則。
2. Switch 支援需要的 tagged 與 untagged port 行為。
3. AP 可以把 SSID 對應到 VLAN。
4. 操作者知道變更期間自己是從哪個 port 連線進來的。
5. 改了 trunk 和 SSID 之後，management 網路仍然連得到。

## DNS Filtering Readiness

Pi-hole 或其他本地 resolver 應該當成一個依賴來導入，不要變成
單點故障。

1. 在把 resolver 放進 DHCP option 之前，先給它保留一個固定位址。
2. 確認它能解析公開 DNS 和本地的 `home.arpa` 名稱。
3. 保留 gateway 或第二台 resolver 當作暫時的 fallback。
4. 在改每個 DHCP scope 之前，先拿一台 client 或一個 VLAN 測試。
5. 記下哪些網路可以繞過過濾，以及原因。
6. 檢查封鎖規則不會弄壞 captive portal、公司 VPN、韌體更新，
   或醫療/保全裝置。

有用的驗證證據：

```text
Client gets expected DHCP lease
Client receives expected DNS resolver
Public DNS lookup succeeds
Local home.arpa lookup succeeds
Blocked test domain is blocked only where intended
Gateway and DNS admin interfaces are not reachable from guest or IoT networks
```

## Remote Access Readiness

WireGuard 類的存取，要在產生金鑰或開 port 之前，先決定 VPN 可以連到什麼。

| 模式 | 適用時機 | 風險備註 |
| --- | --- | --- |
| Split tunnel 到單一子網 | 遠端管理 NAS 或實驗室主機 | 路由清單要保持狹窄 |
| Split tunnel 到 trusted 服務 | 用 IP 或 DNS 存取特定應用 | 需要精準的 firewall 規則 |
| Full tunnel | 不受信任的網路或出差 | 頻寬用得更多，DNS 也要負責 |
| Overlay VPN | 用身分控制讓遠端存取更簡單 | 還是需要檢查 ACL |

在操作者確認以下事項之前，不要建議做 port forwarding：

- VPN endpoint 已經打過 patch，而且有人持續維護。
- 轉發的 port 只會到 VPN 服務，不會到管理介面。
- 已經搞清楚 dynamic DNS、公網 IP 行為，以及 ISP 有沒有 CGNAT。
- 可以撤銷 peer 的金鑰，不用把整個網路重建。
- 可以用 log 或連線狀態確認誰在什麼時候連線。

## Change Sequence

偏好小而可回復的變更：

1. 把目前的拓撲、IP 規劃、DHCP 設定、DNS 設定和
   firewall 規則做個快照。
2. 為 gateway、DNS、controller、AP、NAS 和
   VPN endpoint 保留基礎設施用的位址。
3. 建立新的區域或 VLAN，先不要搬任何關鍵裝置。
4. 搬一台測試用 client，驗證 DHCP、DNS、路由、上網和封鎖
   行為。
5. 為必要的流量加上狹窄的 firewall 例外。
6. 搬一組低風險的裝置。
7. 加入 VPN 存取，路由和 firewall 政策要用能滿足需求的最窄設定。
8. 記錄最終狀態、已知的例外，以及回復用的指令或 UI 步驟。

## Review Checklist

- 每個網路都有存在的理由和清楚的信任邊界。
- 從 guest、IoT 或公網都連不到任何管理介面。
- DNS 掛掉不會讓操作者失去在本地回復的能力。
- DHCP scope 的變更在大範圍推行前，先在一台 client 上測過。
- VPN client 只拿到它們需要的路由和 DNS 設定。
- 區域之間的 firewall 規則是預設拒絕，再加上有名字的例外。
- 操作者仍然連得到 gateway、switch、AP、DNS 和 VPN 的管理介面。
- 回復方式要用所選平台 UI 或 CLI 的同一套用語寫下來。

## Anti-Patterns

- 在還不知道哪些 switch port 和 SSID 承載哪些 VLAN 之前，就先做網路分段。
- 把管理工作站移出唯一連得到的 management 網路。
- 在測 fallback DNS 之前，就把所有 DHCP scope 指向 Pi-hole。
- 把 NAS、DNS、router 或 hypervisor 的管理介面直接公開到
  網際網路。
- 把 VPN 存取當成等同於完整的 trusted LAN 存取。
- 暫時加了 allow-all 的 firewall 規則，然後忘了移除。
- 沒確認確切的平台語法，就照抄別的廠商或別的韌體版本的指令。

## See Also

- Skill: `homelab-network-setup`
- Skill: `network-config-validation`
- Skill: `network-interface-health`
