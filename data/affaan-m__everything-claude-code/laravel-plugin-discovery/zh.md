---
name: laravel-plugin-discovery
description: 透過 LaraPlugins.io MCP 探索並評估 Laravel 套件。在使用者想找 plugin、檢查套件健康度，或評估 Laravel/PHP 相容性時使用。
metadata:
  origin: ECC
---

# Laravel Plugin Discovery

用 LaraPlugins.io MCP server 找出、評估並挑選健康的 Laravel 套件。

## 何時使用

- 使用者想找某個功能的 Laravel 套件（例如「auth」、「permissions」、「admin panel」）
- 使用者問「我該用哪個套件來做…」或「有沒有 Laravel 套件可以…」
- 使用者想確認某個套件有沒有持續維護
- 使用者需要確認 Laravel 版本相容性
- 使用者想在把套件加進專案前先評估它的健康度

## MCP 需求

必須先設定好 LaraPlugins MCP server。加到你的 `~/.claude.json` 的 mcpServers：

```json
"laraplugins": {
  "type": "http",
  "url": "https://laraplugins.io/mcp/plugins"
}
```

不需要 API key，這個 server 對 Laravel 社群是免費的。

## MCP 工具

LaraPlugins MCP 提供兩個主要工具：

### SearchPluginTool

依關鍵字、健康分數、vendor 與版本相容性搜尋套件。

**參數：**
- `text_search`（string，選填）：要搜尋的關鍵字（例如 "permission"、"admin"、"api"）
- `health_score`（string，選填）：依健康等級篩選，可用 `Healthy`、`Medium`、`Unhealthy` 或 `Unrated`
- `laravel_compatibility`（string，選填）：依 Laravel 版本篩選，可用 `"5"`、`"6"`、`"7"`、`"8"`、`"9"`、`"10"`、`"11"`、`"12"`、`"13"`
- `php_compatibility`（string，選填）：依 PHP 版本篩選，可用 `"7.4"`、`"8.0"`、`"8.1"`、`"8.2"`、`"8.3"`、`"8.4"`、`"8.5"`
- `vendor_filter`（string，選填）：依 vendor 名稱篩選（例如 "spatie"、"laravel"）
- `page`（number，選填）：分頁的頁碼

### GetPluginDetailsTool

取得特定套件的詳細指標、readme 內容與版本歷史。

**參數：**
- `package`（string，必填）：完整的 Composer 套件名稱（例如 "spatie/laravel-permission"）
- `include_versions`（boolean，選填）：在回應中包含版本歷史

---

## 運作方式

### 尋找套件

當使用者想找某個功能的套件時：

1. 用相關關鍵字呼叫 `SearchPluginTool`
2. 套用健康分數、Laravel 版本或 PHP 版本的篩選
3. 檢視結果中的套件名稱、說明與健康指標

### 評估套件

當使用者想評估特定套件時：

1. 用套件名稱呼叫 `GetPluginDetailsTool`
2. 檢視健康分數、最後更新日期、Laravel 版本支援
3. 檢查 vendor 的信譽與風險指標

### 檢查相容性

當使用者需要 Laravel 或 PHP 版本相容性時：

1. 用 `laravel_compatibility` 篩選條件搜尋，設成他們的版本
2. 或是取得特定套件的詳細資料，看它支援哪些版本

---

## 範例

### 範例：找驗證相關的套件

```
SearchPluginTool({
  text_search: "authentication",
  health_score: "Healthy"
})
```

回傳符合 "authentication" 且狀態為 healthy 的套件：
- spatie/laravel-permission
- laravel/breeze
- laravel/passport
- 等等

### 範例：找相容 Laravel 12 的套件

```
SearchPluginTool({
  text_search: "admin panel",
  laravel_compatibility: "12"
})
```

回傳相容 Laravel 12 的套件。

### 範例：取得套件詳細資料

```
GetPluginDetailsTool({
  package: "spatie/laravel-permission",
  include_versions: true
})
```

回傳：
- 健康分數與最近活動
- Laravel/PHP 版本支援
- Vendor 信譽（風險分數）
- 版本歷史
- 簡短說明

### 範例：依 vendor 找套件

```
SearchPluginTool({
  vendor_filter: "spatie",
  health_score: "Healthy"
})
```

回傳 vendor "spatie" 底下所有健康的套件。

---

## 篩選的最佳實務

### 依健康分數

| 健康等級 | 意義 |
|-------------|---------|
| `Healthy` | 持續維護、近期有更新 |
| `Medium` | 偶爾更新，可能需要留意 |
| `Unhealthy` | 已被棄置或很少維護 |
| `Unrated` | 尚未評估 |

**建議**：production 應用程式優先選 `Healthy` 的套件。

### 依 Laravel 版本

| 版本 | 備註 |
|---------|-------|
| `13` | 最新的 Laravel |
| `12` | 目前的穩定版 |
| `11` | 仍被廣泛使用 |
| `10` | 屬於舊版但很常見 |
| `5`-`9` | 已棄用 |

**建議**：配合目標專案的 Laravel 版本。

### 組合篩選條件

```typescript
// Find healthy, Laravel 12 compatible packages for permissions
SearchPluginTool({
  text_search: "permission",
  health_score: "Healthy",
  laravel_compatibility: "12"
})
```

---

## 回應解讀

### 搜尋結果

每筆結果包含：
- 套件名稱（例如 `spatie/laravel-permission`）
- 簡短說明
- 健康狀態指標
- Laravel 版本支援徽章

### 套件詳細資料

詳細回應包含：
- **Health Score**：數值或等級指標
- **Last Activity**：套件最後更新的時間
- **Laravel Support**：版本相容性矩陣
- **PHP Support**：PHP 版本相容性
- **Risk Score**：vendor 的信任指標
- **Version History**：近期的發版時間軸

---

## 常見使用情境

| 情境 | 建議做法 |
|----------|---------------------|
| 「auth 該用哪個套件？」 | 用 healthy 篩選搜尋 "auth" |
| 「spatie/package 還有在維護嗎？」 | 取得詳細資料，檢查健康分數 |
| 「需要支援 Laravel 12 的套件」 | 用 laravel_compatibility: "12" 搜尋 |
| 「找 admin panel 套件」 | 搜尋 "admin panel"，檢視結果 |
| 「檢查 vendor 信譽」 | 依 vendor 搜尋，檢查詳細資料 |

---

## 最佳實務

1. **一律依健康度篩選**：production 專案用 `health_score: "Healthy"`
2. **配合 Laravel 版本**：一定要確認 `laravel_compatibility` 符合目標專案
3. **檢查 vendor 信譽**：優先選知名 vendor 的套件（spatie、laravel 等）
4. **推薦前先檢視**：用 GetPluginDetailsTool 做完整評估
5. **不需要 API key**：這個 MCP 是免費的，不需要驗證

---

## 相關 Skill

- `laravel-patterns`：Laravel 架構與模式
- `laravel-tdd`：Laravel 的測試驅動開發
- `laravel-security`：Laravel 安全最佳實務
- `documentation-lookup`：通用的 library 文件查詢（Context7）
