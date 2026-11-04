---
name: cisco-ios-patterns
description: Cisco IOS 與 IOS-XE 的審查模式，涵蓋 show 指令、設定層級、wildcard mask、ACL 放置位置、介面整潔，以及安全的變更窗口驗證。適用於閱讀、撰寫或審查 Cisco IOS / IOS-XE 設定，或規劃變更窗口時。
metadata:
  origin: community
---

# Cisco IOS Patterns

審查 Cisco IOS 或 IOS-XE 片段、建立變更窗口檢查清單，或是說明如何從路由器或
交換器收集證據而不讓事故更嚴重時，用這個 skill。

## When to Use

- 在計畫中的變更之前，審查 IOS 或 IOS-XE 設定。
- 為故障排除挑選唯讀的 `show` 指令。
- 檢查 ACL 的 wildcard mask 和介面方向。
- 說明全域、介面、路由程序和 line 這幾種設定模式。
- 驗證變更已經進到 running config，而且是刻意儲存的。

## Operating Rules

把 IOS 範例當成模式，不是可以直接貼上去的 production 變更。在真實設備上動手之前，要先確認
平台、介面名稱、目前的設定、rollback 路徑和帶外存取（out-of-band access）。

優先採用這個流程：

1. 用唯讀指令擷取目前狀態。
2. 審查確切的候選設定。
3. 確認管理存取不會被鎖在外面。
4. 在維護窗口內套用最小的變更。
5. 重新讀取狀態，與基準比對，驗證之後才儲存。

## Mode Reference

```text
Router> enable
Router# show running-config
Router# configure terminal
Router(config)# interface GigabitEthernet0/1
Router(config-if)# description UPLINK-TO-CORE
Router(config-if)# no shutdown
Router(config-if)# exit
Router(config)# end
Router# show running-config interface GigabitEthernet0/1
```

`running-config` 是執行中的記憶體。`startup-config` 才是重開機後會留下來的。
不要因為指令被接受了就儲存變更；先驗證行為，
變更核准之後再用 `copy running-config startup-config`。

## Read-Only Collection

```text
show version
show inventory
show processes cpu sorted
show memory statistics
show logging
show running-config | section line vty
show running-config | section interface
show running-config | section router bgp
show ip interface brief
show interfaces
show interfaces status
show vlan brief
show mac address-table
show spanning-tree
show ip route
show ip protocols
show ip access-lists
show route-map
show ip prefix-list
```

設定檔可能含有機密、客戶名稱或私有拓樸時，只收集你需要的那一段，
不要把整份設定丟進工單。

## Wildcard Masks

IOS 的 ACL 和許多路由語句用的是 wildcard mask，不是 subnet mask。

```text
Subnet mask       Wildcard mask
255.255.255.255   0.0.0.0
255.255.255.252   0.0.0.3
255.255.255.0     0.0.0.255
255.255.0.0       0.0.255.255
```

部署之前要審查 wildcard mask。不小心把 subnet mask 當 wildcard 用，
匹配到的流量可能遠比預期的多。

```text
ip access-list extended WEB-IN
  10 permit tcp 192.0.2.0 0.0.0.255 any eq 443
  999 deny ip any any log
```

每個 ACL 的結尾都有隱含的 deny。如果營運目標包含觀察沒命中的流量，
就加一條明確且有 log 的 deny，並確認 log 量是安全的。

## ACL Placement Review

把 ACL 套用到介面之前，先回答這些問題：

- 過濾的是哪個流量方向，`in` 還是 `out`？
- 管理流量是不是來自已知的跳板機或管理子網路？
- 必要的路由、DNS、NTP、監控或
  應用程式流量，有明確的 permit 嗎？
- 有沒有辦法從安全的測試來源看到命中計數器？
- 有 rollback 指令，而且有可用的 console 或帶外路徑嗎？

不要靠移除防火牆或 ACL 的保護來測試連通性。先看計數器、
log 和路由狀態。

## Interface Hygiene

```text
interface GigabitEthernet0/1
 description UPLINK-TO-CORE
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
 switchport trunk native vlan 999
 no shutdown
```

用清楚的 description、明確的 switchport mode，以及有文件記載的 native VLAN。
routed 介面上，不要假設 link 狀態正常就代表轉發是對的，先確認 mask、對端位址和路由程序。

## Change-Window Verification

用跟實際變更相符的前後檢查。

```text
show running-config | section interface GigabitEthernet0/1
show interfaces GigabitEthernet0/1
show logging | include GigabitEthernet0/1|changed state|line protocol
show ip route <prefix>
show ip access-lists <name>
```

路由變更的話，也要在變更前後擷取鄰居狀態和路由表。
ACL 變更的話，要比對來自計畫中測試來源的命中計數器，
不要只靠一般的 ping。

## Anti-Patterns

- 沒有針對該設備的 diff，就直接套用產生出來的設定。
- 在變更後檢查通過之前就儲存設定。
- 在 IOS 預期 wildcard mask 的地方使用 subnet mask。
- 把 ACL 套用到錯誤的介面方向。
- 靠停用 ACL、路由政策或認證來排除故障。
- 沒有清掉機密和拓樸資訊，就把完整設定貼到公開工具裡。

## See Also

- Agent: `network-config-reviewer`
- Agent: `network-troubleshooter`
- Skill: `network-config-validation`
- Skill: `network-interface-health`
