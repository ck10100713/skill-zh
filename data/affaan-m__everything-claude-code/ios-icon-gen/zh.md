---
name: ios-icon-gen
description: 從 SF Symbols（5000+ 個 Apple 原生圖示）或 Iconify API（200+ 個圖示集、275k+ 個開源圖示），為 Xcode asset catalog 產生 PNG 格式的 iOS app 圖示 imageset。產生圖示、建立圖示資源、把圖示加進 asset catalog，或替 iOS 專案搜尋圖示時使用。
metadata:
  origin: community
---

# iOS Icon Generator

從兩個來源為 Xcode asset catalog 產生 PNG 圖示 imageset。

## When to Activate

- 為 iOS/macOS 的 Xcode 專案產生圖示資源
- 在開源圖示集裡搜尋圖示
- 為 asset catalog 建立 PNG imageset（1x、2x、3x）
- 把佔位圖示換成正式品質的資源
- 對齊 Xcode 專案中既有的圖示風格

## Core Principles

### 1. Two Sources, One Output Format
兩個來源產出的 imageset 完全一樣，都相容 Xcode。依需求選擇：

| 來源 | 圖示數 | 需求 | 最適合 |
|--------|-------|----------|----------|
| **Iconify API** | 200+ 個圖示集共 275,000+ 個 | 網路 | 選擇多、特定風格、開源圖示 |
| **SF Symbols** | 5,000+ 個 Apple 符號 | 只限 macOS | Apple 原生風格、離線使用 |

### 2. Always Match Existing Style
產生之前，先檢查專案現有圖示的尺寸、顏色和粗細是否一致。

### 3. Output Structure
兩種方式都會產生完整的 Xcode imageset：

```
<output-dir>/<asset-name>.imageset/
  Contents.json
  <asset-name>.png        # 1x (68px default)
  <asset-name>@2x.png     # 2x (136px default)
  <asset-name>@3x.png     # 3x (204px default)
```

## Examples

### Step 1: Assess Requirements

確定圖示需求：圖示代表什麼、偏好的風格、目標顏色和尺寸。

如果專案已經有圖示，先檢查既有的風格：
```bash
# Check dimensions of existing icon
sips -g pixelWidth -g pixelHeight path/to/existing@2x.png
```

### Step 2: Search for Icons

**Iconify API（想要選擇多時推薦）：**
```bash
# Search all collections
$SKILL_DIR/scripts/iconify_gen.sh search "receipt"

# Search within a specific collection
$SKILL_DIR/scripts/iconify_gen.sh search "business card" --prefix mdi

# List available collections
$SKILL_DIR/scripts/iconify_gen.sh collections
```

**SF Symbols（想要 Apple 原生風格時）：**
瀏覽 SF Symbols app，或參考常用名稱：

| 使用情境 | 符號名稱 |
|----------|-------------|
| 文件 | `doc.text`, `doc.fill` |
| 收據 | `doc.text.below.ecg`, `receipt` |
| 人 | `person.crop.rectangle`, `person.text.rectangle` |
| 相機 | `camera`, `camera.fill` |
| 掃描 | `doc.viewfinder`, `qrcode.viewfinder` |
| 設定 | `gearshape`, `slider.horizontal.3` |

### Step 3: Preview (Optional)

```bash
# Iconify preview
$SKILL_DIR/scripts/iconify_gen.sh preview mdi:receipt-text-outline
```

### Step 4: Generate

**Iconify API：**
```bash
# Basic generation
$SKILL_DIR/scripts/iconify_gen.sh mdi:receipt-text-outline editTool_expenseReport

# Custom color and output location
$SKILL_DIR/scripts/iconify_gen.sh mdi:receipt-text-outline myIcon --color 007AFF --output ./Assets.xcassets/icons
```

選項：`--size <pt>`（預設：68）、`--color <hex>`（預設：8E8E93）、`--output <dir>`（預設：/tmp/icons）

**SF Symbols：**
```bash
# Basic generation
swift $SKILL_DIR/scripts/generate_icons.swift doc.text.below.ecg editTool_expenseReport

# Custom color, weight, and output
swift $SKILL_DIR/scripts/generate_icons.swift person.crop.rectangle myIcon --color 007AFF --weight regular --output ./Assets.xcassets/icons
```

選項：`--size <pt>`（預設：68）、`--color <hex>`（預設：8E8E93）、`--weight <name>`（預設：thin）、`--output <dir>`（預設：/tmp/icons）

### Step 5: Verify and Integrate

1. 讀產生的 @2x PNG，用肉眼確認
2. 如果沒有直接輸出到 asset catalog，就複製過去：
   ```bash
   cp -r /tmp/icons/<name>.imageset path/to/Assets.xcassets/<group>/
   ```
3. 建置專案，確認 Xcode 有抓到新的資源

## Popular Iconify Collections

| 前綴 | 名稱 | 數量 | 風格 |
|--------|------|-------|-------|
| `mdi` | Material Design Icons | 7400+ | 實心 + 外框版本 |
| `ph` | Phosphor | 9000+ | 每個圖示有 6 種粗細 |
| `solar` | Solar | 7400+ | 粗體、線性、外框 |
| `tabler` | Tabler Icons | 6000+ | 線條粗細一致 |
| `lucide` | Lucide | 1700+ | 乾淨、極簡 |
| `ri` | Remix Icon | 3100+ | 實心 + 線條版本 |
| `carbon` | Carbon | 2400+ | IBM 設計語言 |
| `heroicons` | HeroIcons | 1200+ | Tailwind CSS 的搭配組合 |

瀏覽全部：<https://icon-sets.iconify.design/>

## Scripts Reference

| Script | 來源 | 路徑 |
|--------|--------|------|
| `iconify_gen.sh` | Iconify API（275k+ 個圖示） | `$SKILL_DIR/scripts/iconify_gen.sh` |
| `generate_icons.swift` | SF Symbols（5k+ 個圖示） | `$SKILL_DIR/scripts/generate_icons.swift` |

## Best Practices

- **產生之前先搜尋**：瀏覽可用的圖示，找出最合適的
- **對齊專案既有風格**：產生新圖示之前，先檢查既有圖示的尺寸、顏色和粗細
- **要多樣性就用 Iconify**：200+ 個圖示集，你一定找得到要的風格
- **要 Apple 一致性就用 SF Symbols**：它們跟系統 UI 完美搭配
- **直接產生到 asset catalog**：用 `--output ./Assets.xcassets/icons` 省去手動複製
- **用肉眼驗證**：commit 之前一定要先預覽 @2x PNG

## Anti-Patterns

- 沒檢查專案既有的圖示風格就直接產生圖示
- 專案有既定色票，卻用預設顏色
- 用錯誤的尺寸產生（先檢查既有圖示）
- 沒做視覺驗證就 commit 產生出來的圖示
