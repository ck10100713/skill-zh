---
name: network-interface-health
description: 診斷路由器、交換器和 Linux 主機上的介面錯誤、丟包、CRC、duplex 不一致、震盪、速度協商問題和計數器趨勢。介面出現錯誤、丟包、CRC、震盪，或 duplex 或速度不一致時使用。
metadata:
  origin: community
---

# Network Interface Health

網路症狀可能是由實體連線、交換器
埠、線材、收發器、duplex 設定或擁塞的介面造成時，用這個 skill。

## When to Use

- 主機或 VLAN 有封包遺失、延遲飆高或時好時壞的連線。
- 交換器或路由器的介面出現 CRC、runt、giant、丟包、reset 或震盪。
- 更換硬體之前，需要比對連線兩端。
- 變更時段需要變更前/後的介面計數器證據。
- 監控回報 `ifInErrors`、`ifOutErrors` 或 `ifOutDiscards` 在上升。

## How It Works

介面計數器是證據，但趨勢比絕對數字重要。先擷取基準，等一個量測
區間，再擷取一次，然後比較增量。

```text
show interfaces <interface>
show interfaces <interface> status
show logging | include <interface>|changed state|line protocol
```

在 Linux 主機上：

```text
ip -s link show <interface>
ethtool <interface>
ethtool -S <interface>
```

## Counter Reference

| 計數器 | 意義 | 常見原因 |
| --- | --- | --- |
| CRC | 收到的 frame checksum 驗證失敗 | 壞掉的線材、髒掉的光纖、壞掉的光模組、duplex 不一致 |
| input errors | 接收端錯誤的總和 | 下結論之前先看子計數器 |
| runts | 小於乙太網路最小尺寸的 frame | duplex 不一致、碰撞域、故障的網卡 |
| giants | 比預期 MTU 更大的 frame | MTU 不一致或 jumbo frame 邊界 |
| input drops | 設備無法接受進來的封包 | 突發流量、超額訂閱、CPU 路徑、佇列壓力 |
| output drops | 出口佇列丟棄封包 | 擁塞、QoS 政策、上行頻寬不足 |
| resets | 介面硬體 reset | 震盪、keepalive、driver、光模組、電源 |
| collisions | 乙太網路碰撞計數器 | 半雙工或協商不一致 |

## Diagnosis Flow

### CRCs Or Input Errors

1. 確認計數器正在增加，而不只是歷史數字。
2. 檢查連線兩端。接收端的錯誤通常指向抵達那一側的
   訊號，不一定是回報錯誤的那個埠。
3. 更換跳線，或清潔/更換光纖和光模組。
4. 確認兩端的速度/duplex 設定一致。
5. 檢查同一時間點前後的紀錄有沒有震盪事件。

### Drops

1. 把 input drops 和 output drops 分開。
2. 比較介面速率和容量。
3. 檢查 QoS 政策、佇列計數器，以及這條連線是不是超額訂閱的
   上行。
4. 佇列調校是次要的。先證明連線是不是真的擁塞。

### Duplex And Speed

現代乙太網路連線在兩端都支援時，偏好用自動協商。如果
有一端必須固定，就把兩端都明確設定，並記錄原因。絕不要
一端固定速度/duplex，另一端卻用 auto。

```text
show interfaces <interface> | include duplex|speed
```

## Safe Parser Example

從一個標頭切到下一個標頭，來切出每個介面區塊。不要用任意的
字元視窗；大的介面區塊可能造成計數器被漏掉，或被
歸到錯誤的埠。

```python
import re
from typing import Any

HEADER_RE = re.compile(
    r"^(?P<name>\S+) is (?P<status>(?:administratively )?down|up), "
    r"line protocol is (?P<protocol>up|down)",
    re.I | re.M,
)
ERROR_RE = re.compile(r"(?P<input>\d+) input errors, (?P<crc>\d+) CRC", re.I)
DROP_RE = re.compile(r"(?P<output>\d+) output errors", re.I)
DUPLEX_RE = re.compile(r"(?P<duplex>Full|Half|Auto)-duplex,\s+(?P<speed>[^,]+)", re.I)

def parse_show_interfaces(raw: str) -> list[dict[str, Any]]:
    headers = list(HEADER_RE.finditer(raw))
    interfaces = []
    for index, header in enumerate(headers):
        end = headers[index + 1].start() if index + 1 < len(headers) else len(raw)
        block = raw[header.start():end]
        errors = ERROR_RE.search(block)
        drops = DROP_RE.search(block)
        duplex = DUPLEX_RE.search(block)
        interfaces.append({
            "name": header.group("name"),
            "status": header.group("status"),
            "protocol": header.group("protocol"),
            "duplex": duplex.group("duplex") if duplex else "unknown",
            "speed": duplex.group("speed").strip() if duplex else "unknown",
            "input_errors": int(errors.group("input")) if errors else 0,
            "crc_errors": int(errors.group("crc")) if errors else 0,
            "output_errors": int(drops.group("output")) if drops else 0,
        })
    return interfaces
```

## Examples

### CRCs On One Switch Port

1. 擷取本地埠的計數器。
2. 擷取連接的遠端埠的計數器。
3. 在改路由或防火牆規則之前，先換線材或光模組。
4. 記錄基準之後，才清除計數器。
5. 隔固定的區間後再檢查一次。

### Internet Slow But LAN Is Fine

1. 檢查 WAN 介面的丟包/錯誤。
2. 檢查 LAN 上行的使用率和 output drops。
3. 如果 WAN 連線乾淨但吞吐量還是低，就檢查閘道的 CPU。
4. 在怪上游服務之前，先比較有線和無線的測試結果。

## Anti-Patterns

- 還沒存基準就先清除計數器。
- 只看連線的其中一端。
- 沒有時間窗口，就假設所有歷史 CRC 都是現在的問題。
- 一端用自動協商，另一端卻用固定速度/duplex。
- 還沒檢查擁塞，就把 output drops 當成線材問題。

## See Also

- Agent: `network-troubleshooter`
- Skill: `network-config-validation`
- Skill: `homelab-network-setup`
