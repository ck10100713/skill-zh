---
name: homelab-network-setup
description: 家用與 homelab 網路的實用規劃，涵蓋 gateway、switch、access point、IP 網段、DHCP 保留位址、DNS、佈線，以及新手常犯的錯誤。規劃或修正家用或 homelab 網路時使用，包含 gateway、switch、AP、IP 網段、DHCP、DNS 或佈線。
metadata:
  origin: community
---

# Homelab Network Setup

用這個 skill 設計一個家用或小型實驗室網路，讓它可以長大，
不用整個砍掉重建。

## When to Use

- 規劃新的家用網路，或重新設計只靠 ISP router 的環境。
- 決定 gateway、switch 和 access point 各自的角色。
- 設計 IP 網段、DHCP scope、固定保留位址和 DNS。
- 為之後的 VLAN、Pi-hole、NAS、實驗室伺服器或 VPN 存取做準備。
- 排查新網路的問題，例如 double NAT、Wi-Fi 不穩，或伺服器位址一直變。

## How It Works

先把裝置的角色分開：

```text
Internet
  |
Modem or ONT
  |
Gateway or router      NAT, firewall, DHCP, DNS, inter-VLAN routing
  |
Managed switch         wired clients, AP uplinks, optional VLAN trunks
  |
Access points          Wi-Fi only; ideally wired backhaul
Servers and NAS        stable addresses, DNS names, monitoring
Clients and IoT        DHCP pools, isolated later if VLANs are available
```

挑 gateway 要看操作者的實際狀況，不要只看功能清單：

| 選項 | 最適合 | 備註 |
| --- | --- | --- |
| ISP router | 只需要基本上網 | 可控性有限，VLAN 支援常常很差 |
| UniFi gateway | 有管理的家用網路 | UI 好用，但會被生態系綁住 |
| OPNsense 或 pfSense | 彈性高的 homelab | VLAN、firewall、VPN 和 DNS 的控制都很強 |
| MikroTik | 進階網路使用者 | 功能強，但很容易設錯 |
| Linux router | 愛玩的人 | 當主要 gateway 之前，先寫好回復方式 |

## IP Plan

如果預期會用 VPN，就避開最常見的預設值 `192.168.1.0/24`。
它常常跟飯店、辦公室和 ISP router 的網段衝突。

```text
Example small homelab plan:

192.168.10.0/24  trusted clients
192.168.20.0/24  IoT and media devices
192.168.30.0/24  servers and NAS
192.168.40.0/24  guest Wi-Fi
192.168.99.0/24  network management

Gateway convention: .1
Infrastructure reservations: .2 through .49
Dynamic DHCP pool: .50 through .240
Spare room: .241 through .254
```

本地名稱用 `home.arpa`。它是保留給家用網路的，也避開了
`home.lan` 這類臨時取名會有的外洩或衝突問題。

```text
nas.home.arpa
pihole.home.arpa
gateway.home.arpa
switch-01.home.arpa
```

## DHCP And DNS

- 凡是你會 SSH 進去、加書籤、監控，或當成服務對外提供的東西，都用 DHCP 保留位址。
- 在刻意部署本地 resolver 之前，先把 gateway 當成 DNS 發出去。
- 如果用 Pi-hole 或其他 DNS 過濾器，先幫它做保留位址，再把
  DHCP 的 DNS 選項指到那個位址。
- 每個子網留一小段固定/保留範圍，這樣換裝置時才不會跟動態 lease 撞在一起。

## Cabling And Wi-Fi

- 能拉網路線的話，AP 的 backhaul 優先選有線，不要用 mesh。
- 預算允許的話，AP 和攝影機用 PoE switch。
- 每條線的兩端都貼標籤，並維護一份簡單的 port 對照表。
- 如果常停電，把 gateway、switch、DNS 伺服器和 NAS 接在 UPS 上。

## Examples

### Beginner Upgrade

目標：保留 ISP router，但讓小型實驗室穩定下來。

1. 幫 NAS、Pi 和所有 SSH 主機設定 DHCP 保留位址。
2. 把本地名稱改成 `home.arpa`。
3. 關掉次要 router 或 AP 上重複的 DHCP 伺服器。
4. 主要的 AP 改用有線連接，不要靠無線 backhaul。

### VLAN-Ready Plan

目標：為之後的網路分段做好準備，但先不啟用。

1. 為 trusted、IoT、servers、guest 和 management 各挑一個互不重疊的 /24 網段。
2. 每個子網都把 .1 留給 gateway，.2-.49 留給基礎設施。
3. 買支援 VLAN 和 inter-VLAN firewall 規則的 gateway 與 switch。
4. 記錄之後哪些 SSID 和 switch port 會對應到各個網路。

## Anti-Patterns

- 沒有理由也沒有文件說明的 double NAT。
- 計畫要用 VPN，卻用 `192.168.1.0/24`。
- NAS、Pi-hole、Home Assistant 或其他服務主機用動態位址。
- 把消費級 router 拿來當 AP，卻沒關掉它的 DHCP 伺服器。
- 攝影機、智慧插座、筆電和伺服器全部擠在同一個信任邊界的扁平網路。

## See Also

- Skill: `network-interface-health`
- Skill: `network-config-validation`
