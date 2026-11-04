---
name: mobile-android-design
description: 精通 Material Design 3 與 Jetpack Compose 模式，用來建構原生 Android app。在設計 Android 介面、實作 Compose UI 或遵循 Google 的 Material Design 指南時使用。
---

# Android Mobile Design

精通 Material Design 3（Material You）與 Jetpack Compose，建構能與 Android 生態系無縫整合的現代、可自適應的 Android 應用程式。

## When to Use This Skill

- 依 Material Design 3 設計 Android app 介面
- 建構 Jetpack Compose UI 與版面
- 實作 Android 導覽模式（Navigation Compose）
- 為手機、平板與摺疊式裝置建立自適應版面
- 使用帶有動態色彩的 Material 3 主題
- 建構無障礙的 Android 介面
- 實作 Android 專屬的手勢與互動
- 為不同螢幕配置做設計

## Detailed section: Core Concepts

這段原本是這份 SKILL.md 裡一段 9201 bytes 的內容，為了符合 Codex 對 skill 本文 8 KB 的上限，已搬到 `references/details.md`。

## Quick Start Component

```kotlin
@Composable
fun ItemListCard(
    item: Item,
    onItemClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        onClick = onItemClick,
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier
                .padding(16.dp)
                .fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape)
                    .background(MaterialTheme.colorScheme.primaryContainer),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Default.Star,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.onPrimaryContainer
                )
            }

            Spacer(modifier = Modifier.width(16.dp))

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = item.title,
                    style = MaterialTheme.typography.titleMedium
                )
                Text(
                    text = item.subtitle,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            Icon(
                imageVector = Icons.Default.ChevronRight,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}
```

## Best Practices

1. **使用 Material Theme**：透過 `MaterialTheme.colorScheme` 取得顏色，自動支援深色模式
2. **支援 Dynamic Color**：在 Android 12+ 啟用動態色彩，做到個人化
3. **自適應版面**：用 `WindowSizeClass` 做響應式設計
4. **Content Descriptions**：為所有可互動元素加上 `contentDescription`
5. **觸控目標**：為了無障礙，觸控目標至少 48dp
6. **State Hoisting**：把 state 往上提，讓元件可重用且好測試
7. **正確使用 Remember**：適當使用 `remember` 和 `rememberSaveable`
8. **Preview 註解**：用不同設定加上 `@Preview`

## Common Issues

- **Recomposition 問題**：避免傳入不穩定的 lambda，用 `remember`
- **State 遺失**：設定變更時用 `rememberSaveable`
- **效能**：長清單用 `LazyColumn`，不要用 `Column`
- **Theme 外洩**：確保 `MaterialTheme` 包住所有 composable
- **導覽崩潰**：正確處理返回鍵與 deep link
- **記憶體洩漏**：在 `DisposableEffect` 裡取消 coroutine
