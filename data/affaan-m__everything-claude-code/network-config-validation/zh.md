---
name: network-config-validation
description: 路由器和交換器設定的部署前檢查，包括危險指令、重複位址、子網路重疊、過期的參照、管理平面風險，以及 IOS 風格的安全衛生。在部署之前審查路由器或交換器設定時使用。
metadata:
  origin: community
---

# Network Config Validation

在變更時段之前，或自動化執行碰到正式環境設備之前，用這個 skill 審查網路設定。

## When to Use

- 部署之前審查 Cisco IOS 或 IOS-XE 風格的設定片段。
- 稽核由腳本或範本產生的設定。
- 找危險指令、重複的 IP 位址或子網路重疊。
- 檢查 ACL、route-map、prefix-list 或 line 政策是不是被參照了
  卻沒有定義。
- 為網路自動化建立輕量的 pre-flight 腳本。

## How It Works

把設定驗證當成分層的證據，不要當成完整的解析器。Regex
檢查拿來做 pre-flight 警告很有用，但最終核准仍然需要
網路工程師審查意圖、平台語法和回滾步驟。

驗證順序：

1. 破壞性指令。
2. 憑證和管理平面的暴露。
3. 重複的位址和重疊的子網路。
4. 對 ACL、route-map、prefix-list 和介面的過期參照。
5. NTP、時間戳記、遠端紀錄和 banner 這類營運衛生。

## Dangerous Command Detection

```python
import re

DANGEROUS_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\breload\b", re.I), "reload causes downtime"),
    (re.compile(r"\berase\s+(startup|nvram|flash)", re.I), "erases persistent storage"),
    (re.compile(r"\bformat\b", re.I), "formats a device filesystem"),
    (re.compile(r"\bno\s+router\s+(bgp|ospf|eigrp)\b", re.I), "removes a routing process"),
    (re.compile(r"\bno\s+interface\s+\S+", re.I), "removes interface configuration"),
    (re.compile(r"\baaa\s+new-model\b", re.I), "changes authentication behavior"),
    (re.compile(r"\bcrypto\s+key\s+(zeroize|generate)\b", re.I), "changes device SSH keys"),
]

def find_dangerous_commands(lines: list[str]) -> list[dict[str, str | int]]:
    findings = []
    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()
        for pattern, reason in DANGEROUS_PATTERNS:
            if pattern.search(stripped):
                findings.append({
                    "line": line_number,
                    "command": stripped,
                    "reason": reason,
                })
    return findings
```

## Duplicate IPs And Subnet Overlaps

```python
import ipaddress
import re
from collections import Counter

IP_ADDRESS_RE = re.compile(
    r"^\s*ip address\s+"
    r"(?P<ip>\d{1,3}(?:\.\d{1,3}){3})\s+"
    r"(?P<mask>\d{1,3}(?:\.\d{1,3}){3})\b",
    re.I | re.M,
)

def extract_interfaces(config: str) -> list[dict[str, str]]:
    results = []
    current = None
    for line in config.splitlines():
        if line.startswith("interface "):
            current = line.split(maxsplit=1)[1]
            continue
        match = IP_ADDRESS_RE.match(line)
        if current and match:
            ip = match.group("ip")
            mask = match.group("mask")
            network = ipaddress.ip_interface(f"{ip}/{mask}").network
            results.append({"interface": current, "ip": ip, "network": str(network)})
    return results

def find_duplicate_ips(config: str) -> list[str]:
    ips = [entry["ip"] for entry in extract_interfaces(config)]
    counts = Counter(ips)
    return sorted(ip for ip, count in counts.items() if count > 1)

def find_subnet_overlaps(config: str) -> list[tuple[str, str]]:
    networks = [ipaddress.ip_network(entry["network"]) for entry in extract_interfaces(config)]
    overlaps = []
    for index, left in enumerate(networks):
        for right in networks[index + 1:]:
            if left.overlaps(right):
                overlaps.append((str(left), str(right)))
    return overlaps
```

