---
name: color-palette
description: "從單一個品牌 hex 產生完整、符合無障礙的色彩系統。產出 11 階色階（50-950）、語意 token、深色模式變體、Tailwind v4 CSS 輸出和 WCAG 對比檢查。只要使用者提供品牌 hex 並要求色票、提到要建立設計系統、想從品牌色得到 Tailwind 主題色，或要檢查色彩無障礙 / 對比度，就使用。"
compatibility: claude-code-only
---

# Colour Palette Generator

從單一個品牌 hex 產生完整、符合無障礙的色彩系統。產出可以直接貼進專案的 Tailwind v4 CSS。

## 工作流程

### Step 1：取得品牌 Hex

詢問主要的品牌色。像 `#0D9488` 這樣單一個 hex 就夠了。

### Step 2：產生 11 階色階

把 hex 轉成 HSL，然後保持色相不變、調整明度來產生各階色。

#### Hex 轉 HSL

```javascript
function hexToHSL(hex) {
  hex = hex.replace(/^#/, '');
  const r = parseInt(hex.substring(0, 2), 16) / 255;
  const g = parseInt(hex.substring(2, 4), 16) / 255;
  const b = parseInt(hex.substring(4, 6), 16) / 255;

  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const diff = max - min;

  let l = (max + min) / 2;
  let s = 0;
  if (diff !== 0) {
    s = l > 0.5 ? diff / (2 - max - min) : diff / (max + min);
  }

  let h = 0;
  if (diff !== 0) {
    if (max === r) h = ((g - b) / diff + (g < b ? 6 : 0)) / 6;
    else if (max === g) h = ((b - r) / diff + 2) / 6;
    else h = ((r - g) / diff + 4) / 6;
  }

  return { h: Math.round(h * 360), s: Math.round(s * 100), l: Math.round(l * 100) };
}
```

#### 明度與飽和度數值

| 色階 | 明度 | 飽和度倍率 | 用途 |
|-------|-----------|-----------------|----------|
| 50 | 97% | 0.80 | 淡淡的背景 |
| 100 | 94% | 0.80 | Hover 狀態 |
| 200 | 87% | 0.85 | 邊框、分隔線 |
| 300 | 75% | 0.90 | 停用狀態 |
| 400 | 62% | 0.95 | Placeholder 文字 |
| 500 | 48% | 1.00 | **品牌色基準** |
| 600 | 40% | 1.00 | 主要動作（常常就是品牌色） |
| 700 | 33% | 1.00 | 主要動作的 hover |
| 800 | 27% | 1.00 | Active 狀態 |
| 900 | 20% | 1.00 | 淺色背景上的文字 |
| 950 | 10% | 1.00 | 最深的點綴色 |

較淺的色階要降低飽和度（50-200 降 15-20%，300-400 降 5-10%），避免粉彩色過於鮮豔。500-950 維持完整飽和度。

#### 完整色階產生器

```javascript
function generateShadeScale(brandHex) {
  const { h, s } = hexToHSL(brandHex);
  const shades = {
    50:  { l: 97, sMul: 0.8 },  100: { l: 94, sMul: 0.8 },
    200: { l: 87, sMul: 0.85 }, 300: { l: 75, sMul: 0.9 },
    400: { l: 62, sMul: 0.95 }, 500: { l: 48, sMul: 1.0 },
    600: { l: 40, sMul: 1.0 },  700: { l: 33, sMul: 1.0 },
    800: { l: 27, sMul: 1.0 },  900: { l: 20, sMul: 1.0 },
    950: { l: 10, sMul: 1.0 }
  };
  const result = {};
  for (const [shade, { l, sMul }] of Object.entries(shades)) {
    result[shade] = `hsl(${h}, ${Math.round(s * sMul)}%, ${l}%)`;
  }
  return result;
}
```

#### HSL 轉 Hex

