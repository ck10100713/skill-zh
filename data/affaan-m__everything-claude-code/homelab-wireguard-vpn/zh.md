---
name: homelab-wireguard-vpn
description: WireGuard VPN 伺服器設定、peer 設定、金鑰產生、split tunnel 與 full tunnel 路由的選擇，以及從手機和筆電 client 遠端存取家用網路。要設定 WireGuard 來遠端存取家用網路，或要在 split 與 full tunnel 路由之間做決定時使用。
metadata:
  origin: community
---

# Homelab WireGuard VPN

WireGuard 是快速又現代的 VPN 協定。遠端存取家用網路選它就對了，
設定比 OpenVPN 簡單，速度也比大多數替代方案快。

所有設定範例都是常見的配置。套用到你的系統之前，每條指令都要自己檢查，
尤其是 iptables 的轉發規則和金鑰檔案的權限，
而且要在維護時段進行變更。

## When to Use

- 在 Raspberry Pi、Linux 主機、pfSense 或 router 上設定 WireGuard 伺服器
- 產生 WireGuard 金鑰對，並撰寫 peer 設定檔
- 設定手機或筆電對家用網路的遠端存取
- 解釋 split tunnel（只路由家裡的流量）與 full tunnel（路由所有流量）
- 排查連不起來的 WireGuard 連線
- 為多個 client 自動產生 peer 設定

## How WireGuard Works

```
Your phone (WireGuard client)
    │
    │  Encrypted UDP tunnel (port 51820)
    │
Your home router (WireGuard server — needs a public IP or DDNS)
    │
    Your home network (192.168.1.0/24, NAS, Pi, etc.)

Every device has a keypair (public + private key).
The server knows each client's public key.
The client knows the server's public key + endpoint (IP:port).
Traffic is encrypted end-to-end with no central server or certificate authority.
```

## Server Setup (Linux)

```bash
# Install WireGuard
sudo apt update && sudo apt install wireguard -y

# Generate server keypair — create files with private permissions from the start
sudo mkdir -p /etc/wireguard
sudo sh -c 'umask 077; wg genkey > /etc/wireguard/server_private.key'
sudo sh -c 'wg pubkey < /etc/wireguard/server_private.key > /etc/wireguard/server_public.key'

# Write server config — substitute the actual private key value
# Do not store private keys in version control or share them
sudo tee /etc/wireguard/wg0.conf << 'EOF'
[Interface]
Address = 10.8.0.1/24              # VPN subnet — server gets .1
ListenPort = 51820
PrivateKey = <paste_server_private_key_here>

# Scoped forwarding rules: allow VPN traffic in/out, not a blanket FORWARD ACCEPT
PostUp   = iptables -A FORWARD -i wg0 -o eth0 -j ACCEPT
PostUp   = iptables -A FORWARD -i eth0 -o wg0 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
PostUp   = iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -o eth0 -j ACCEPT
PostDown = iptables -D FORWARD -i eth0 -o wg0 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
PostDown = iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

[Peer]
# Phone — replace with the actual phone public key
PublicKey = <phone_public_key>
AllowedIPs = 10.8.0.2/32

[Peer]
# Laptop — replace with the actual laptop public key
PublicKey = <laptop_public_key>
AllowedIPs = 10.8.0.3/32
EOF
sudo chmod 600 /etc/wireguard/wg0.conf

# Replace eth0 with your actual outbound interface name
# Check with: ip route show default

# Enable IP forwarding (required for routing traffic through the server)
echo "net.ipv4.ip_forward=1" | sudo tee /etc/sysctl.d/99-wireguard.conf
sudo sysctl --system

# Start WireGuard and enable on boot
sudo wg-quick up wg0
sudo systemctl enable wg-quick@wg0
```

## Client Configuration

