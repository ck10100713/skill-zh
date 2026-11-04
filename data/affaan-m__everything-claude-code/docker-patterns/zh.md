---
name: docker-patterns
description: 用於本機開發、強化過的 CLI installer harness、container 安全、網路、volume 與多服務編排的 Docker 與 Docker Compose 模式。在建立或審查 Dockerfile 與 Compose 服務、跨 Linux 發行版測試 installer，或規劃準確的原生 macOS 與 Windows 驗證時使用。
---

# Docker 模式

給 container 化開發用的 Docker 與 Docker Compose 最佳實務。

## 本機開發用的 Docker Compose

### 標準 Web App Stack

```yaml
# docker-compose.yml
services:
  app:
    build:
      context: .
      target: dev                     # Use dev stage of multi-stage Dockerfile
    ports:
      - "3000:3000"
    volumes:
      - .:/app                        # Bind mount for hot reload
      - /app/node_modules             # Anonymous volume -- preserves container deps
    environment:
      - DATABASE_URL=postgres://postgres:postgres@db:5432/app_dev
      - REDIS_URL=redis://redis:6379/0
      - NODE_ENV=development
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    command: npm run dev

  db:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: app_dev
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redisdata:/data

  mailpit:                            # Local email testing
    image: axllent/mailpit
    ports:
      - "8025:8025"                   # Web UI
      - "1025:1025"                   # SMTP

volumes:
  pgdata:
  redisdata:
```

### 開發 vs Production 的 Dockerfile

```dockerfile
# Stage: dependencies
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# Stage: dev (hot reload, debug tools)
FROM node:22-alpine AS dev
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]

# Stage: build
FROM node:22-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build && npm prune --production

# Stage: production (minimal image)
FROM node:22-alpine AS production
WORKDIR /app
RUN addgroup -g 1001 -S appgroup && adduser -S appuser -u 1001
USER appuser
COPY --from=build --chown=appuser:appgroup /app/dist ./dist
COPY --from=build --chown=appuser:appgroup /app/node_modules ./node_modules
COPY --from=build --chown=appuser:appgroup /app/package.json ./
ENV NODE_ENV=production
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://localhost:3000/health || exit 1
CMD ["node", "dist/server.js"]
```

### Override 檔

```yaml
# docker-compose.override.yml (auto-loaded, dev-only settings)
services:
  app:
    environment:
      - DEBUG=app:*
      - LOG_LEVEL=debug
    ports:
      - "9229:9229"                   # Node.js debugger

# docker-compose.prod.yml (explicit for production)
services:
  app:
    build:
      target: production
    restart: always
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 512M
```

```bash
# Development (auto-loads override)
docker compose up

# Production
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 網路

### 服務探索

同一個 Compose 網路裡的服務可以用服務名稱互相解析：
```
# From "app" container:
postgres://postgres:postgres@db:5432/app_dev    # "db" resolves to the db container
redis://redis:6379/0                             # "redis" resolves to the redis container
```

### 自訂網路

```yaml
services:
  frontend:
    networks:
      - frontend-net

  api:
    networks:
      - frontend-net
      - backend-net

  db:
    networks:
      - backend-net              # Only reachable from api, not frontend

networks:
  frontend-net:
  backend-net:
```

### 只暴露需要的

```yaml
services:
  db:
    ports:
      - "127.0.0.1:5432:5432"   # Only accessible from host, not network
    # Omit ports entirely in production -- accessible only within Docker network
```

## Volume 策略

```yaml
volumes:
  # Named volume: persists across container restarts, managed by Docker
  pgdata:

  # Bind mount: maps host directory into container (for development)
  # - ./src:/app/src

  # Anonymous volume: preserves container-generated content from bind mount override
  # - /app/node_modules
```

### 常見模式

```yaml
services:
  app:
    volumes:
      - .:/app                   # Source code (bind mount for hot reload)
      - /app/node_modules        # Protect container's node_modules from host
      - /app/.next               # Protect build cache

  db:
    volumes:
      - pgdata:/var/lib/postgresql/data          # Persistent data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql  # Init scripts
