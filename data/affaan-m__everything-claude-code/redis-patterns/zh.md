---
name: redis-patterns
description: 給 production 應用程式用的 Redis 資料結構模式、快取策略、分散式鎖、rate limiting、pub/sub 和連線管理。用 Redis 加快取、分散式鎖、rate limiting 或 pub/sub，或需要 review key 設計時使用。
metadata:
  origin: ECC
---

# Redis 模式

常見後端使用情境下的 Redis 最佳實踐速查。

## 運作方式

Redis 是記憶體內的資料結構儲存，支援 string、hash、list、set、sorted set、stream 等。單一個 Redis 指令在單一實例上是 atomic 的；多步驟的工作流程需要 Lua 腳本、MULTI/EXEC 交易，或明確的同步機制才能保持 atomic。資料可以選擇透過 RDB snapshot 或 AOF log 持久化。客戶端透過 TCP 用 RESP 協定溝通；連線池是必要的，才能避免每次請求都要握手的額外負擔。

## 何時啟用

- 為應用程式加快取
- 實作 rate limiting 或節流
- 建立分散式鎖或協調機制
- 設定 session 或 token 儲存
- 用 Pub/Sub 或 Redis Streams 做訊息傳遞
- 在 production 設定 Redis（連線池、淘汰、叢集）

## 資料結構速查表

| 使用情境 | 結構 | 範例 Key |
|----------|-----------|-------------|
| 簡單快取 | String | `product:123` |
| 使用者 session | Hash | `session:abc` |
| 排行榜 | Sorted Set | `scores:weekly` |
| 不重複訪客 | Set | `visitors:2024-01-01` |
| 動態消息 | List | `feed:user:456` |
| 事件串流 | Stream | `events:orders` |
| 計數器／rate limit | String (INCR) | `ratelimit:user:123` |
| Bloom filter / HLL | HyperLogLog | `hll:pageviews` |

## 核心模式

### Cache-Aside（延遲載入）

```python
import redis
import json

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def get_product(product_id: int):
    cache_key = f"product:{product_id}"
    cached = r.get(cache_key)

    if cached:
        return json.loads(cached)

    product = db.query("SELECT * FROM products WHERE id = %s", product_id)
    r.setex(cache_key, 3600, json.dumps(product))  # TTL：1 小時
    return product
```

### Write-Through 快取

```python
def update_product(product_id: int, data: dict):
    # 先寫 DB
    db.execute("UPDATE products SET ... WHERE id = %s", product_id)

    # 馬上更新快取
    cache_key = f"product:{product_id}"
    r.setex(cache_key, 3600, json.dumps(data))
```

### 快取失效

```python
# 以 tag 為基礎的失效：把相關的 key 歸到一個 set 底下
def cache_product(product_id: int, category_id: int, data: dict):
    key = f"product:{product_id}"
    tag = f"tag:category:{category_id}"
    pipe = r.pipeline(transaction=True)
    pipe.setex(key, 3600, json.dumps(data))
    pipe.sadd(tag, key)
    pipe.expire(tag, 3600)
    pipe.execute()

def invalidate_category(category_id: int):
    tag = f"tag:category:{category_id}"
    keys = r.smembers(tag)
    if keys:
        r.delete(*keys)
    r.delete(tag)
```

### Session 儲存

```python
import time
import uuid

def create_session(user_id: int, ttl: int = 86400) -> str:
    session_id = str(uuid.uuid4())
    key = f"session:{session_id}"
    pipe = r.pipeline(transaction=True)
    pipe.hset(key, mapping={
        "user_id": user_id,
        "created_at": int(time.time()),
    })
    pipe.expire(key, ttl)
    pipe.execute()
    return session_id

def get_session(session_id: str) -> dict | None:
    data = r.hgetall(f"session:{session_id}")
    return data if data else None

def delete_session(session_id: str):
    r.delete(f"session:{session_id}")
```

## Rate Limiting

### 固定視窗（簡單）

```python
def is_rate_limited(user_id: int, limit: int = 100, window: int = 60) -> bool:
    key = f"ratelimit:{user_id}:{int(time.time()) // window}"
    pipe = r.pipeline(transaction=True)
    pipe.incr(key)
    pipe.expire(key, window)
    count, _ = pipe.execute()
    return count > limit
```