```bash
# Generate a unique keypair for each client device
# Run on the client, or on the server and transfer the private key securely — never in plaintext
umask 077
wg genkey | tee phone_private.key | wg pubkey > phone_public.key

# Client config file (phone_wg0.conf):
[Interface]
PrivateKey = <phone_private_key>
Address = 10.8.0.2/32
DNS = 192.168.1.2                  # Optional: use Pi-hole for DNS over the tunnel

[Peer]
PublicKey = <server_public_key>
Endpoint = your-home-ip.ddns.net:51820  # Your public IP or DDNS hostname
AllowedIPs = 192.168.1.0/24            # Split tunnel: only home network traffic
# AllowedIPs = 0.0.0.0/0, ::/0        # Full tunnel: all traffic through VPN

PersistentKeepalive = 25              # Keep NAT hole open (required for mobile clients)
```

## Split Tunnel vs Full Tunnel

```
# Split tunnel: AllowedIPs = 192.168.1.0/24
  Only traffic destined for your home network goes through the VPN.
  Internet traffic (YouTube, Spotify) goes directly — better performance on mobile.
  Best for: "I just want to reach my NAS and Pi from anywhere."

# Full tunnel: AllowedIPs = 0.0.0.0/0, ::/0
  ALL traffic goes through your home internet connection.
  Useful for: piggybacking home DNS/Pi-hole ad blocking.
  Downside: home upload speed becomes your bottleneck everywhere.

# Multi-subnet split tunnel (most common homelab use case):
  AllowedIPs = 192.168.10.0/24, 192.168.20.0/24, 192.168.30.0/24, 10.8.0.0/24
  Routes all your VLANs through the tunnel; internet stays direct.
```

## Key Generation and Peer Management

```python
import subprocess

def generate_keypair() -> tuple[str, str]:
    """Generate a WireGuard keypair. Returns (private_key, public_key)."""
    private = subprocess.check_output(["wg", "genkey"]).decode().strip()
    public = subprocess.run(
        ["wg", "pubkey"], input=private.encode(), capture_output=True
    ).stdout.decode().strip()
    return private, public

def generate_preshared_key() -> str:
    return subprocess.check_output(["wg", "genpsk"]).decode().strip()

def build_client_config(
    client_private_key: str,
    client_vpn_ip: str,       # e.g. "10.8.0.3"
    server_public_key: str,
    server_endpoint: str,     # e.g. "home.example.com:51820"
    allowed_ips: str = "192.168.1.0/24",
    dns: str = "",
) -> str:
    dns_line = f"DNS = {dns}\n" if dns else ""
    return f"""[Interface]
PrivateKey = {client_private_key}
Address = {client_vpn_ip}/32
{dns_line}
[Peer]
PublicKey = {server_public_key}
Endpoint = {server_endpoint}
AllowedIPs = {allowed_ips}
PersistentKeepalive = 25
"""

def build_server_peer_block(
    client_public_key: str,
    client_vpn_ip: str,
    comment: str = "",
) -> str:
    comment_line = f"# {comment}\n" if comment else ""
    return f"""
{comment_line}[Peer]
PublicKey = {client_public_key}
AllowedIPs = {client_vpn_ip}/32
"""
```

私鑰絕對不要進版本控制。如果你要用這支 script，金鑰內容要寫到
權限 600 的檔案，而且絕對不要 log 或 print 出來。

## pfSense / OPNsense WireGuard

```
# pfSense: VPN → WireGuard → Add Tunnel
  Interface Keys: Generate (creates keypair automatically)
  Listen Port: 51820
  Interface Address: 10.8.0.1/24

# Add Peer (one per client):
  Public Key: <client public key>
  Allowed IPs: 10.8.0.2/32

# Assign the WireGuard interface:
  Interfaces → Assignments → Add (select wg0)
  Enable interface, no IP needed (it is set in the tunnel config)

# Firewall rules:
  WAN → Allow UDP port 51820 inbound (so clients can reach the server)
  WireGuard interface → Allow traffic to LAN networks you want reachable
```