```

## Container 安全

### Dockerfile 強化

```dockerfile
# 1. Use specific tags (never :latest)
FROM node:22.12-alpine3.20

# 2. Run as non-root
RUN addgroup -g 1001 -S app && adduser -S app -u 1001
USER app

# 3. Drop capabilities (in compose)
# 4. Read-only root filesystem where possible
# 5. No secrets in image layers
```

### Compose 安全

```yaml
services:
  app:
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
      - /app/.cache
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE          # Only if binding to ports < 1024
```

### Secret 管理

```yaml
# GOOD: Use environment variables (injected at runtime)
services:
  app:
    env_file:
      - .env                     # Never commit .env to git
    environment:
      - API_KEY                  # Inherits from host environment

# GOOD: Docker secrets (Swarm mode)
secrets:
  db_password:
    file: ./secrets/db_password.txt

services:
  db:
    secrets:
      - db_password

# BAD: Hardcoded in image
# ENV API_KEY=sk-proj-xxxxx      # NEVER DO THIS
```

## 強化過的 CLI Installer Harness

用 container 對可丟棄的專案副本測試 installer 行為，同時不讓測試動到原始 checkout。

### 尊重平台邊界

- Debian、Ubuntu 這類 Linux 發行版，跑真的 container。
- macOS 不能當 Docker container 跑，因為 Docker 共用的是 Linux kernel。要在 macOS 上原生執行同一個不靠 shell 的測試入口。
- Windows container 需要 Windows 的 Docker engine。平台無關的邏輯在原生 Windows CI runner 上跑，Windows container 只留給 Windows 主機。
- 針對主機特有的路徑、指令 shim、引號處理與檔案系統行為，保留原生 Ubuntu/macOS/Windows 的 CI matrix。

不要宣稱 Linux container 驗證過 macOS 或 Windows 的行為。

### 落實隔離契約

- 用不可變的 digest 固定 base image，並固定安裝的 CLI 版本。
- 發行版帳號名稱不同時，用非 root 的數字 UID/GID 執行。
- 把 repo 和來源專案以唯讀方式掛載。
- 動手改之前，先把來源專案複製到可寫入的 `tmpfs` workspace。
- 用 `noexec`、UID/GID 1000 和 `mode=0700` 掛載 `/workspace`，讓只有
  container 使用者能看到專案資料。
- 把 npm 與 npx 的可執行 cache 放在 `NPM_CONFIG_CACHE=/tmp/npm-cache`，
  位於可執行的 `/tmp` 掛載上。預設大小是 2 GiB，可用
  `ECC_TMPFS_SIZE` 調整；`ECC_WORKSPACE_SIZE` 另外控制私有
  workspace 掛載的大小。
- 設定 `read_only: true`、`no-new-privileges:true`、`cap_drop: [ALL]`，以及有限的 `pids_limit`。
- 預設的真 CLI 服務一律用 `network_mode: none`。要開網路，
  只能透過一個名稱明顯的 opt-in 服務，給需要認證的 provider
  session 用；絕對不要讓它變成環境變數意外帶出來的預設值。
- 只建立工具需要的可寫入暫存路徑。
- 預設不要把主機的憑證傳進 container。
- 預設是 dry run，只對明確的 `dry-run`、`install`、
  `plugin` 和 `shell` 模式放行。
- 跨平台 runner 用參數陣列或 `spawnSync(..., { shell: false })`。專案路徑絕對不要拼進 shell 指令。

### 實際操作 ECC Plugin Setup Harness

以 `docker/plugin-setup/compose.yaml` 作為參考實作。它提供：

- `fixture-tests`：針對 install manifest、target 和 executor 的聚焦測試套件。
- `real-cli`：固定版本、以 Debian 為基礎的通用 Linux image。
- `real-cli-ubuntu`：固定版本的 Ubuntu image。

建置前先驗證 Compose model：

```bash
docker compose -f docker/plugin-setup/compose.yaml config --quiet
```

建置兩個真正的 Linux image：

```bash
docker compose -f docker/plugin-setup/compose.yaml \
  build real-cli real-cli-ubuntu