```javascript
function hslToHex(h, s, l) {
  s = s / 100; l = l / 100;
  const c = (1 - Math.abs(2 * l - 1)) * s;
  const x = c * (1 - Math.abs((h / 60) % 2 - 1));
  const m = l - c / 2;
  let r = 0, g = 0, b = 0;
  if (h < 60) { r = c; g = x; }
  else if (h < 120) { r = x; g = c; }
  else if (h < 180) { g = c; b = x; }
  else if (h < 240) { g = x; b = c; }
  else if (h < 300) { r = x; b = c; }
  else { r = c; b = x; }
  r = Math.round((r + m) * 255);
  g = Math.round((g + m) * 255);
  b = Math.round((b + m) * 255);
  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`.toUpperCase();
}
```

#### 驗證

產生出來的色階看起來應該屬於同一個色系，而且漸變平順。淺色階（50-300）可以當背景用，深色階（700-950）可以當文字用。品牌色要能在 500-700 之間辨認出來。

---

### Step 3：對應語意 Token

每個背景 token **一定**要搭配一個前景 token。絕對不要使用沒有配對的背景，否則深色模式會壞掉。

#### 淺色模式 Token

| Token | 色階 | 用途 |
|-------|-------|----------|
| `background` | white | 頁面背景 |
| `foreground` | 950 | 內文文字 |
| `card` | white | 卡片背景 |
| `card-foreground` | 900 | 卡片文字 |
| `popover` | white | 下拉選單/tooltip 背景 |
| `popover-foreground` | 950 | 下拉選單文字 |
| `primary` | 600 | 主要按鈕、連結 |
| `primary-foreground` | white | 主要按鈕上的文字 |
| `secondary` | 100 | 次要按鈕 |
| `secondary-foreground` | 900 | 次要按鈕上的文字 |
| `muted` | 50 | 停用的背景、淡淡的區塊 |
| `muted-foreground` | 600 | 弱化的文字、圖說 |
| `accent` | 100 | Hover 狀態、淡淡的強調 |
| `accent-foreground` | 900 | 強調背景上的文字 |
| `destructive` | red-600 | 刪除按鈕、錯誤 |
| `destructive-foreground` | white | 破壞性按鈕上的文字 |
| `border` | 200 | 輸入框邊框、分隔線 |
| `input` | 200 | 輸入欄位邊框 |
| `ring` | 600 | Focus 外框 |

#### 深色模式 Token

| Token | 色階 | 用途 |
|-------|-------|----------|
| `background` | 950 | 頁面背景 |
| `foreground` | 50 | 內文文字 |
| `card` | 900 | 卡片背景 |
| `card-foreground` | 50 | 卡片文字 |
| `popover` | 900 | 下拉選單背景 |
| `popover-foreground` | 50 | 下拉選單文字 |
| `primary` | 500 | 主要按鈕（深色模式下更亮） |
| `primary-foreground` | white | 主要按鈕上的文字 |
| `secondary` | 800 | 次要按鈕 |
| `secondary-foreground` | 50 | 次要按鈕上的文字 |
| `muted` | 800 | 停用的背景 |
| `muted-foreground` | 400 | 弱化的文字 |
| `accent` | 800 | Hover 狀態 |
| `accent-foreground` | 50 | 強調背景上的文字 |
| `destructive` | red-500 | 刪除按鈕（更亮） |
| `destructive-foreground` | white | 破壞性按鈕上的文字 |
| `border` | 800 | 邊框 |
| `input` | 800 | 輸入框邊框 |
| `ring` | 500 | Focus 外框 |

#### 深色模式反轉模式

深色模式是把明度反轉，同時保留色相和飽和度。兩端互換（50 變 950，950 變 50），中間保留（500 維持在 500 附近）。

| 淺色色階 | 深色對應 | 角色 |
|-------------|-----------------|------|
| 50 | 950 | 背景 |
| 100 | 900 | 淡淡的背景 |
| 200 | 800 | 邊框 |
| 500 | 500（稍微亮一點） | 品牌色基準 |
| 600 | 400 | 主要動作 |
| 950 | 50 | 文字顏色 |

深色模式的關鍵原則：
- primary 用 500 色階（不是 600），在深色背景上更亮才看得清楚
- 文字用 50 色階（偏白）而不是純 `#FFFFFF`，眼睛比較舒服
- 邊框要比背景亮約 10-15%（例如 950 背景上用 800 邊框）
- 層級越高，顏色越亮（跟淺色模式的陰影相反）
- 換背景的時候，前景一定要跟著更新

---

### Step 4：檢查對比

#### WCAG 最低比值

| 內容類型 | AA | AAA |
|--------------|-----|-----|
| 一般文字（<18px 或 <14px 粗體） | 4.5:1 | 7:1 |
| 大字（>=18px 或 >=14px 粗體） | 3:1 | 4.5:1 |
| UI 元件（按鈕、邊框） | 3:1 | 未定義 |
| 圖形物件（圖示、圖表） | 3:1 | 未定義 |

大部分專案目標是 AA，高無障礙需求的（政府、醫療）目標是 AAA。

#### 亮度與對比公式

