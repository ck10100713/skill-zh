---
name: protocol-reverse-engineering
description: 精通網路協定逆向工程，包含封包分析、協定解析與自訂協定文件化。在分析網路流量、理解專有協定或除錯網路通訊時使用。
---

# Protocol Reverse Engineering

為了資安研究、互通性與除錯，擷取、分析並記錄網路協定的完整技術。

## Traffic Capture

### Wireshark Capture

```bash
# Capture on specific interface
wireshark -i eth0 -k

# Capture with filter
wireshark -i eth0 -k -f "port 443"

# Capture to file
tshark -i eth0 -w capture.pcap

# Ring buffer capture (rotate files)
tshark -i eth0 -b filesize:100000 -b files:10 -w capture.pcap
```

### tcpdump Capture

```bash
# Basic capture
tcpdump -i eth0 -w capture.pcap

# With filter
tcpdump -i eth0 port 8080 -w capture.pcap

# Capture specific bytes
tcpdump -i eth0 -s 0 -w capture.pcap  # Full packet

# Real-time display
tcpdump -i eth0 -X port 80
```

### Man-in-the-Middle Capture

```bash
# mitmproxy for HTTP/HTTPS
mitmproxy --mode transparent -p 8080

# SSL/TLS interception
mitmproxy --mode transparent --ssl-insecure

# Dump to file
mitmdump -w traffic.mitm

# Burp Suite
# Configure browser proxy to 127.0.0.1:8080
```

## Protocol Analysis

### Wireshark Analysis

```
# Display filters
tcp.port == 8080
http.request.method == "POST"
ip.addr == 192.168.1.1
tcp.flags.syn == 1 && tcp.flags.ack == 0
frame contains "password"

# Following streams
Right-click > Follow > TCP Stream
Right-click > Follow > HTTP Stream

# Export objects
File > Export Objects > HTTP

# Decryption
Edit > Preferences > Protocols > TLS
  - (Pre)-Master-Secret log filename
  - RSA keys list
```

### tshark Analysis

```bash
# Extract specific fields
tshark -r capture.pcap -T fields -e ip.src -e ip.dst -e tcp.port

# Statistics
tshark -r capture.pcap -q -z conv,tcp
tshark -r capture.pcap -q -z endpoints,ip

# Filter and extract
tshark -r capture.pcap -Y "http" -T json > http_traffic.json

# Protocol hierarchy
tshark -r capture.pcap -q -z io,phs
```

### Scapy for Custom Analysis

```python
from scapy.all import *

# Read pcap
packets = rdpcap("capture.pcap")

# Analyze packets
for pkt in packets:
    if pkt.haslayer(TCP):
        print(f"Src: {pkt[IP].src}:{pkt[TCP].sport}")
        print(f"Dst: {pkt[IP].dst}:{pkt[TCP].dport}")
        if pkt.haslayer(Raw):
            print(f"Data: {pkt[Raw].load[:50]}")

# Filter packets
http_packets = [p for p in packets if p.haslayer(TCP)
                and (p[TCP].sport == 80 or p[TCP].dport == 80)]

# Create custom packets
pkt = IP(dst="target")/TCP(dport=80)/Raw(load="GET / HTTP/1.1\r\n")
send(pkt)
```

## Protocol Identification

### Common Protocol Signatures

```
HTTP        - "HTTP/1." or "GET " or "POST " at start
TLS/SSL     - 0x16 0x03 (record layer)
DNS         - UDP port 53, specific header format
SMB         - 0xFF 0x53 0x4D 0x42 ("SMB" signature)
SSH         - "SSH-2.0" banner
FTP         - "220 " response, "USER " command
SMTP        - "220 " banner, "EHLO" command
MySQL       - 0x00 length prefix, protocol version
PostgreSQL  - 0x00 0x00 0x00 startup length
Redis       - "*" RESP array prefix
MongoDB     - BSON documents with specific header
```

### Protocol Header Patterns

```
+--------+--------+--------+--------+
|  Magic number / Signature         |
+--------+--------+--------+--------+
|  Version       |  Flags          |
+--------+--------+--------+--------+
|  Length        |  Message Type   |
+--------+--------+--------+--------+
|  Sequence Number / Session ID     |
+--------+--------+--------+--------+
|  Payload...                       |
+--------+--------+--------+--------+
```

在做二進位協定或加密分析之前，先讀[解析器、結構辨識與 TLS 技巧](references/binary-encryption-analysis.md)。

在記錄協定或撰寫 dissector 之前，先讀[規格範本與 Lua 範例](references/protocol-documentation.md)。

## Active Testing

### Fuzzing with Boofuzz

```python
from boofuzz import *

def main():
    session = Session(
        target=Target(
            connection=TCPSocketConnection("target", 8888)
        )
    )

    # Define protocol structure
    s_initialize("HELLO")
    s_static(b"\x50\x52\x4f\x54")  # Magic
    s_word(1, name="version")       # Version
    s_word(0x01, name="type")       # Type (HELLO)
    s_size("payload", length=4)     # Length field
    s_block_start("payload")
    s_dword(0x12345678, name="client_id")
    s_word(0, name="flags")
    s_block_end()

    session.connect(s_get("HELLO"))
    session.fuzz()

if __name__ == "__main__":
    main()
```

### Replay and Modification

```python
from scapy.all import *

# Replay captured traffic
packets = rdpcap("capture.pcap")
for pkt in packets:
    if pkt.haslayer(TCP) and pkt[TCP].dport == 8888:
        send(pkt)

# Modify and replay
for pkt in packets:
    if pkt.haslayer(Raw):
        # Modify payload
        original = pkt[Raw].load
        modified = original.replace(b"client", b"CLIENT")
        pkt[Raw].load = modified
        # Recalculate checksums
        del pkt[IP].chksum
        del pkt[TCP].chksum
        send(pkt)
```

## Best Practices

### Analysis Workflow

1. **擷取流量**：多個 session、不同情境
2. **辨識邊界**：訊息的開頭/結尾標記
3. **對應結構**：固定標頭、可變 payload
4. **辨識欄位**：比較多個樣本
5. **記錄格式**：建立規格
6. **驗證理解**：實作 parser/generator
7. **測試邊界案例**：fuzzing、邊界條件

### Common Patterns to Look For

- 訊息開頭的魔術數字/簽章
- 用於相容性的版本欄位
- 長度欄位（通常在可變資料之前）
- 用來辨識訊息的型別/opcode 欄位
- 用於排序的序號
- 用於完整性的 checksum/CRC
- 用於計時的時間戳記
- Session/連線識別碼
