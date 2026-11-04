---
name: repo-scan
description: 從固定、可審查的 commit 安裝外部 repo-scan skill 的啟動指引。在執行跨技術堆疊的原始碼資產稽核之前，必須先安裝 repo-scan 時使用；這個 ECC 指引本身不執行稽核。
metadata:
  origin: community
---

# repo-scan

> 每個生態系都有自己的依賴管理工具，但沒有任何工具能橫跨 C++、Android、iOS 和 Web，告訴你：到底有多少程式碼是自己的、哪些是第三方的、哪些是累贅。

## 何時使用

- 接手大型舊程式碼庫，需要結構性的總覽
- 大型重構之前：找出什麼是核心、什麼是重複、什麼是死碼
- 稽核直接嵌在原始碼裡的第三方依賴（沒有在套件管理工具中宣告）
- 為 monorepo 重組準備架構決策紀錄

## 安裝

```bash
# 先 clone，這樣才能在安裝前審查固定的 commit
set -euo pipefail

REPO_SCAN_COMMIT=2742664ebcad1450c208eda0ae45d3c17fad5dd8
REPO_SCAN_INSTALL_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/repo-scan"
REPO_SCAN_INSTALL_PARENT="$(dirname "$REPO_SCAN_INSTALL_DIR")"
mkdir -p "$REPO_SCAN_INSTALL_PARENT"
REPO_SCAN_TMP="$(mktemp -d "$REPO_SCAN_INSTALL_PARENT/.repo-scan-install.XXXXXX")"
REPO_SCAN_TOKEN="${REPO_SCAN_TMP##*.}"
REPO_SCAN_STAGE="$REPO_SCAN_TMP/stage-$REPO_SCAN_TOKEN"
REPO_SCAN_BACKUP="$REPO_SCAN_TMP/backup-$REPO_SCAN_TOKEN"
REPO_SCAN_LOCK="$REPO_SCAN_INSTALL_PARENT/.repo-scan-install.lock"
REPO_SCAN_KEEP_TMP=0
REPO_SCAN_LOCK_HELD=0
REPO_SCAN_MV_HAS_NO_TARGET=0
cleanup_repo_scan_install() {
  if [ "$REPO_SCAN_KEEP_TMP" -eq 0 ]; then
    rm -rf -- "$REPO_SCAN_TMP"
  fi
  if [ "$REPO_SCAN_LOCK_HELD" -eq 1 ] && ! rmdir -- "$REPO_SCAN_LOCK"; then
    printf 'Could not release installation lock at %s\n' "$REPO_SCAN_LOCK" >&2
  fi
}
trap cleanup_repo_scan_install EXIT
mkdir "$REPO_SCAN_TMP/mv-probe-source"
if mv -T -- "$REPO_SCAN_TMP/mv-probe-source" \
  "$REPO_SCAN_TMP/mv-probe-destination" 2>/dev/null; then
  REPO_SCAN_MV_HAS_NO_TARGET=1
  rmdir "$REPO_SCAN_TMP/mv-probe-destination"
else
  rmdir "$REPO_SCAN_TMP/mv-probe-source"
fi
move_repo_scan_dir() {
  REPO_SCAN_MOVE_SOURCE=$1
  REPO_SCAN_MOVE_DESTINATION=$2
  REPO_SCAN_MOVE_NAME=${REPO_SCAN_MOVE_SOURCE##*/}
  if [ -e "$REPO_SCAN_MOVE_DESTINATION" ] || [ -L "$REPO_SCAN_MOVE_DESTINATION" ]; then
    return 1
  fi
  if [ "$REPO_SCAN_MV_HAS_NO_TARGET" -eq 1 ]; then
    mv -T -- "$REPO_SCAN_MOVE_SOURCE" "$REPO_SCAN_MOVE_DESTINATION"
    return
  fi
  if ! mv -- "$REPO_SCAN_MOVE_SOURCE" "$REPO_SCAN_MOVE_DESTINATION"; then
    return 1
  fi
  if [ -e "$REPO_SCAN_MOVE_DESTINATION/$REPO_SCAN_MOVE_NAME" ] || \
    [ -L "$REPO_SCAN_MOVE_DESTINATION/$REPO_SCAN_MOVE_NAME" ]; then
    if ! mv -- "$REPO_SCAN_MOVE_DESTINATION/$REPO_SCAN_MOVE_NAME" \
      "$REPO_SCAN_MOVE_SOURCE"; then
      REPO_SCAN_KEEP_TMP=1
      printf 'Move conflict recovery failed; staged data remains at %s\n' \
        "$REPO_SCAN_MOVE_DESTINATION/$REPO_SCAN_MOVE_NAME" >&2
    fi
    return 1
  fi
}

git clone --filter=blob:none --no-checkout \
  https://github.com/haibindev/repo-scan.git "$REPO_SCAN_TMP/source"
git -C "$REPO_SCAN_TMP/source" checkout --detach "$REPO_SCAN_COMMIT"
mkdir -p "$REPO_SCAN_STAGE"
git -C "$REPO_SCAN_TMP/source" archive "$REPO_SCAN_COMMIT" | \
  tar -xf - -C "$REPO_SCAN_STAGE"

# 核准安裝之前，先審查 "$REPO_SCAN_TMP/source"。
printf 'Type install to replace %s after reviewing the pinned source: ' \
  "$REPO_SCAN_INSTALL_DIR" >&2
read -r REPO_SCAN_CONFIRM
if [ "$REPO_SCAN_CONFIRM" != install ]; then
  printf 'Installation cancelled.\n' >&2
  exit 1
fi
if ! mkdir -- "$REPO_SCAN_LOCK" 2>/dev/null; then
  printf 'Another repo-scan installation holds the lock at %s\n' \
    "$REPO_SCAN_LOCK" >&2
  exit 1
fi
REPO_SCAN_LOCK_HELD=1

if [ -e "$REPO_SCAN_INSTALL_DIR" ] || [ -L "$REPO_SCAN_INSTALL_DIR" ]; then
  move_repo_scan_dir "$REPO_SCAN_INSTALL_DIR" "$REPO_SCAN_BACKUP"
fi
if ! move_repo_scan_dir "$REPO_SCAN_STAGE" "$REPO_SCAN_INSTALL_DIR"; then
  if [ -e "$REPO_SCAN_BACKUP" ] || [ -L "$REPO_SCAN_BACKUP" ]; then
    if [ -e "$REPO_SCAN_INSTALL_DIR" ] || [ -L "$REPO_SCAN_INSTALL_DIR" ]; then
      REPO_SCAN_KEEP_TMP=1
      printf 'Replacement failed and target was recreated; previous installation preserved at %s\n' \
        "$REPO_SCAN_BACKUP" >&2
    elif ! move_repo_scan_dir "$REPO_SCAN_BACKUP" "$REPO_SCAN_INSTALL_DIR"; then
      REPO_SCAN_KEEP_TMP=1
      printf 'Replacement and rollback failed; previous installation preserved at %s\n' \
        "$REPO_SCAN_BACKUP" >&2
    fi
  fi
  exit 1
fi
```

