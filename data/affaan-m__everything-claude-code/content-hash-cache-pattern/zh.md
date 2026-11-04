---
name: content-hash-cache-pattern
description: 用 SHA-256 內容雜湊快取昂貴的檔案處理結果：與路徑無關、自動失效，並且分離服務層。適用於重複處理檔案很慢、結果應該依內容（而不是路徑）來快取和失效時。
metadata:
  origin: ECC
---

# Content-Hash File Cache Pattern

用 SHA-256 內容雜湊當作快取 key，快取昂貴的檔案處理結果（PDF 解析、文字擷取、圖片分析）。跟以路徑為基礎的快取不同，這個做法在檔案被搬移/改名後依然有效，內容改變時會自動失效。

## When to Activate

- 建構檔案處理管線（PDF、圖片、文字擷取）
- 處理成本很高，而且同樣的檔案會被重複處理
- 需要 `--cache/--no-cache` 的 CLI 選項
- 想在不修改現有純函式的情況下，替它們加上快取

## Core Pattern

### 1. Content-Hash Based Cache Key

用檔案內容（不是路徑）當作快取 key：

```python
import hashlib
from pathlib import Path

_HASH_CHUNK_SIZE = 65536  # 64KB chunks for large files

def compute_file_hash(path: Path) -> str:
    """SHA-256 of file contents (chunked for large files)."""
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(_HASH_CHUNK_SIZE)
            if not chunk:
                break
            sha256.update(chunk)
    return sha256.hexdigest()
```

**為什麼用內容雜湊？** 檔案改名/搬移 = 快取命中。內容改變 = 自動失效。不需要索引檔。

### 2. Frozen Dataclass for Cache Entry

```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class CacheEntry:
    file_hash: str
    source_path: str
    document: ExtractedDocument  # The cached result
```

### 3. File-Based Cache Storage

每個快取項目存成 `{hash}.json`，用雜湊就能 O(1) 查找，不需要索引檔。

```python
import json
from typing import Any

def write_cache(cache_dir: Path, entry: CacheEntry) -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f"{entry.file_hash}.json"
    data = serialize_entry(entry)
    cache_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

def read_cache(cache_dir: Path, file_hash: str) -> CacheEntry | None:
    cache_file = cache_dir / f"{file_hash}.json"
    if not cache_file.is_file():
        return None
    try:
        raw = cache_file.read_text(encoding="utf-8")
        data = json.loads(raw)
        return deserialize_entry(data)
    except (json.JSONDecodeError, ValueError, KeyError):
        return None  # Treat corruption as cache miss
```

### 4. Service Layer Wrapper (SRP)

讓處理函式保持純粹。把快取當成獨立的服務層加上去。

```python
def extract_with_cache(
    file_path: Path,
    *,
    cache_enabled: bool = True,
    cache_dir: Path = Path(".cache"),
) -> ExtractedDocument:
    """Service layer: cache check -> extraction -> cache write."""
    if not cache_enabled:
        return extract_text(file_path)  # Pure function, no cache knowledge

    file_hash = compute_file_hash(file_path)

    # Check cache
    cached = read_cache(cache_dir, file_hash)
    if cached is not None:
        logger.info("Cache hit: %s (hash=%s)", file_path.name, file_hash[:12])
        return cached.document

    # Cache miss -> extract -> store
    logger.info("Cache miss: %s (hash=%s)", file_path.name, file_hash[:12])
    doc = extract_text(file_path)
    entry = CacheEntry(file_hash=file_hash, source_path=str(file_path), document=doc)
    write_cache(cache_dir, entry)
    return doc
```

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| SHA-256 內容雜湊 | 與路徑無關，內容改變時自動失效 |
| `{hash}.json` 檔案命名 | O(1) 查找，不需要索引檔 |
| 服務層包裝 | SRP：擷取保持純粹，快取是獨立的關注點 |
| 手動 JSON 序列化 | 完全掌控 frozen dataclass 的序列化 |
| 損毀時回傳 `None` | 優雅降級，下次執行時重新處理 |
| `cache_dir.mkdir(parents=True)` | 第一次寫入時才延遲建立目錄 |

## Best Practices

- **雜湊內容，不要雜湊路徑**：路徑會變，內容的身分不會變
- 雜湊時要**分塊處理大檔案**，避免把整個檔案載入記憶體
- **讓處理函式保持純粹**：它們不該知道任何跟快取有關的事
- **記錄快取命中/未命中**，並用截短的雜湊方便除錯
- **優雅處理損毀**：把無效的快取項目視為未命中，絕對不要當掉

## Anti-Patterns to Avoid

```python
# BAD: Path-based caching (breaks on file move/rename)
cache = {"/path/to/file.pdf": result}

# BAD: Adding cache logic inside the processing function (SRP violation)
def extract_text(path, *, cache_enabled=False, cache_dir=None):
    if cache_enabled:  # Now this function has two responsibilities
        ...

# BAD: Using dataclasses.asdict() with nested frozen dataclasses
# (can cause issues with complex nested types)
data = dataclasses.asdict(entry)  # Use manual serialization instead
```

## When to Use

- 檔案處理管線（PDF 解析、OCR、文字擷取、圖片分析）
- 受益於 `--cache/--no-cache` 選項的 CLI 工具
- 同樣的檔案會在多次執行中重複出現的批次處理
- 在不修改現有純函式的情況下加上快取

## When NOT to Use

- 必須永遠保持最新的資料（即時資料流）
- 會變得極大的快取項目（考慮改用串流）
- 結果取決於檔案內容以外的參數（例如不同的擷取設定）
