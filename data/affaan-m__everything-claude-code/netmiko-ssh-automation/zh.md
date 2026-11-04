---
name: netmiko-ssh-automation
description: 安全的 Python Netmiko 模式，涵蓋唯讀蒐集、有上限的批次 SSH、TextFSM 解析、有防護的設定變更、逾時，以及網路自動化的錯誤處理。用 Python Netmiko 自動化存取網路設備時使用，不論是蒐集狀態還是推送有防護的設定變更。
metadata:
  origin: community
---

# Netmiko SSH Automation

撰寫或審查用 Netmiko 連線到網路設備的 Python 自動化時，用這個 skill。預設路徑要保持唯讀；
設定變更需要另外的變更時段、同儕審查和回滾計畫。

## When to Use

- 跨路由器、交換器或防火牆蒐集 `show` 指令的輸出。
- 建一個小型的稽核腳本，蒐集介面、路由或設定的證據。
- 替網路 SSH 腳本加上逾時和例外處理。
- 有範本時，用 TextFSM 解析指令輸出。
- 在自動化碰到正式環境設備之前先審查。

## Safety Defaults

- 從唯讀的 `send_command()` 蒐集開始。
- 讓清單小而明確；不要掃整個位址範圍。
- 用環境變數、vault 或 `getpass`；絕對不要寫死憑證。
- 設定連線逾時和讀取逾時。
- 限制並行數量，免得舊設備被壓垮。
- 在 `send_config_set()` 之前，要求明確的操作員旗標。
- 變更還沒驗證並核准之前，不要呼叫 `save_config()`。

## Read-Only Connection Pattern

```python
import os
from getpass import getpass
from netmiko import ConnectHandler
from netmiko.exceptions import (
    NetmikoAuthenticationException,
    NetmikoTimeoutException,
    ReadTimeout,
)

device = {
    "device_type": "cisco_ios",
    "host": "192.0.2.10",
    "username": os.environ.get("NETMIKO_USERNAME") or input("Username: "),
    "password": os.environ.get("NETMIKO_PASSWORD") or getpass("Password: "),
    "secret": os.environ.get("NETMIKO_ENABLE_SECRET"),
    "conn_timeout": 10,
    "auth_timeout": 20,
    "banner_timeout": 15,
    "read_timeout_override": 30,
}

try:
    with ConnectHandler(**device) as conn:
        if device.get("secret") and not conn.check_enable_mode():
            conn.enable()
        output = conn.send_command("show ip interface brief", read_timeout=30)
        print(output)
except NetmikoAuthenticationException:
    print("Authentication failed")
except NetmikoTimeoutException:
    print("SSH connection timed out")
except ReadTimeout:
    print("Command read timed out")
```

範例裡用文件保留範圍的 placeholder 位址。真正的
設備清單放在被忽略的本機檔案，或由機密管理的系統裡。

## Batch Collection

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

def collect_show(device: dict[str, Any], command: str) -> dict[str, Any]:
    host = device["host"]
    try:
        with ConnectHandler(**device) as conn:
            output = conn.send_command(command, read_timeout=45)
        return {"host": host, "ok": True, "output": output}
    except (NetmikoAuthenticationException, NetmikoTimeoutException, ReadTimeout) as exc:
        return {"host": host, "ok": False, "error": type(exc).__name__}

results = []
with ThreadPoolExecutor(max_workers=8) as pool:
    futures = [pool.submit(collect_show, device, "show version") for device in devices]
    for future in as_completed(futures):
        results.append(future.result())
```

除非確定設備群和 AAA 系統能承受更高的連線量，
否則 `max_workers` 要設低一點。

## Structured Parsing

Netmiko 可以請 TextFSM、TTP 或 Genie 解析支援的指令輸出。把
解析器的輸出當作最佳化，不要當成唯一的證據路徑。

```python
with ConnectHandler(**device) as conn:
    parsed = conn.send_command(
        "show ip interface brief",
        use_textfsm=True,
        raise_parsing_error=False,
        read_timeout=30,
    )

if isinstance(parsed, str):
    print("No parser template matched; store raw output for review")
else:
    for row in parsed:
        print(row)
```

如果解析結果會驅動會擋住流程的決策，要把原始的指令輸出
和解析結果一起留著，讓操作員可以檢查不一致的地方。

## Guarded Config Pattern

```python
import os

commands = [
    "interface GigabitEthernet0/1",
    "description CHANGE-1234 UPLINK-TO-CORE",
]

apply_changes = os.environ.get("APPLY_NETWORK_CHANGES") == "1"

if not apply_changes:
    print("Dry run only. Candidate commands:")
    print("\n".join(commands))
else:
    with ConnectHandler(**device) as conn:
        conn.enable()
        before = conn.send_command("show running-config interface GigabitEthernet0/1")
        output = conn.send_config_set(commands)
        after = conn.send_command("show running-config interface GigabitEthernet0/1")
        print(before)
        print(output)
        print(after)
        print("Verify behavior before saving startup config.")
```

儲存設定是另外一個核准步驟。在正式環境裡，要附上回滾
片段，並把變更前/後的證據記在變更紀錄裡。

## Review Checklist

- 腳本有沒有指明明確的設備清單來源？
- 憑證有沒有完全不出現在原始碼、紀錄和例外訊息裡？
- 有沒有設定 `conn_timeout`、`auth_timeout` 和指令的 `read_timeout`？
- 失敗是依設備分別回報，而不會讓整批停掉嗎？
- 腳本有沒有避免大範圍掃描和沒有上限的並行？
- 設定變更是不是放在 dry-run 或明確的操作員旗標後面？
- `save_config()` 有沒有和最初的推送分開，並且綁在驗證之後？

## Anti-Patterns

- 在原始碼裡寫死密碼、enable secret 或私鑰。
- 把送出設定指令當成預設的程式路徑。
- 對 CIDR 範圍跑自動化，而不是對審查過的設備清單跑。
- 沒有清理就把完整的 running config 記到共用系統。
- 把解析成功當成設備狀態正確的證明。

## See Also

- Skill: `cisco-ios-patterns`
- Skill: `network-config-validation`
- Skill: `network-interface-health`
