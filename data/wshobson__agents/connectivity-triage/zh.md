---
name: connectivity-triage
description: 除錯目前正在發生的 macOS 連線故障、API 或 MCP 服務逾時或斷線、DNS 解析失敗或不一致，或視訊通話等即時流量出現封包遺失或延遲時，使用這個 skill。用內建、不具破壞性的工具，隔離出本地 LAN、DNS、上游路徑，以及遠端服務/應用程式這幾個故障域。
---

# 連線分流診斷

在不更動網路設定的前提下，把正在發生的連線故障定位出來。只蒐集最小而有用的證據組合，區分觀察和推論，等故障域清楚到足以決定下一個安全的動作就停下來。

## 何時使用這個 Skill

當 macOS 端點出現下列正在發生的症狀時，使用這個工作流程：

- API、網站或 MCP 服務逾時或斷線；
- DNS 查詢失敗或名稱解析不一致；
- 封包遺失、延遲或即時流量不穩定；
- 應用程式看起來離線，其他流量卻正常；
- 不確定問題出在本地、上游，還是服務端。

這是診斷的工作流程，不是補救的工作流程。在確立故障域的過程中，不要更動介面狀態、DNS 設定、VPN/防火牆設定，或遠端服務的狀態。

## 快速決策流程

從症狀出發，往最能區分問題的檢查前進：

```text
symptom
  -> local link / LAN evidence
  -> DNS configuration and resolution
  -> destination reachability
  -> path quality
  -> application / service timing
  -> fault-domain assessment
```

證據已經夠用時就提早停下。不要機械式地把每個探測都跑一遍。

### 1. 定義症狀

記錄受影響的應用程式或 process、目標主機名稱或 URL、失敗從什麼時候開始、是持續還是間歇性的，以及不相關的目的地是否還能用。

如果症狀是特定應用程式才有的，要保留應用程式實際使用的確切主機名稱或 URL。測試無關的公開網站，可以確認一般連線沒問題，卻無法證明受影響的服務是健康的。

### 2. 檢查本地連結 / LAN 的證據

可以的話，執行一次有時間限制的 `networkQuality` 取樣，取得整體回應性和吞吐量的訊號。如果沒有 `networkQuality`，就繼續往下，它是選用的。

如果有已知的本地 gateway 或同一個 LAN 內的目標，把對那個本地目標的短時間 `ping` 取樣，跟對遠端目的地的短時間取樣做比較。不要自己編一個 gateway 位址。如果不知道任何本地目標，就把 LAN 這一段保持「未證實」並繼續。

有用的做法：

```bash
ping -c 5 <known-local-target>
ping -c 5 <destination>
```

### 3. 把 DNS 的設定和 DNS 的行為分開

檢查系統的 resolver 狀態，特別是可能牽涉到 VPN、split DNS 或有範圍的 resolver 時：

```bash
scutil --dns
```

然後用有時間限制的 DNS 查詢，直接測試目的地名稱：

```bash
dig +time=2 +tries=1 <hostname>
```

把這兩者當成不同的證據。`scutil --dns` 顯示的是 resolver 的設定；`dig` 顯示的是查詢的行為。查詢成功，並不能證明回傳的端點連得到。

### 4. 測試可達性和路徑品質

當 ICMP 是有用的訊號時，用短時間的 `ping` 取樣：

```bash
ping -c 5 <destination>
```

如果主機名稱能解析，只有在有助於區分 DNS 行為和路徑故障時，才另外測試回傳的位址。如果目前解析失敗，只有在這個位址先前是從可信的事故證據中觀察到的，才使用位址；否則就把位址層級的可達性保持「未知」。

當路徑可見性能降低不確定性時，用有限制的數字型 traceroute：

```bash
traceroute -n -q 1 -m 20 <destination>
```

沒有回應或會變動的 hop，是一個觀察，不能證明那個 hop 壞了。路由器可能會過濾或限制 traceroute 流量的速率，卻照常轉送應用程式的流量。

### 5. 檢查受影響應用程式即時的網路活動

