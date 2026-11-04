---
name: nemoclaw-setup
description: "在 Linux 上安裝並設定 NVIDIA NemoClaw（沙箱化的 OpenClaw agent 平台）。處理 cloudflared tunnel、Docker cgroup 修正、OpenShell、建立沙箱、透過 Cloudflare Tunnel 遠端存取，以及已知 bug 的暫時解法。只要使用者提到要安裝 NemoClaw、設定 OpenClaw、為沙箱化 agent 設定 NVIDIA Spark 或 DGX，或排查 NemoClaw 部署問題，就用這個 skill。"
compatibility: claude-code-only
---

# NemoClaw Setup

安裝 NVIDIA NemoClaw，一個建立在 OpenClaw 上的沙箱化 AI agent 平台，使用 Landlock + seccomp + network namespace 隔離。透過 k3s（OpenShell）在 Docker 裡執行。

## 你會得到什麼

- 沙箱化的 AI agent，有網頁 UI 和終端機 CLI
- 由 NVIDIA Nemotron 模型驅動（雲端或本機）
- 由 network policy 控管對外部服務的存取
- 可選用 Cloudflare Tunnel 做遠端存取

## 前置條件

| 需求 | 檢查 | 安裝 |
|-------------|-------|---------|
| Linux（Ubuntu 22.04+） | `uname -a` | — |
| Docker | `docker ps` | `sudo apt install docker.io` |
| Node.js 20+（建議 22） | `node --version` | `nvm install 22` |
| NVIDIA GPU（選用，但建議有） | `nvidia-smi` | — |
| NVIDIA API key | — | https://build.nvidia.com/settings/api-keys |

## 工作流程

### 步驟 1：事前檢查

```bash
# Check Docker
docker ps 2>/dev/null || echo "Docker not running or no access"

# Check Node.js
node --version

# Check if already installed
which nemoclaw && nemoclaw --version
which openshell && openshell --version
```

如果 `nemoclaw` 已經裝好了，跳到步驟 4。

### 步驟 2：安裝 NemoClaw

```bash
curl -fsSL https://nvidia.com/nemoclaw.sh | bash
```

這會用 npm 全域安裝 NemoClaw 和 OpenClaw（裝到 `~/.npm-global/bin/`）。

**如果安裝程式找不到 Node.js**，先裝它：
```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs
```

### 步驟 3：安裝 OpenShell

```bash
curl -LsSf https://raw.githubusercontent.com/NVIDIA/OpenShell/main/install.sh | sh
```

會裝到 `~/.local/bin/openshell`。

### 步驟 4：修正 Docker 權限和 cgroup

**Docker 群組**：使用者必須在 `docker` 群組裡：
```bash
sudo usermod -aG docker $USER
newgrp docker
# or log out and back in
```

**cgroup v2 修正**：Docker 裡跑 k3s 需要這個：
```bash
# Check if needed
grep cgroup2 /proc/filesystems && echo "cgroup v2 detected — fix needed"

# Apply fix (needs sudo)
sudo $HOME/.npm-global/bin/nemoclaw setup-spark
```

這會在 `/etc/docker/daemon.json` 加上 `"default-cgroupns-mode": "host"`，並重啟 Docker。

**重要**：`nemoclaw setup-spark` 指令也會要求 NVIDIA API key。先準備好（以 `nvapi-` 開頭）。到 https://build.nvidia.com/settings/api-keys 取得。

### 步驟 5：執行 Onboarding

```bash
PATH=$HOME/.npm-global/bin:$HOME/.local/bin:$PATH nemoclaw onboard
```

互動式精靈會：
1. 檢查 Docker 和 OpenShell
2. 啟動 OpenShell gateway（Docker 裡的 k3s）
3. 詢問沙箱名稱，用 `claw` 或任何名稱
4. 設定 NVIDIA API key
5. 設定推論（透過雲端 API 使用 Nemotron 3 Super 120B）
6. 在沙箱裡啟動 OpenClaw
7. 套用 network policy 預設，選你需要的

**常見的 port 衝突**：如果 8080 port 被占用，找出並結束那個 process：
```bash
fuser -k 8080/tcp
```

### 步驟 6：驗證

```bash
# Check sandbox is running
PATH=$HOME/.npm-global/bin:$HOME/.local/bin:$PATH nemoclaw claw status

# Connect via terminal
PATH=$HOME/.npm-global/bin:$HOME/.local/bin:$PATH nemoclaw claw connect
```

### 步驟 7：設定網頁 UI 存取