### 滑動視窗（Lua，Atomic）

```lua
-- sliding_window.lua
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])

redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
local count = redis.call('ZCARD', key)

if count < limit then
    -- 用不重複的 member（now + 序號），避免同一毫秒內碰撞
    local seq_key = key .. ':seq'
    local seq = redis.call('INCR', seq_key)
    redis.call('EXPIRE', seq_key, math.ceil(window / 1000))
    redis.call('ZADD', key, now, now .. '-' .. seq)
    redis.call('EXPIRE', key, math.ceil(window / 1000))
    return 1
end
return 0
```

```python
sliding_window = r.register_script(open('sliding_window.lua').read())

def allow_request(user_id: int) -> bool:
    key = f"ratelimit:sliding:{user_id}"
    now = int(time.time() * 1000)
    return bool(sliding_window(keys=[key], args=[now, 60000, 100]))
```

## 分散式鎖

### 分散式鎖（單節點，SET NX PX）

```python
import uuid

def acquire_lock(resource: str, ttl_ms: int = 5000) -> str | None:
    lock_key = f"lock:{resource}"
    token = str(uuid.uuid4())
    acquired = r.set(lock_key, token, px=ttl_ms, nx=True)
    return token if acquired else None

def release_lock(resource: str, token: str) -> bool:
    release_script = """
    if redis.call('get', KEYS[1]) == ARGV[1] then
        return redis.call('del', KEYS[1])
    else
        return 0
    end
    """
    result = r.eval(release_script, 1, f"lock:{resource}", token)
    return bool(result)

# 使用方式
token = acquire_lock("order:payment:123")
if token:
    try:
        process_payment()
    finally:
        release_lock("order:payment:123", token)
```

> 多節點的環境，請用實作了完整 Redlock 演算法的 `redlock-py` 函式庫。

## Pub/Sub 與 Streams

### Pub/Sub（Fire-and-Forget）

```python
# 發布者
def publish_event(channel: str, payload: dict):
    r.publish(channel, json.dumps(payload))

# 訂閱者（阻塞，要在獨立的 thread/process 執行）
def subscribe_events(channel: str):
    pubsub = r.pubsub()
    pubsub.subscribe(channel)
    for message in pubsub.listen():
        if message['type'] == 'message':
            handle(json.loads(message['data']))
```

### Redis Streams（持久的 Queue）

```python
# 生產者
def emit(stream: str, event: dict):
    r.xadd(stream, event, maxlen=10000)  # 限制 stream 長度

# Consumer group：保證至少投遞一次
try:
    r.xgroup_create('events:orders', 'processor', id='0', mkstream=True)
except Exception:
    pass  # group 已經存在

def consume(stream: str, group: str, consumer: str):
    while True:
        messages = r.xreadgroup(group, consumer, {stream: '>'}, count=10, block=2000)
        for _, entries in (messages or []):
            for msg_id, data in entries:
                process(data)
                r.xack(stream, group, msg_id)
```

> 需要投遞保證、consumer group 或 replay 時，優先用 **Streams**，不要用 Pub/Sub。

## Key 設計

### 命名慣例

```
# 模式：resource:id:field
user:123:profile
order:456:status
cache:product:789

# 模式：namespace:resource:id
myapp:session:abc123
myapp:ratelimit:user:123

# 模式：resource:date（有時間範圍的 key）
stats:pageviews:2024-01-01
```

### TTL 策略

| 資料類型 | 建議 TTL |
|-----------|--------------|
| 使用者 session | 24h（`86400`） |
| API 回應快取 | 5–15 分鐘 |
| Rate limit 視窗 | 與視窗大小相同 |
| 短效 token | 5–10 分鐘 |
| 排行榜 | 1h–24h |
| 靜態／參考資料 | 1h–1 週 |

一定要設 TTL。沒有 TTL 的 key 會無限累積，造成記憶體壓力。

## 連線管理

### 連線池

```python
from redis import ConnectionPool, Redis

pool = ConnectionPool(
    host='localhost',
    port=6379,
    db=0,
    max_connections=20,
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2,
)

r = Redis(connection_pool=pool)
```

### 叢集模式

```python
from redis.cluster import RedisCluster

r = RedisCluster(
    startup_nodes=[{"host": "redis-1", "port": 6379}],
    decode_responses=True,
    skip_full_coverage_check=True,
)
```