```

在每個 image 裡跑安全的預設流程：

```bash
docker compose -p ecc-plugin-debian-test \
  -f docker/plugin-setup/compose.yaml \
  run --rm -T real-cli dry-run

docker compose -p ecc-plugin-ubuntu-test \
  -f docker/plugin-setup/compose.yaml \
  run --rm -T real-cli-ubuntu dry-run
```

dry run 執行的是目前公開的指令契約：

```bash
ecc install --profile core --target claude-project --dry-run --json
```

那個指令執行前，container 會先用 `npm pack --ignore-scripts`
從唯讀 checkout 打出一個本地 npm 產物。它把自己產生的
tarball 解壓到 `/tmp` 底下，驗證 `ecc-universal` 套件名稱、
必要的 install manifest，以及受限的 `package.json` `bin.ecc` 對應，
然後執行解壓出來的 `ecc` 可執行檔。runtime 維持在
`network_mode: none`，不執行套件的 lifecycle script，
也不依賴主機的 `node_modules`；它確切固定版本的 production 相依套件
早就在 image 裡了。

這個 harness 會拒絕空的 plan、非 `claude-project` 的 target、
任何超出 `/workspace/project/.claude` 的操作，以及任何會建立 target
目錄的 dry run。`install` 會在隔離環境中套用兩次，檢查它管理的
install 狀態，列出已安裝的 target，並執行 `doctor`。

### 啟動、開啟、重新連線與清理具名 Session

啟動 detached container 時不要加 `--rm`，這樣關掉終端機
不會把 session 一起移除：

```bash
docker compose -p ecc-plugin-session \
  -f docker/plugin-setup/compose.yaml \
  run --detach --name ecc-plugin-shell real-cli shell
```

container 會把唯讀的 fixture 複製到固定的私有目錄
`/workspace/project`。確認它在跑之後，輸出 terminal-opener v1
資料契約中屬於 Docker 的那一側：

```bash
docker inspect --format '{{.State.Running}}' ecc-plugin-shell
node docker/plugin-setup/interactive-plan.js \
  --container ecc-plugin-shell \
  --workdir /workspace/project \
  --json \
  -- bash
```

JSON 結果只有 `executable` 和 `argv` 兩個邊界（外加
`contractVersion: 1`）：executable 是 `docker`，argv 以
`exec`、`-it` 和 `-w` 開頭。把這份資料交給另外安裝的
terminal-opener skill。這個 Docker harness 刻意不引入
終端機 adapter、不拼接 shell 指令，也不管理主機的 GUI process。
在那之前，直接在目前主機的終端機裡開同一個 PTY：

```bash
docker exec -it -w /workspace/project ecc-plugin-shell bash
```

退出 shell 時不要停掉 detached container。用同一個
`docker exec -it` 指令重新連線。用完之後，移除這個確切具名的 container
和它的 Compose 專案資源：

```bash
docker rm --force ecc-plugin-shell
docker compose -p ecc-plugin-session \
  -f docker/plugin-setup/compose.yaml \
  down --remove-orphans
```

主機憑證預設不存在，憑證目錄也絕對不會被
掛載。預設服務也沒有網路存取。當需要認證的
provider session 真的需要網路時，先建置 `real-cli`，再用
`docker compose -f docker/plugin-setup/compose.yaml
--profile networked run --service-ports real-cli-networked shell` 明確 opt-in。
`--service-ports` 旗標會發布該服務的 loopback callback 對應。
建議在那個用完即丟的 session 裡面做認證。如果 CI 一定要
繼承主機環境的憑證，就在執行時用明確的 Compose `--env NAME` 旗標 opt-in，
要清楚那個值在 container 存活期間可以被檢視，
也可能被外洩，用完立刻移除那個確切具名的
container。

### 在有網路的 Session 裡認證 Codex

`codex login` 會把它的 OAuth callback server 綁在 container 內的
`127.0.0.1:1455`。Docker 的 port 發布是轉到 container 的網路介面，不是
loopback，所以主機瀏覽器 redirect 到 `http://localhost:1455` 時，
沒有橋接就會被拒絕。`real-cli-networked` 服務把主機的
`127.0.0.1:1455` 發布到 container 的 `1456` port；登入前先把那個 port
橋接到 loopback：