```javascript
function getLuminance(hex) {
  hex = hex.replace(/^#/, '');
  const r = parseInt(hex.substring(0, 2), 16) / 255;
  const g = parseInt(hex.substring(2, 4), 16) / 255;
  const b = parseInt(hex.substring(4, 6), 16) / 255;
  const rsRGB = r <= 0.03928 ? r / 12.92 : Math.pow((r + 0.055) / 1.055, 2.4);
  const gsRGB = g <= 0.03928 ? g / 12.92 : Math.pow((g + 0.055) / 1.055, 2.4);
  const bsRGB = b <= 0.03928 ? b / 12.92 : Math.pow((b + 0.055) / 1.055, 2.4);
  return 0.2126 * rsRGB + 0.7152 * gsRGB + 0.0722 * bsRGB;
}

function getContrastRatio(hex1, hex2) {
  const lum1 = getLuminance(hex1);
  const lum2 = getLuminance(hex2);
  const lighter = Math.max(lum1, lum2);
  const darker = Math.min(lum1, lum2);
  return (lighter + 0.05) / (darker + 0.05);
}
```

#### 快速檢查表：淺色模式

| 前景 | 背景 | 比值 | 通過？ | 用途 |
|------------|------------|-------|-------|----------|
| 950 | white | 18.5:1 | AAA | 內文文字 |
| 900 | white | 14.2:1 | AAA | 卡片文字 |
| 700 | white | 8.1:1 | AAA | 文字 |
| 600 | white | 5.7:1 | AA | 文字、按鈕 |
| 500 | white | 3.9:1 | 不通過 | 當文字太淺 |
| white | 600 | 5.7:1 | AA | 按鈕文字 |
| white | 700 | 8.1:1 | AAA | 按鈕文字 |
| 600 | 50 | 5.4:1 | AA | 弱化區塊的文字 |

#### 快速檢查表：深色模式

| 前景 | 背景 | 比值 | 通過？ | 用途 |
|------------|------------|-------|-------|----------|
| 50 | 950 | 18.5:1 | AAA | 內文文字 |
| 50 | 900 | 14.2:1 | AAA | 卡片文字 |
| 400 | 950 | 8.2:1 | AAA | 弱化的文字 |
| 400 | 900 | 6.3:1 | AA | 弱化的文字 |
| white | 600 | 5.7:1 | AA | 按鈕文字 |

**經驗法則**：文字的前景和背景，明度差要有 50% 以上。

#### 一定要驗證的配對

1. **內文文字**：background 上的 foreground（淺色：white 上用 950 = 18.5:1，深色：950 上用 50 = 18.5:1）
2. **主要按鈕**：primary 上的 primary-foreground（淺色：600 上用 white = 5.7:1，深色：500 上用 white = 3.9:1，在邊緣）
3. **弱化文字**：muted 上的 muted-foreground（淺色：50 上用 600 = 5.4:1，深色：800 上用 400 = 4.1:1，可能不通過）
4. **卡片文字**：card 上的 card-foreground（淺色：white 上用 900 = 14.2:1，深色：900 上用 50 = 14.2:1）

#### 修正常見的對比失敗

**primary-500 上的白字不通過（3.9:1）**：改用 primary-600（5.7:1），或在按鈕上用深色文字。

**深色模式的弱化文字不通過（800 上用 400 = 4.1:1）**：用 900 上的 300 = 6.8:1。

**連結不好辨認（white 上用 500 = 3.9:1）**：用 primary-700（8.1:1），或加上底線裝飾。

---

### Step 5：輸出 Tailwind v4 CSS

