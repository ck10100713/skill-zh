---
name: uncloud
description: 管理 Uncloud 叢集時使用：部署服務、設定 Caddy ingress、為非叢集裝置新增靜態 proxy 路由、發布 port、擴縮容、查看 log，或用 `uc` CLI 管理機器和 volume。
metadata:
  origin: ECC
---

# Uncloud 叢集管理

`uc` CLI 的參考資料。它是一個去中心化的自架平台，使用 Docker 容器、WireGuard mesh 網路和 Caddy 反向代理。

## 何時啟用

在操作 Uncloud 叢集時使用這個 skill，特別是在這些情況：
- 用 `uc machine` 初始化或加入機器
- 用 `uc deploy` 從 Compose 檔部署服務
- 透過 Uncloud 發布 HTTP、HTTPS、TCP 或 UDP port
- 用 `x-caddy`、`x-ports` 或 `--caddyfile` 設定 Caddy ingress
- 把外部區域網路的裝置路由到叢集的 proxy
- 查看 log、服務狀態、volume、DNS 或機器配置

## 運作方式

Uncloud 在由 WireGuard mesh 連起來的對等機器上跑 Docker 服務。每台機器都是對等的叢集成員；服務在 overlay 網路上互相通訊，Caddy 以 global 方式執行，負責終結對外的 HTTP/HTTPS 流量。Compose 檔可以使用 Uncloud 的擴充功能來做 ingress、配置和產生 Caddy 設定，而 `uc` CLI 負責映像檔分發、排程、擴縮容、log 和叢集狀態。

## 範例

```bash
uc machine init user@host --name machine-1
uc service run --name web -p app.example.com:8080/https nginx:latest
uc deploy
```

## 核心概念

- **沒有中央控制平面**：所有機器都是由 WireGuard 連接的對等節點
- **Caddy** 以 global 服務的形式跑在每台機器上；自動從 Let's Encrypt 取得 TLS
- **Overlay 網路**：服務預設透過 `10.210.0.0/16` 通訊；mesh 內部有提供 DNS
- **Caddyfile 是自動產生的**：絕對不要直接編輯它；改用 `x-caddy` / `--caddyfile`

---

## CLI 速查

### Machines

| 指令 | 用途 |
|---------|---------|
| `uc machine init user@host` | 初始化第一台機器 / 新叢集 |
| `uc machine add user@host` | 把機器加入現有叢集 |
| `uc machine ls` | 列出機器 |
| `uc machine update NAME --public-ip IP` | 更新給 ingress 用的公開 IP |
| `uc machine rm NAME` | 移除機器 |

`init` 的主要 flag：`--name`、`--network 10.210.0.0/16`、`--no-caddy`、`--no-dns`、`--public-ip auto\|IP\|none`

### Services

| 指令 | 用途 |
|---------|---------|
| `uc service ls` / `uc ls` | 列出服務 |
| `uc service run IMAGE` | 執行單一容器服務 |
| `uc deploy` | 從 `compose.yaml` 部署 |
| `uc deploy --no-build` | 部署已經 push 的映像檔，不重新 build |
| `uc deploy --recreate` | 強制重新建立服務 |
| `uc scale SERVICE N` | 設定 replica 數量 |
| `uc service logs SERVICE` | 查看 log |
| `uc service exec SERVICE` | 進入容器的 shell |
| `uc service inspect SERVICE` | 詳細資訊 |
| `uc service rm SERVICE` | 移除服務（保留具名 volume） |
| `uc ps` | 叢集內所有容器 |

### Images

```bash
uc image push myapp:latest                    # Push local image to all machines
uc image push myapp:latest -m machine1,machine2  # Push to specific machines
uc images                                     # List images in cluster
```

### Volumes

```bash
uc volume ls                  # All volumes
uc volume ls -m machine1      # On specific machine
uc volume create NAME -m MACHINE
uc volume rm NAME
```

### Caddy

```bash
uc caddy config    # Show current generated Caddyfile (read-only)
uc caddy deploy    # Deploy/upgrade Caddy across cluster
```

### DNS 與 Context

```bash
uc dns show        # Show reserved *.uncld.dev domain
uc dns reserve     # Reserve a new domain
uc ctx ls          # List cluster contexts
uc ctx use prod    # Switch context
```

---

## Port 發布

### HTTP/HTTPS（透過 Caddy 反向代理）

```
-p [hostname:]container_port[/protocol]
```

| 範例 | 意義 |
|---------|---------|
| `-p 8080/https` | HTTPS，自動使用 `service-name.cluster-domain` 當 hostname |
| `-p app.example.com:8080/https` | HTTPS，使用自訂 hostname |
| `-p 8080/http` | 只有 HTTP，沒有 TLS |

### TCP/UDP（綁定在主機上，繞過 Caddy）

```
-p [host_ip:]host_port:container_port[/protocol]@host
```

| 範例 | 意義 |
|---------|---------|
| `-p 5432:5432@host` | 所有介面上的 TCP 5432 |
| `-p 127.0.0.1:5432:5432@host` | TCP 5432，只限 loopback |
| `-p 53:5353/udp@host` | UDP |

---

## Compose 檔擴充

Uncloud 在 Docker Compose 之上加了這些擴充：

