---
name: homelab-pihole-dns
description: 在家用網路上安裝 Pi-hole、管理封鎖清單、設定 DNS-over-HTTPS、整合 DHCP、建立本地 DNS 記錄，以及排查壞掉的 DNS 解析。任務明確牽涉 Pi-hole 時使用，例如安裝、管理封鎖清單、設定 DoH 或 DHCP、新增本地 DNS 記錄，或診斷 Pi-hole 在路徑上的 DNS 解析問題。
metadata:
  origin: community
---

# Homelab Pi-hole DNS

Pi-hole 是整個網路層級的 DNS 廣告封鎖器，可以跑在 Raspberry Pi 或任何 Linux 主機上。
網路上的每個裝置都會自動套用廣告和惡意網域封鎖，不用裝瀏覽器
擴充功能。

## When to Use

- 在 Raspberry Pi 或 Linux 主機上安裝 Pi-hole
- 把 Pi-hole 設成家用網路的 DNS 伺服器
- 新增或管理封鎖清單
- 設定 DNS-over-HTTPS（DoH）上游 resolver
- 建立本地 DNS 記錄（例如 `nas.home.lan`、`pi.home.lan`）
- 排查裝了 Pi-hole 之後就連不上網的裝置
- 讓 Pi-hole 跟 DHCP 並行，或取代 DHCP

## How Pi-hole Works

```
Normal flow (without Pi-hole):
  Device → requests ads.tracker.com → ISP DNS → real IP → ads load

With Pi-hole:
  Device → requests ads.tracker.com → Pi-hole DNS → blocked (returns 0.0.0.0) → no ad

All DNS queries go through Pi-hole first.
Pi-hole checks against blocklists.
Blocked domains return a null response — the ad/tracker never loads.
Allowed domains get forwarded to your upstream resolver (Cloudflare, Google, etc.).
```

## Installation

### Docker (Recommended)

Docker 是安裝 Pi-hole 最簡單的方式，更新和備份也很直接。

```yaml
# docker-compose.yml
services:
  pihole:
    image: pihole/pihole:<pinned-release-tag>
    container_name: pihole
    ports:
      - "53:53/tcp"
      - "53:53/udp"
      - "80:80/tcp"          # Web admin
    environment:
      TZ: "America/New_York"
      WEBPASSWORD: "${PIHOLE_WEBPASSWORD}"   # set via .env file or secret
      PIHOLE_DNS_: "1.1.1.1;1.0.0.1"
      DNSMASQ_LISTENING: "all"
    volumes:
      - "./etc-pihole:/etc/pihole"
      - "./etc-dnsmasq.d:/etc/dnsmasq.d"
    restart: unless-stopped
    cap_add:
      - NET_ADMIN              # only needed if Pi-hole will serve DHCP
```

部署前，把 `<pinned-release-tag>` 換成目前的 Pi-hole release tag。
長期運作的 DNS 基礎設施不要用 `latest`，這樣升級才是刻意的，
而且可以審查。

把 `PIHOLE_WEBPASSWORD` 設在 `docker-compose.yml` 旁邊的 `.env` 檔，
權限 chmod 成 `600`，而且不要進 git，絕對不要把密碼直接寫在 compose 檔裡。

管理介面網址：`http://<pi-ip>/admin`

### Bare-Metal Install (Raspberry Pi OS / Debian / Ubuntu)

安裝 Pi-hole 之前必須先有固定 IP。

```bash
# Step 1: Assign a static IP (edit /etc/dhcpcd.conf on Pi OS)
sudo nano /etc/dhcpcd.conf
# Add at the bottom:
interface eth0
static ip_address=192.168.3.2/24
static routers=192.168.3.1
static domain_name_servers=192.168.3.1

# Step 2: Download and inspect the installer before running it.
# Prefer the package or installer path documented by Pi-hole for your OS/version.
curl -sSL https://install.pi-hole.net -o pi-hole-install.sh
less pi-hole-install.sh   # review before proceeding

# Step 3: Run
bash pi-hole-install.sh

# Follow the interactive installer:
# 1. Select network interface (eth0 for wired — recommended)
# 2. Select upstream DNS (Cloudflare or leave default — can change later)
# 3. Confirm static IP
# 4. Install the web admin interface (recommended)
# 5. Note the admin password shown at the end
```

## Pointing Your Network at Pi-hole

```
# Method 1: Change DNS in your router DHCP settings (recommended)
  Router admin UI → DHCP Settings → DNS Server
  Primary DNS: 192.168.3.2  (Pi-hole IP)
  Secondary DNS: leave blank for strict blocking, or use a second Pi-hole.
                 A public fallback such as 1.1.1.1 improves availability during
                 rollout but can bypass blocking because clients may query it.

  All devices get Pi-hole as DNS automatically on next DHCP renewal.
  Force renewal: reconnect Wi-Fi or run 'sudo dhclient -r && sudo dhclient' on Linux

# Method 2: Per-device DNS (useful for testing before network-wide rollout)
  Windows: Control Panel → Network Adapter → IPv4 Properties → set DNS manually
  macOS: System Settings → Network → Details → DNS → set manually
  Linux: /etc/resolv.conf or NetworkManager

# Method 3: Pi-hole as DHCP server (replaces router DHCP)
  Pi-hole admin → Settings → DHCP → Enable
  Disable DHCP on your router first — two DHCP servers on the same network cause conflicts
  Advantage: hostname resolution works automatically (devices register their names)
```