```css
@import "tailwindcss";

@theme {
  /* Shade scale */
  --color-primary-50: #F0FDFA;
  --color-primary-100: #CCFBF1;
  --color-primary-200: #99F6E4;
  --color-primary-300: #5EEAD4;
  --color-primary-400: #2DD4BF;
  --color-primary-500: #14B8A6;
  --color-primary-600: #0D9488;
  --color-primary-700: #0F766E;
  --color-primary-800: #115E59;
  --color-primary-900: #134E4A;
  --color-primary-950: #042F2E;

  /* Light mode semantic tokens */
  --color-background: #FFFFFF;
  --color-foreground: var(--color-primary-950);
  --color-card: #FFFFFF;
  --color-card-foreground: var(--color-primary-900);
  --color-popover: #FFFFFF;
  --color-popover-foreground: var(--color-primary-950);
  --color-primary: var(--color-primary-600);
  --color-primary-foreground: #FFFFFF;
  --color-secondary: var(--color-primary-100);
  --color-secondary-foreground: var(--color-primary-900);
  --color-muted: var(--color-primary-50);
  --color-muted-foreground: var(--color-primary-600);
  --color-accent: var(--color-primary-100);
  --color-accent-foreground: var(--color-primary-900);
  --color-destructive: #DC2626;
  --color-destructive-foreground: #FFFFFF;
  --color-border: var(--color-primary-200);
  --color-input: var(--color-primary-200);
  --color-ring: var(--color-primary-600);
  --radius: 0.5rem;
}

/* Dark mode overrides */
.dark {
  --color-background: var(--color-primary-950);
  --color-foreground: var(--color-primary-50);
  --color-card: var(--color-primary-900);
  --color-card-foreground: var(--color-primary-50);
  --color-popover: var(--color-primary-900);
  --color-popover-foreground: var(--color-primary-50);
  --color-primary: var(--color-primary-500);
  --color-primary-foreground: #FFFFFF;
  --color-secondary: var(--color-primary-800);
  --color-secondary-foreground: var(--color-primary-50);
  --color-muted: var(--color-primary-800);
  --color-muted-foreground: var(--color-primary-400);
  --color-accent: var(--color-primary-800);
  --color-accent-foreground: var(--color-primary-50);
  --color-destructive: #EF4444;
  --color-destructive-foreground: #FFFFFF;
  --color-border: var(--color-primary-800);
  --color-input: var(--color-primary-800);
  --color-ring: var(--color-primary-500);
}
```

複製 `assets/tailwind-colors.css` 當作起始範本。

---

## 元件使用範例

```tsx
// Primary button
<button className="bg-primary text-primary-foreground hover:bg-primary/90">Click me</button>

// Secondary button
<button className="bg-secondary text-secondary-foreground hover:bg-secondary/80">Cancel</button>

// Card
<div className="bg-card text-card-foreground border-border rounded-lg">
  <h2>Title</h2>
  <p className="text-muted-foreground">Description</p>
</div>

// Input
<input className="bg-background text-foreground border-input focus:ring-ring" />
```

---

## 常見調整

- **淺色階太鮮豔**：把飽和度降低 10-20%
- **primary 上的對比不佳**：文字用 700 以上的色階
- **深色模式太暗**：背景用 900 色階，不要用 950
- **品牌色太淺/太深**：調整到 500-600 的範圍
- **深色模式看起來褪色**：primary 用 500 色階（比淺色模式的 600 更亮）
- **深色模式下純白文字太刺眼**：改用 50 色階（偏白）
- **深色模式的弱化文字對比不通過**：用更極端的色階（900 上用 300，而不是 800 上用 400）

### 品牌調性調整

- **保守的品牌**（金融、法律）：按鈕用 primary-700，淺色階降低飽和度
- **鮮明的品牌**（創意、科技）：用 primary-500-600，維持完整飽和度
- **極簡的品牌**（設計、建築）：少用 primary，強調弱化的色調，邊框要細（primary-100）

---

## 驗證檢查清單

- [ ] 內文文字：>=4.5:1（一般）或 >=3:1（大字）
- [ ] 主要按鈕文字：>=4.5:1
- [ ] 次要按鈕文字：>=4.5:1
- [ ] 弱化文字：>=4.5:1
- [ ] 連結：>=4.5:1（或加底線）
- [ ] UI 元素（邊框）：>=3:1
- [ ] Focus 指示器：>=3:1
- [ ] 錯誤文字：>=4.5:1
- [ ] 深色模式：以上所有檢查都通過
- [ ] 每個背景都有配對的前景
- [ ] 品牌色在兩種模式下都能辨認
- [ ] 邊框看得到但不刺眼
- [ ] 卡片/區塊有清楚的界線

**上線之前，兩種模式都要測。**

---

## 選用參考資料

- **線上對比檢查工具**：WebAIM (webaim.org/resources/contrastchecker)、Coolors (coolors.co/contrast-checker)、Accessible Colors (accessible-colors.com)
- **CI/CD 對比測試**：在測試套件裡用 `getContrastRatio()`，替所有 token 配對斷言最低比值
- **透明/漸層的邊界情況**：有透明度的顏色，要對照最終渲染出來的顏色計算。漸層則要檢查兩個端點。
- **OLED 深色模式**：用 `@media (prefers-contrast: high)` 搭配 `#000000` 背景，在 AMOLED 螢幕上省電
- **多色色票**：替每個品牌色分別產生色階，對應到不同的語意角色（primary、accent）
- **色票視覺化工具**：coolors.co、paletton.com、Figma 色票
- `assets/tailwind-colors.css`：完整的 CSS 輸出範本