> 安裝任何 agent skill 之前，都要先審查原始碼。

安裝只會完成啟動程序。重新載入你的 agent harness，然後再次呼叫 `repo-scan`。這個 ECC 指引會安裝外部 skill，但本身不會執行掃描。

## 核心能力

| 能力 | 說明 |
|---|---|
| **跨技術堆疊掃描** | 一次掃過 C/C++、Java/Android、iOS（OC/Swift）、Web（TS/JS/Vue） |
| **檔案分類** | 每個檔案都標成專案程式碼、第三方，或建置產物 |
| **函式庫偵測** | 50 多個已知函式庫（FFmpeg、Boost、OpenSSL…），並擷取版本 |
| **四級判定** | Core Asset／Extract & Merge／Rebuild／Deprecate |
| **HTML 報告** | 互動式深色主題頁面，可逐層下鑽 |
| **Monorepo 支援** | 階層式掃描，附彙總與子專案報告 |

## 分析深度等級

| 等級 | 讀取的檔案 | 使用情境 |
|---|---|---|
| `fast` | 每個模組 1-2 個 | 快速盤點巨大的目錄 |
| `standard` | 每個模組 2-5 個 | 預設的稽核，含完整的依賴與架構檢查 |
| `deep` | 每個模組 5-10 個 | 加上 thread safety、記憶體管理、API 一致性 |
| `full` | 所有檔案 | merge 前的完整 review |

## 運作方式

1. **分類 repo 表面**：列舉檔案，然後把每個標成專案程式碼、嵌入的第三方程式碼，或建置產物。
2. **偵測嵌入的函式庫**：檢查目錄名稱、header、授權檔案和版本標記，找出打包進來的依賴和可能的版本。
3. **替每個模組評分**：依模組或子系統把檔案分組，再依所有權、重複程度和維護成本，給出四種判定之一。
4. **標出結構性風險**：點出累贅的產物、重複的 wrapper、過時的 vendored 程式碼，以及該抽出、重建或棄用的模組。
5. **產出報告**：回傳精簡的摘要，加上可逐模組下鑽的互動式 HTML 輸出，讓稽核結果可以非同步審閱。

## 範例

在一個 50,000 個檔案的 C++ monorepo 上：
- 發現 FFmpeg 2.x（2015 年份）仍在 production 使用
- 發現同一個 SDK wrapper 被複製了 3 份
- 找出 636 MB 被 commit 進來的 Debug/ipch/obj 建置產物
- 分類結果：3 MB 專案程式碼 vs 596 MB 第三方

## 最佳實踐

- 第一次稽核先用 `standard` 深度
- 有 100 個以上模組的 monorepo，用 `fast` 快速盤點
- 對被標記要重構的模組，漸進式地跑 `deep`
- 檢視跨模組分析，找出子專案之間的重複

## 連結

- [GitHub Repository](https://github.com/haibindev/repo-scan)