網頁 UI 跑在沙箱裡面，需要做 port forward：

```bash
PATH=$HOME/.npm-global/bin:$HOME/.local/bin:$PATH openshell forward start 18789 claw
```

然後打開：`http://127.0.0.1:18789/`

**已知 bug（OpenClaw ≤ v2026.3.11）**：出現「device identity required」錯誤。暫時解法是把 gateway token 附加到 URL 後面：

```bash
# Get the token
ssh -F /tmp/nemoclaw-ssh-config openshell-claw \
  "python3 -c \"import json; print(json.load(open('/sandbox/.openclaw/openclaw.json'))['gateway']['auth']['token'])\""
```

然後前往：`http://127.0.0.1:18789/#token=<gateway-token>`

**修法**：更新到 OpenClaw v2026.3.12 以上（見下方更新一節）。

### 步驟 8：讓 Port Forward 持續運作

建立一個有健康檢查的 keepalive script：

```bash
cat > ~/.local/bin/nemoclaw-keepalive.sh << 'KEEPALIVE'
#!/bin/bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"
cleanup() { kill %1 2>/dev/null; exit 0; }
trap cleanup SIGTERM SIGINT
while true; do
    fuser -k 18789/tcp 2>/dev/null; sleep 1
    openshell forward start 18789 claw &
    FORWARD_PID=$!; sleep 3
    while kill -0 $FORWARD_PID 2>/dev/null; do
        if ! curl -sf -o /dev/null --connect-timeout 3 http://127.0.0.1:18789/ 2>/dev/null; then
            echo "$(date): Health check failed, restarting..."
            kill $FORWARD_PID 2>/dev/null; wait $FORWARD_PID 2>/dev/null; break
        fi
        sleep 10
    done
    echo "$(date): Forward died, restarting in 3s..."; sleep 3
done
KEEPALIVE
chmod +x ~/.local/bin/nemoclaw-keepalive.sh
```

建立 systemd 服務：

```bash
sudo tee /etc/systemd/system/nemoclaw-forward.service << 'SERVICE'
[Unit]
Description=NemoClaw Port Forward with Health Check
After=docker.service
Requires=docker.service

[Service]
Type=simple
User=$USER
Group=docker
Environment=PATH=/home/$USER/.npm-global/bin:/home/$USER/.local/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/home/$USER/.local/bin/nemoclaw-keepalive.sh
Restart=always
RestartSec=5
KillMode=control-group

[Install]
WantedBy=multi-user.target
SERVICE

sudo systemctl daemon-reload
sudo systemctl enable nemoclaw-forward
sudo systemctl start nemoclaw-forward
```

### 步驟 9：透過 Cloudflare Tunnel 遠端存取（選用）

如果你已經有在跑的 Cloudflare Tunnel，把 NemoClaw 加進去。

**新增 DNS route：**
```bash
cloudflared tunnel route dns <tunnel-name> nemoclaw.<domain>
```

**更新 tunnel 設定**（`/etc/cloudflared/config.yml`）：
```yaml
  - hostname: nemoclaw.<domain>
    service: http://localhost:18789
    originRequest:
      httpHostHeader: "127.0.0.1:18789"
```

**重啟 tunnel：**
```bash
sudo systemctl restart cloudflared
```

**更新沙箱允許的 origin**：SSH 進沙箱，把你的網域加進去：

```bash
openshell sandbox ssh-config claw > /tmp/nemoclaw-ssh-config

ssh -F /tmp/nemoclaw-ssh-config openshell-claw 'python3 -c "
import json
with open(\"/sandbox/.openclaw/openclaw.json\") as f:
    config = json.load(f)
config[\"gateway\"][\"controlUi\"][\"allowedOrigins\"].append(\"https://nemoclaw.<domain>\")
config[\"gateway\"][\"trustedProxies\"] = [\"127.0.0.1\", \"::1\", \"172.0.0.0/8\", \"10.0.0.0/8\"]
config[\"gateway\"][\"allowRealIpFallback\"] = True
with open(\"/sandbox/.openclaw/openclaw.json\", \"w\") as f:
    json.dump(config, f, indent=2)
print(\"Done. Token:\", config[\"gateway\"][\"auth\"][\"token\"])
"'
```

**用 Cloudflare Access 保護**：到 Zero Trust dashboard，把這個 hostname 加進你的 Access application。

**存取網址**：`https://nemoclaw.<domain>/#token=<gateway-token>`

### 步驟 10：安裝自訂 Skill

Skill 是放在 `/sandbox/.openclaw/skills/<name>/SKILL.md` 的 markdown 檔。SSH 進沙箱來建立：