## DDNS (Dynamic DNS) for Home Servers

大多數家用網路是動態 IP。用 DDNS，這樣 IP 變了之後，
VPN endpoint 還是連得到。

```bash
# Option 1: Cloudflare DDNS — store credentials in a secrets file, not inline
# docker-compose entry using an env file:
  ddns-updater:
    image: qmcgaw/ddns-updater
    env_file: ./ddns.env   # store zone_id and token here, not in compose
    restart: unless-stopped

# ddns.env (chmod 600, not committed to git):
# SETTINGS_CLOUDFLARE_ZONE_ID=your_zone_id
# SETTINGS_CLOUDFLARE_TOKEN=your_api_token

# Option 2: DuckDNS (free, simple)
  Sign up at duckdns.org → get a token and subdomain (myhome.duckdns.org)
  Store token in /etc/ddns.env (mode 600), then use a small root-owned script:

  # /usr/local/bin/update-duckdns
  #!/bin/sh
  set -eu
  . /etc/ddns.env
  curl --fail --silent --show-error --max-time 10 \
    --get "https://www.duckdns.org/update" \
    --data-urlencode "domains=myhome" \
    --data-urlencode "token=${DUCKDNS_TOKEN}" \
    --data-urlencode "ip="

  # Cron job:
  */5 * * * * /usr/local/bin/update-duckdns >/dev/null 2>&1
```

## Troubleshooting

```bash
# Check WireGuard status and last handshake
sudo wg show

# If "latest handshake" is never or very old, the tunnel is not connected.
# Check:
# 1. Is UDP port 51820 open on the router/firewall?
sudo ufw status  # or check pfSense/UniFi firewall rules

# 2. Is the server public key in the client config correct?
sudo wg show wg0 public-key   # Compare to what is in the client config

# 3. Is IP forwarding enabled on the server?
cat /proc/sys/net/ipv4/ip_forward  # Should be 1

# 4. Does the client AllowedIPs cover the IP you are trying to reach?
# If AllowedIPs = 192.168.1.0/24 and you are trying to reach 192.168.3.5, it will not route.

# Check kernel logs for WireGuard errors
dmesg | grep wireguard

# Restart WireGuard
sudo wg-quick down wg0 && sudo wg-quick up wg0
```

## Anti-Patterns

```
# BAD: Storing private keys in version control or sharing them
# Private keys are equivalent to passwords — never commit them to git

# BAD: Using AllowedIPs = 0.0.0.0/0 on mobile without considering the impact
# Full tunnel routes all mobile traffic through your home upload — usually slow

# BAD: Not setting PersistentKeepalive on mobile clients
# Mobile clients behind NAT drop idle tunnels without it

# BAD: Opening port 51820 in the firewall but forgetting IP forwarding on the server
# Tunnel connects but no traffic routes — confusing to debug

# BAD: Sharing a keypair across multiple client devices
# Each device must have its own unique keypair — shared keys break the security model

# BAD: Using a broad "FORWARD ACCEPT" iptables rule
# Scope forwarding rules to the wg0 interface and direction only
```

## Best Practices

- 每個 client 裝置都產生獨立的金鑰對，絕對不要重複使用金鑰
- 手機用 split tunnel（`AllowedIPs = <home subnets>`）
- 所有手機 client 都設定 `PersistentKeepalive = 25`
- 如果 ISP 配的是動態 IP，就用 DDNS；憑證放在 env 檔，不要寫在行內
- 用有限定範圍的 iptables 轉發規則（只放行 wg0 的 inbound），不要用全面的 FORWARD ACCEPT
- 在 client 設定裡把 Pi-hole 的 IP 加進 `DNS =`，這樣走 VPN 也能擋廣告
- 定期輪替伺服器的金鑰對，並更新所有 client 設定

## Related Skills

- homelab-network-setup
- homelab-vlan-segmentation
- homelab-pihole-dns