當問題只跟特定 process 有關時，用有限制的 `nettop` 擷取，不要無限期地盯著看：

```bash
nettop -n -L 3 -p <process-name-or-pid>
```

用它確認 process 有沒有在開連線、用的是哪些端點，以及流量有沒有在流動。看不到任何活動，可能代表應用程式根本沒嘗試連線，但這本身並不能說明原因。

### 6. 對應用程式路徑計時

對 HTTP(S)，如果有安全的唯讀請求可用，就針對實際受影響的端點，用 curl 的分階段計時。要確認事故提供的端點是完整的 `http://` 或 `https://` URL，保留它原本的 scheme，並把 URL 當成一個加引號的參數傳入，不要把任意的事故文字內插進 shell 指令：

```bash
curl -sS -o /dev/null \
  -w 'dns=%{time_namelookup} connect=%{time_connect} tls=%{time_appconnect} ttfb=%{time_starttransfer} total=%{time_total}\n' \
  --connect-timeout 5 --max-time 15 '<affected-http-or-https-url>'
```

要用比較的方式解讀各個階段。較高的 time-to-first-byte 可能包含伺服器處理的時間，所以不能證明是網路延遲。

## 證據規則

把結論標成下列其中一種：

- **Observed（觀察到的）**：直接由指令輸出或使用者提供的證據所支持。
- **Inferred（推論的）**：把觀察結果對照關聯之後，最有可能的解釋。
- **Unknown（未知的）**：目前的證據無法確立。

絕對不要把單一的探測當成根本原因的證明。特別是：

- `ping` 失敗，可能只是 ICMP 被過濾，不是斷線；
- `ping` 成功，並不能證明應用程式是健康的；
- traceroute 沒回應的 hop，並不能證明那些路由器有封包遺失；
- DNS 解析成功，並不能證明連得到；
- HTTP first-byte 時間很高，可能主要是遠端應用程式處理造成的。

當觀察結果互相矛盾時，寧可選 `inconclusive`，也不要自信地亂猜。

## 故障域評估

只回傳一個主要類別：

- `local-link/LAN`：證據在本地網路邊界之前或在邊界上就開始惡化；
- `DNS`：resolver 的設定或查詢行為，比路徑證據更能解釋這個故障；
- `upstream-path`：本地證據正常，而且相互對應的路徑證據在 LAN 之外惡化；
- `remote-service/application`：傳輸/路徑證據夠健康，但受影響的服務或 process 的行為仍然異常；
- `inconclusive`：目前的證據無法區分剩下的故障域。

用定性的信心程度：`low`、`medium` 或 `high`。信心反映的是證據的品質和關聯性，不是嚴重程度。

## 事故結果格式

### Symptom
重述目前的故障，以及受影響的目的地/應用程式。

### Observations
只列出相關的量測，包括重要的、無法取得或被擋下的證據。要清楚標示哪些是觀察、推論和未知。

### Fault-domain assessment
回報類別、信心程度，以及一段簡短、連結到證據的解釋。

### Next safest check
給出一個最能降低不確定性的診斷動作。除非使用者另外要求補救，否則不要直接跳到更動設定。

## 安全與界線

診斷期間，不要：

- 更動介面狀態或重啟網路服務；
- 編輯 resolver 設定或清除 DNS 快取；
- 修改防火牆或 VPN 設定；
- 安裝套件或要求使用 Homebrew；
- 對遠端服務送出會改變狀態的請求；
- 當有限制的取樣就能回答問題時，還去執行無限期或大流量的探測。

不完整的探測、被擋下的 ICMP、VPN、captive portal、有範圍的 DNS、proxy、端點控管和暫時性的故障，都是證據的限制，不是診斷結果。

## 詳細解讀

要看逐個指令的解讀、模糊情況的處理、間歇性故障的指引和實作範例，請讀 `references/details.md`。

## 相關 Skill

- `incident-runbook-templates`：把反覆發生的連線事故，變成可重複的回應程序
- `on-call-handoff-patterns`：在處理人員交接時，保存正在進行的連線證據
- `postmortem-writing`：事故之後，記錄確認的原因和矯正措施