## Management-Plane Checks

依區段解析 VTY 區塊，這樣 access-class 檢查才不會跨到不相關的
行。

```python
import re

def iter_blocks(config: str, starts_with: str) -> list[str]:
    blocks = []
    current: list[str] = []
    for line in config.splitlines():
        if line.startswith(starts_with):
            if current:
                blocks.append("\n".join(current))
            current = [line]
            continue
        if current:
            if line and not line.startswith(" "):
                blocks.append("\n".join(current))
                current = []
            else:
                current.append(line)
    if current:
        blocks.append("\n".join(current))
    return blocks

def check_vty_blocks(config: str) -> list[str]:
    issues = []
    for block in iter_blocks(config, "line vty"):
        if re.search(r"transport\s+input\s+.*telnet", block, re.I):
            issues.append("VTY allows Telnet; require SSH only.")
        if not re.search(r"\baccess-class\s+\S+\s+in\b", block, re.I):
            issues.append("VTY block has no inbound access-class source restriction.")
        if not re.search(r"\bexec-timeout\s+\d+\s+\d+\b", block, re.I):
            issues.append("VTY block has no explicit exec-timeout.")
    return issues
```

## Security Hygiene Checks

```python
SECURITY_PATTERNS = [
    (re.compile(r"\bsnmp-server community\s+(public|private)\b", re.I),
     "default SNMP community configured"),
    (re.compile(r"\bsnmp-server community\s+\S+", re.I),
     "SNMPv2 community string configured; prefer SNMPv3 authPriv"),
    (re.compile(r"\bip ssh version 1\b", re.I),
     "SSH version 1 enabled"),
    (re.compile(r"\benable password\b", re.I),
     "enable password is present; use enable secret"),
    (re.compile(r"\busername\s+\S+\s+password\b", re.I),
     "local username uses password instead of secret"),
]

BEST_PRACTICE_PATTERNS = [
    (re.compile(r"\bntp server\b", re.I), "NTP server"),
    (re.compile(r"\bservice timestamps\b", re.I), "log timestamps"),
    (re.compile(r"\blogging\s+\S+", re.I), "logging destination or buffer"),
    (re.compile(r"\bsnmp-server group\s+\S+\s+v3\s+priv\b", re.I), "SNMPv3 authPriv group"),
    (re.compile(r"\bbanner\s+(login|motd)\b", re.I), "login banner"),
]

def check_security(config: str) -> list[str]:
    return [message for pattern, message in SECURITY_PATTERNS if pattern.search(config)]

def check_missing_hygiene(config: str) -> list[str]:
    return [
        f"Missing {description}"
        for pattern, description in BEST_PRACTICE_PATTERNS
        if not pattern.search(config)
    ]
```

## Examples

### Change-Window Preflight

1. 對要貼上去的確切片段執行危險指令檢查。
2. 對完整的候選設定執行重複 IP 和子網路重疊檢查。
3. 確認每個被參照的 ACL、route-map 和 prefix-list 都存在。
4. 在任何管理平面變更之前，確認回滾指令和頻外存取。

### Automation Preflight

在 Netmiko、NAPALM、Ansible 或廠商 API 自動化推送產生的設定之前，
把驗證當成會擋住流程的關卡。遇到危險指令和憑證要 fail closed。
超出這次變更範圍的最佳實踐缺口，只發出警告。

## Anti-Patterns

- 把 regex 驗證當成設備的解析器。
- 沒有 dry-run 的 diff，就套用產生出來的設定。
- 把 SNMPv2 community string 當成監控的必要條件來建議。
- 用可能意外跨越不相關區段的 regex 來檢查 VTY 區塊。
- 用停用 ACL 來測試防火牆行為，而不是去讀計數器/紀錄。

## See Also

- Agent: `network-config-reviewer`
- Agent: `network-troubleshooter`
- Skill: `network-interface-health`
