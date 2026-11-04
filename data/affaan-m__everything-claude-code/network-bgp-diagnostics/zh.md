---
name: network-bgp-diagnostics
description: 只做診斷的 BGP 疑難排解模式，涵蓋 neighbor 狀態、路由交換、prefix 政策、AS path 檢查和安全的證據蒐集。BGP neighbor 斷線、路由遺失，或需要檢查 prefix 政策和 AS path 時使用。
metadata:
  origin: community
---

# Network BGP Diagnostics

BGP session 斷線、反覆震盪、已建立但路由遺失，
或廣播了意外的 prefix 時，用這個 skill。預設的流程是唯讀的
證據蒐集；政策和 reset 的動作屬於經過審查的變更時段。

## When to Use

- BGP neighbor 卡在 Idle、Connect、Active、OpenSent 或 OpenConfirm。
- Session 已經 Established，但預期的 prefix 遺失。
- route-map、prefix-list、max-prefix 上限或 AS path 政策，可能正在過濾
  路由。
- 需要 BGP 變更前後的證據。
- 你在審查解析 BGP summary 輸出的自動化。

## Read-Only Triage Flow

1. 找出確切的 neighbor、address family、VRF，以及本地/遠端的 ASN。
2. 擷取 summary 狀態和最後一次 reset 的原因。
3. 證明對 peer 來源位址是可達的。
4. 在假設是傳輸層失敗之前，先檢查路由政策的參照。
5. 平台有支援相關指令時，比較廣播出去、收到和已安裝的路由。

```text
show bgp summary
show bgp neighbors <peer>
show ip route <peer>
show tcp brief | include <peer>|:179
show logging | include BGP|<peer>
show running-config | section router bgp
show ip prefix-list
show route-map
```

設備使用 VRF、IPv6、VPNv4 或 EVPN 時，用平台專屬的 address-family 指令。
不要假設是全域的 IPv4 unicast。

## State Interpretation

| 狀態 | 先檢查 |
| --- | --- |
| Established 且有 prefix 數量 | 路由交換正常；檢查政策和路由表的選擇 |
| Established 但 prefix 為零 | 檢查 inbound 政策、max-prefix、廣播的路由和 AFI/SAFI |
| Active | TCP session 沒有完成；檢查路由、來源、ACL 和 peer 的可達性 |
| Connect | TCP 連線進行中；檢查路徑和遠端的 listener |
| OpenSent/OpenConfirm | TCP 正常；檢查 ASN、驗證、計時器、能力和紀錄 |
| Idle | Neighbor 可能被停用、缺少設定、被政策擋住，或處於 backoff 計時器 |

## Transport Checks

```text
ping <peer> source <local-source>
traceroute <peer> source <local-source>
show ip route <peer>
show bgp neighbors <peer> | include BGP state|Last reset|Local host|Foreign host
```

如果 peer 的來源是 loopback，要確認雙向都能路由到
loopback 位址，而且 neighbor 設定用的是預期的 update source。

不要把停用 ACL 或防火牆政策當成診斷的捷徑。先讀命中
計數器、紀錄和路徑狀態。

## Route Policy Checks

```text
show bgp neighbors <peer> advertised-routes
show bgp neighbors <peer> routes
show ip prefix-list <name>
show route-map <name>
show bgp <prefix>
```

有些平台需要額外的設定，`received-routes` 才能使用。事件分流期間，
除非操作員核准，否則不要加那個設定。

## AS Path And Prefix Review

```text
show bgp regexp _65001_
show bgp regexp ^65001$
show bgp <prefix>
show bgp neighbors <peer> advertised-routes | include Network|Path|<prefix>
```

AS-path 的 regex 要小心用。`_65001_` 會把 AS 65001 當成一個 token 來比對。單純的
`65001` 可能會比對到更長的 ASN 或不相關的文字。

## Parser Pattern

```python
import re
from typing import Any

BGP_SUMMARY_RE = re.compile(
    r"^(?P<neighbor>\d{1,3}(?:\.\d{1,3}){3})\s+"
    r"(?P<version>\d+)\s+"
    r"(?P<remote_as>\d+)\s+"
    r"(?P<msg_rcvd>\d+)\s+"
    r"(?P<msg_sent>\d+)\s+"
    r"(?P<table_version>\d+)\s+"
    r"(?P<input_queue>\d+)\s+"
    r"(?P<output_queue>\d+)\s+"
    r"(?P<uptime>\S+)\s+"
    r"(?P<state_or_prefixes>\S+)$",
    re.M,
)

def parse_bgp_summary(raw: str) -> list[dict[str, Any]]:
    rows = []
    for match in BGP_SUMMARY_RE.finditer(raw):
        state_or_prefixes = match.group("state_or_prefixes")
        if state_or_prefixes.isdigit():
            state = "Established"
            prefixes_received = int(state_or_prefixes)
        else:
            state = state_or_prefixes
            prefixes_received = None
        rows.append({
            "neighbor": match.group("neighbor"),
            "remote_as": int(match.group("remote_as")),
            "state": state,
            "prefixes_received": prefixes_received,
            "uptime": match.group("uptime"),
        })
    return rows
```

有結構化的解析器輸出時就偏好使用它，但要把原始輸出和事件紀錄一起保存，
因為 BGP summary 的格式會隨平台和 address family 而異。

## Change-Window Only

這些動作會影響路由，不應該被建議成自動診斷：

- 清除 BGP session。
- 變更 neighbor 的驗證、計時器、update source、route-map 或
  prefix-list。
- 啟用額外的 received-route 儲存。
- 放寬防火牆、ACL 或 control-plane 政策。

如果 reset 已經核准，偏好用平台支援的、破壞最小的 soft 或 route-refresh 選項，
並把它為什麼安全寫清楚。

## Anti-Patterns

- 假設 `Active` 一定代表遠端斷了。
- 忽略 VRF、address family 或 update-source 的差異。
- 使用沒有 token 邊界的大範圍 AS-path regex。
- 還沒讀最後一次 reset 的原因和紀錄，就 hard reset peer。
- 把沒有 `received-routes` 輸出，當成沒有收到任何路由的證明。

## See Also

- Skill: `cisco-ios-patterns`
- Skill: `network-config-validation`
- Skill: `network-interface-health`