### Sentinel（高可用）

```python
from redis.sentinel import Sentinel

sentinel = Sentinel(
    [('sentinel-1', 26379), ('sentinel-2', 26379)],
    socket_timeout=0.5,
)
master = sentinel.master_for('mymaster', decode_responses=True)
replica = sentinel.slave_for('mymaster', decode_responses=True)
```

## 淘汰策略

| 策略 | 行為 | 最適合 |
|--------|----------|----------|
| `noeviction` | 滿了之後寫入會報錯 | Queue／關鍵資料 |
| `allkeys-lru` | 淘汰最久沒用的 | 一般快取 |
| `volatile-lru` | 只在有 TTL 的 key 之間做 LRU | 混合的資料儲存 |
| `allkeys-lfu` | 淘汰使用頻率最低的 | 存取分佈偏斜的模式 |
| `volatile-ttl` | 淘汰最快過期的 | 優先保留長壽的資料 |

透過 `redis.conf` 設定：`maxmemory-policy allkeys-lru`

## 反模式

| 反模式 | 問題 | 修正 |
|---|---|---|
| key 沒有 TTL | 記憶體無限成長 | 一律設 TTL |
| production 用 `KEYS *` | 會阻塞 server（O(N)） | 用 `SCAN` cursor |
| 存大型 blob（>100KB） | 序列化慢、記憶體壓力 | 存參照，再從物件儲存抓取 |
| 所有東西都用同一個 Redis | 快取和 queue 之間沒有隔離 | 用不同的 DB 或實例 |
| 忽略連線池上限 | 負載下連線耗盡 | 依 workload 調整連線池大小 |
| 沒處理快取未命中的 stampede | 冷啟動時 thundering herd | 用鎖或機率式提前過期 |
| 隨便就 `FLUSHALL` | 整個實例被清空 | 用 key 模式限定刪除範圍 |

### 預防快取未命中 Stampede

```python
import threading

_locks: dict[str, threading.Lock] = {}
_locks_mutex = threading.Lock()

def get_with_lock(key: str, fetch_fn, ttl: int = 300):
    cached = r.get(key)
    if cached:
        return json.loads(cached)

    with _locks_mutex:
        if key not in _locks:
            _locks[key] = threading.Lock()
        lock = _locks[key]
    with lock:
        cached = r.get(key)  # 取得鎖之後再檢查一次
        if cached:
            return json.loads(cached)
        value = fetch_fn()
        r.setex(key, ttl, json.dumps(value))
        return value
```

> 注意：多 process 部署時，把 process 內的鎖換成上面「分散式鎖」段落的 `acquire_lock`/`release_lock`。

## 範例

**為 Django/Flask API endpoint 加快取：**
用 cache-aside，搭配 `setex` 和 5 分鐘的 TTL 存回應。用請求參數當 key。

**依使用者對 API 做 rate limit：**
低流量的 endpoint 用固定視窗搭配 `pipeline(transaction=True)`；要精準的逐使用者節流，用滑動視窗 Lua。

**跨 worker 協調背景工作：**
用 `acquire_lock`，TTL 要超過預期的工作時間。一定要在 `finally` 區塊裡釋放。

**對多個訂閱者扇出通知：**
Pub/Sub 用於 fire-and-forget。需要保證投遞，或讓晚到的消費者 replay 時，改用 Streams。

## 速查

| 模式 | 何時使用 |
|---------|-------------|
| Cache-aside | 讀多寫少、可容忍輕微過期 |
| Write-through | 需要強一致性 |
| 分散式鎖 | 防止並行存取某個資源 |
| 滑動視窗 rate limit | 精準的逐使用者節流 |
| Redis Streams | 有 consumer group 的持久事件 queue |
| Pub/Sub | 廣播，不需要保證投遞 |
| Sorted Set 排行榜 | 排名評分、分頁 |
| HyperLogLog | 用低記憶體做近似的不重複計數 |

## 相關

- Skill：`postgres-patterns`：關聯式資料模式
- Skill：`backend-patterns`：API 與 service 層模式
- Skill：`database-migrations`：schema 版本管理
- Skill：`django-patterns`：Django 快取框架整合
- Agent：`database-reviewer`：完整的資料庫 review 流程