## Blocklist Management

```
# Pi-hole admin → Adlists → Add new adlist

# Recommended blocklists:
  https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts
  # default — 200k+ domains

  https://blocklistproject.github.io/Lists/malware.txt
  # malware domains

  https://blocklistproject.github.io/Lists/tracking.txt
  # tracking/telemetry

# After adding a list:
  Tools → Update Gravity  (downloads and compiles all blocklists)

# If a site is blocked that should not be (false positive):
  Pi-hole admin → Whitelist → Add domain
  Example: api.my-legitimate-service.com

# Check what is being blocked in real time:
  Dashboard → Query Log  (live DNS query stream with block/allow status)
```

## DNS-over-HTTPS Upstream

DNS-over-HTTPS 會加密你的 DNS 查詢，讓 ISP 看不到你解析了哪些網站。

```bash
# Install cloudflared (Cloudflare's DoH proxy).
# Prefer Cloudflare's package repository for automatic signed package verification.
# If you download a binary directly, pin a release version and verify its checksum.
CLOUDFLARED_VERSION="<pinned-version>"
curl -LO "https://github.com/cloudflare/cloudflared/releases/download/${CLOUDFLARED_VERSION}/cloudflared-linux-arm64"
# Verify the checksum/signature from Cloudflare's release notes before installing.
sudo mv cloudflared-linux-arm64 /usr/local/bin/cloudflared
sudo chmod +x /usr/local/bin/cloudflared

# Create cloudflared config
sudo mkdir -p /etc/cloudflared
sudo tee /etc/cloudflared/config.yml << EOF
proxy-dns: true
proxy-dns-port: 5053
proxy-dns-upstream:
  - https://1.1.1.1/dns-query
  - https://1.0.0.1/dns-query
EOF

# Create systemd service
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared

# Now point Pi-hole at the local DoH proxy:
# Pi-hole admin → Settings → DNS → Custom upstream DNS
# Set to: 127.0.0.1#5053
# Uncheck all other upstream resolvers
```

## Local DNS Records

讓你的服務可以用名稱存取（例如 `nas.home.lan`、`grafana.home.lan`）。

> **網域名稱備註：** `.home.lan` 在 homelab 裡很常用，實際上也能運作。
> IETF 保留給本地使用的後綴是 `.home.arpa`（RFC 8375），想遵循
> 標準就用這個。Pi-hole 的 DNS 記錄不要用 `.local`，因為它會跟
> mDNS/Bonjour 衝突。

```
# Pi-hole admin → Local DNS → DNS Records

  Domain              IP
  nas.home.lan        192.168.30.10
  pi.home.lan         192.168.30.2
  grafana.home.lan    192.168.30.3
  proxmox.home.lan    192.168.30.4

# From any device on your network:
  ping nas.home.lan        → 192.168.30.10
  http://grafana.home.lan  → your Grafana dashboard

# For subdomains, add a CNAME:
  Pi-hole admin → Local DNS → CNAME Records
  Domain: portainer.home.lan → Target: pi.home.lan
```

## Troubleshooting

```bash
# Pi-hole blocking something it should not
pihole -q example.com          # Check if domain is blocked and which list
pihole -w example.com          # Whitelist immediately

# DNS not resolving at all
pihole status                  # Check if pihole-FTL is running
dig @192.168.3.2 google.com   # Test DNS directly against Pi-hole

# Restart Pi-hole DNS
pihole restartdns

# Check query logs for a specific device
pihole -t                      # Live tail of all queries
# Or filter by client in the web admin Query Log

# Pi-hole gravity update (refresh blocklists)
pihole -g
```

## Anti-Patterns

```
# BAD: Depending on one Pi-hole without a recovery path
# If Pi-hole crashes or the Pi loses power, DNS can stop working
# GOOD: Keep a documented router fallback for rollback during setup
# BETTER: Run two Pi-hole instances for redundancy; avoid public fallback DNS for strict blocking

# BAD: Installing Pi-hole without a static IP
# If the Pi gets a new DHCP IP, all devices lose DNS
# GOOD: Set static IP first, then install Pi-hole

# BAD: Enabling Pi-hole DHCP without disabling the router's DHCP first
# Two DHCP servers on the same network hand out conflicting IPs
# GOOD: Disable router DHCP, then enable Pi-hole DHCP

# BAD: Never updating gravity (blocklists)
# New ad and malware domains accumulate — stale lists miss them
# GOOD: Schedule weekly gravity update: pihole -g (or enable in Settings → API)
```

## Best Practices

- 安裝 Pi-hole 之前，先讓 Pi 有固定 IP 或 DHCP 保留位址
- 把 Pi-hole 當主要 DNS；如果需要嚴格封鎖，要做備援就再加第二台 Pi-hole，
  不要用公開的 resolver
- 用 cloudflared 啟用 DoH（DNS-over-HTTPS），讓上游查詢加密
- 把 `home.lan` 設成本地網域，並為所有服務建立 DNS 記錄
- 偶爾看看 Query Log，被封鎖的查詢會讓你知道各裝置在做什麼

## Related Skills

- homelab-network-setup
- homelab-vlan-segmentation
- homelab-wireguard-vpn