```bash
ssh -F /tmp/nemoclaw-ssh-config openshell-claw
mkdir -p /sandbox/.openclaw/skills/my-skill
cat > /sandbox/.openclaw/skills/my-skill/SKILL.md << 'EOF'
---
name: my-skill
description: What this skill does.
tools: [exec, read, write]
---
# My Skill
Instructions for the agent...
EOF
```

用這個驗證：`openclaw skills list`

### 步驟 11：設定 Workspace

更新 workspace 檔案，讓 agent 知道你是誰：

- `/sandbox/.openclaw/workspace/USER.md`：你的個人資料、偏好
- `/sandbox/.openclaw/workspace/TOOLS.md`：可用的工具與存取權限
- `/sandbox/.openclaw/workspace/SOUL.md`：agent 的個性與行為

## 更新 OpenClaw

沙箱在安裝時就綁定了 OpenClaw。要更新的話：

```bash
# 1. Update host-side packages
npm install -g openclaw@latest

# 2. Destroy and recreate sandbox
nemoclaw claw destroy
nemoclaw onboard

# 3. Reconfigure remote access (Step 9) and skills (Step 10)
```

**注意**：沙箱的 network policy 會擋掉沙箱裡的 npm/PyPI。更新只能靠重建。

## 疑難排解

| 問題 | 原因 | 修法 |
|-------|-------|-----|
| `Docker is not running` | Docker 服務停了，或使用者不在 docker 群組 | `sudo systemctl start docker` 然後 `newgrp docker` |
| `cgroup v2 detected` | Docker 沒設成 cgroupns=host | `sudo nemoclaw setup-spark` |
| Port 8080 被占用 | 別的服務在用那個 port | `fuser -k 8080/tcp` |
| `nemoclaw: command not found` | 不在 PATH 裡 | `PATH=$HOME/.npm-global/bin:$HOME/.local/bin:$PATH` |
| `device identity required` | OpenClaw ≤ v2026.3.11 的 bug | 在 URL 後面加 `#token=<gateway-token>`，或更新到 v2026.3.12+ |
| `gateway token mismatch` | 沙箱重建後 token 變了 | 從沙箱設定取得新的 token |
| `too many failed auth attempts` | 用舊 token 一直嘗試而被限流 | 重啟 gateway：`ssh -F /tmp/nemoclaw-ssh-config openshell-claw 'pkill -f "openclaw gateway"; sleep 2; openclaw gateway &'` |
| `origin not allowed` | 網域不在 allowedOrigins 裡 | 把它加進沙箱設定裡的 `gateway.controlUi.allowedOrigins` |
| Port 18789 沒回應 | SSH tunnel 斷了 | `sudo systemctl restart nemoclaw-forward`（13 秒內會自動恢復） |
| 沙箱裡 npm 403 Forbidden | Network policy 擋了 TLS | 沙箱裡不能安裝套件，改用重建 |
| DNS route 出現 `Tunnel not found` | Cloudflare 帳號/憑證不對 | 檢查 `cloudflared tunnel list` 是否和你的憑證相符 |
| Cloudflare 上出現 502 | Tunnel 連線斷了 | `sudo systemctl restart cloudflared` |
| 透過 Cloudflare 時資源 404 | 瀏覽器對子請求還沒通過認證 | Cloudflare Access 登入後強制重新整理（Ctrl+Shift+R） |

## 架構

```
Docker (openshell-cluster-<name>)
  └─ k3s cluster
      ├─ NVIDIA device plugin
      └─ OpenShell sandbox
          ├─ OpenClaw agent
          ├─ NemoClaw plugin
          ├─ Gateway (WebSocket + REST)
          └─ Workspace (SOUL.md, USER.md, TOOLS.md, skills/)

Port forward (systemd): localhost:18789 ←SSH tunnel→ sandbox:18789
Cloudflare Tunnel (optional): nemoclaw.domain → localhost:18789
```

## 參考資料

- [NemoClaw GitHub](https://github.com/NVIDIA/NemoClaw)
- [OpenShell GitHub](https://github.com/NVIDIA/OpenShell)
- [OpenClaw docs](https://docs.openclaw.ai)
- [NemoClaw quickstart](https://docs.nvidia.com/nemoclaw/latest/get-started/quickstart.html)
- [awesome-nemoclaw presets](https://github.com/VoltAgent/awesome-nemoclaw)
- [awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills)
- [device auth bug fix](https://github.com/openclaw/openclaw/issues/43909)