```bash
(
  set -e
  npm install --global @openai/codex@0.162.0   # the harness image does not ship codex
  node /ecc/docker/plugin-setup/codex-auth-relay.js &
  relay_pid=$!
  trap 'kill "$relay_pid" 2>/dev/null || true; wait "$relay_pid" 2>/dev/null || true' EXIT
  codex login
)
```

有網路的服務會設定 `NPM_CONFIG_PREFIX=/tmp/ecc-npm`，並把它的 `bin`
目錄加進 `PATH`。這樣固定版本的安裝在可執行的 `/tmp` 掛載上對 UID 1000
是可寫的，而 root 檔案系統仍然維持唯讀。

在主機瀏覽器完成登入。每次嘗試都會產生新的
`state`/`code`，所以一律點最新印出的連結。token 留在
用完即丟的 container 的 `~/.codex/auth.json`；移除該具名 container
就會刪掉那份憑證副本。登入區塊不論成功或失敗都會停掉 relay。
同一時間只有一個 container 能佔用主機的 1455 port，
因為 OAuth redirect 指向固定的 port。

主機的 port 發布只限 loopback。在 container 內，relay
監聽所有介面，好讓 Docker 能轉送給它；同一個 bridge 網路上的
其他 container 在它執行期間可以連到它。這次登入請用沒有
不可信對象的專用網路，用完移除那個確切具名的 container。
閒置的 callback 連線 30 秒後會關閉。

在主機上原生執行同一個聚焦測試套件：

```bash
npm run test:plugin-setup-platform
```

在信任 image 之前，先檢查它產出的身分與環境：

```bash
docker image inspect ecc-plugin-setup:debian ecc-plugin-setup:ubuntu
```

清理每個具名的測試專案，同時不刪除不相關的 volume 或 image：

```bash
docker compose -p ecc-plugin-debian-test \
  -f docker/plugin-setup/compose.yaml down --remove-orphans
docker compose -p ecc-plugin-ubuntu-test \
  -f docker/plugin-setup/compose.yaml down --remove-orphans
```

## .dockerignore

```
node_modules
.git
.env
.env.*
dist
coverage
*.log
.next
.cache
docker-compose*.yml
Dockerfile*
README.md
tests/
```

## 除錯

### 常用指令

```bash
# View logs
docker compose logs -f app           # Follow app logs
docker compose logs --tail=50 db     # Last 50 lines from db

# Execute commands in running container
docker compose exec app sh           # Shell into app
docker compose exec db psql -U postgres  # Connect to postgres

# Inspect
docker compose ps                     # Running services
docker compose top                    # Processes in each container
docker stats                          # Resource usage

# Rebuild
docker compose up --build             # Rebuild images
docker compose build --no-cache app   # Force full rebuild

# Clean up
docker compose down                   # Stop and remove containers
docker compose down -v                # Also remove volumes (DESTRUCTIVE)
docker system prune                   # Remove unused images/containers
```

### 除錯網路問題

```bash
# Check DNS resolution inside container
docker compose exec app nslookup db

# Check connectivity
docker compose exec app wget -qO- http://api:3000/health

# Inspect network
docker network ls
docker network inspect <project>_default
```

## 反模式

```
# BAD: Using docker compose in production without orchestration
# Use Kubernetes, ECS, or Docker Swarm for production multi-container workloads

# BAD: Storing data in containers without volumes
# Containers are ephemeral -- all data lost on restart without volumes

# BAD: Running as root
# Always create and use a non-root user

# BAD: Using :latest tag
# Pin to specific versions for reproducible builds

# BAD: One giant container with all services
# Separate concerns: one process per container

# BAD: Putting secrets in docker-compose.yml
# Use .env files (gitignored) or Docker secrets
```