### `x-ports`：用網域發布 port

```yaml
services:
  app:
    image: app:latest
    x-ports:
      - example.com:8000/https
      - www.example.com:8000/https
      - api.example.com:9000/https
```

### `x-caddy`：服務專屬的自訂 Caddy 設定

```yaml
services:
  app:
    image: app:latest
    x-caddy: |
      example.com {
        redir https://www.example.com{uri} permanent
      }
      www.example.com {
        reverse_proxy {{upstreams 8000}} {
          import common_proxy
        }
        basic_auth /admin/* {
          admin $2a$14$...
        }
      }
```

`x-caddy` 裡可以用的範本函式：
- `{{upstreams [service] [port]}}`：健康的容器 IP
- `{{.Name}}`：服務名稱
- `{{.Upstreams}}`：所有服務 → IP 的對照表

### `x-machines`：配置限制

```yaml
services:
  db:
    image: postgres:18
    x-machines: db-machine          # Single machine name
  app:
    image: app:latest
    x-machines:
      - machine-1
      - machine-2
```

### 完整的多服務範例

```yaml
services:
  api:
    build: ./api
    x-ports:
      - api.example.com:3000/https
    environment:
      DATABASE_URL: postgres://db:5432/mydb

  web:
    build: ./web
    x-ports:
      - example.com:8000/https
      - www.example.com:8000/https
    environment:
      API_URL: http://api:3000

  db:
    image: postgres:18
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - db-data:/var/lib/postgresql/data
    x-machines: db-machine

volumes:
  db-data:
```

---

## 路由到外部（非叢集）裝置

要透過 Caddy 對外開放一個外部裝置（例如 BMC、NAS、路由器的管理介面），又不想跑真正的容器：

**1. 建立 Caddyfile 片段**（例如 `~/device.caddyfile`）：

```caddyfile
https://device.example.com {
    reverse_proxy https://192.168.1.x {
        transport http {
            tls_insecure_skip_verify   # needed for self-signed BMC certs
        }
    }
    log
}
```

如果上游是明文：`reverse_proxy http://192.168.1.x:port`

**2. 用一個什麼都不做的容器，註冊成具名服務：**

```bash
uc service run \
  --name device-bmc \
  --caddyfile ~/device.caddyfile \
  registry.k8s.io/pause:3.9
```

`pause` 是最精簡的 no-op 容器：它什麼都不做，但讓 Uncloud 有一個服務項目可以掛上 Caddyfile。

**3. 驗證：**

```bash
uc caddy config   # device.example.com block should appear
```

> `--caddyfile` 不能跟非 `@host` 的已發布 port 一起使用。

**DNS 小技巧：** 設一筆萬用字元記錄（`*.yourdomain.com → cluster-public-ip`），任何新的子網域都能立刻生效，每個服務都不用再改 DNS。

---

## 服務 DNS（內部）

叢集內的服務可以用名稱互相解析：

| DNS 名稱 | 解析到 |
|----------|------------|
| `service-name` | 任何健康的容器 |
| `service-name.internal` | 同上 |
| `rr.service-name.internal` | Round-robin |
| `nearest.service-name.internal` | 優先同一台機器上的 |

---

## 擴縮容與 Global 服務

```bash
uc scale web 5    # 5 replicas (spread across machines)
uc scale web 1    # Scale down
```

```yaml
services:
  caddy:
    deploy:
      mode: global   # One container on every machine
```

---

## 映像檔 Tag 範本（在 compose.yaml 裡）

```yaml
image: myapp:{{gitdate "20060102"}}.{{gitsha 7}}
image: myapp:{{gitsha 7}}.${GITHUB_RUN_ID:-local}
```

| 函式 | 輸出 |
|----------|--------|
| `{{gitsha N}}` | commit SHA 的前 N 個字元 |
| `{{gitdate "format"}}` | 用 Go 格式表示的 git commit 日期 |
| `{{date "format"}}` | 目前日期 |

---

## 常見工作流

**從原始碼部署：**
```bash
uc deploy                          # Build + push + deploy
uc build --push && uc deploy --no-build   # Separate steps
```

**檢查服務：**
```bash
uc inspect web
uc logs -f web
uc logs --since 1h web
uc exec web                        # Opens shell
uc exec web /bin/sh -c "env"       # Run specific command
```

**零停機部署**會自動發生；Uncloud 會等健康檢查通過之後，才終止舊的容器。

**強制重新建立：**
```bash
uc deploy --recreate
```

---

## 常見錯誤

| 錯誤 | 修正 |
|---------|-----|
| 直接編輯 Caddyfile | 在 compose 裡用 `x-caddy`，或在 `uc service run` 上用 `--caddyfile` |
| 代理使用自簽憑證的 HTTPS 上游 | 加上 `transport http { tls_insecure_skip_verify }` |
| `uc caddy config` 沒有顯示使用者定義的區塊 | 連不到 Caddy 的 admin socket：檢查 `uc inspect caddy` 和 `uc logs caddy` |
| 服務從容器裡連不到外部區域網路 IP | 確認 Caddy 容器所在的主機能路由到目標網路 |
| `uc service rm` 之後 volume 不見了 | 具名 volume 會保留；只有匿名 volume 會被自動移除 |
