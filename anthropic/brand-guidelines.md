---
layout: "default"
skill: "brand-guidelines"
author: "Anthropic"
category: "設計與前端"
summary: "把 Anthropic 官方品牌色和字體套到各種產出物上"
source: "https://github.com/anthropics/skills/blob/main/skills/brand-guidelines/SKILL.md"
license: "Apache-2.0"
---

<div class="pair" markdown="1">
<section markdown="1">

## 中文翻譯

{% raw %}
~~~~~markdown
---
name: brand-guidelines
description: 把 Anthropic 官方的品牌色和字體套用到任何適合帶有 Anthropic 視覺風格的產出物上。當品牌色、風格指南、視覺格式或公司設計規範適用時使用。
license: Complete terms in LICENSE.txt
---

# Anthropic Brand Styling

## Overview

要取用 Anthropic 官方的品牌識別和風格資源，就用這個 skill。

**Keywords**: branding, corporate identity, visual identity, post-processing, styling, brand colors, typography, Anthropic brand, visual formatting, visual design

## Brand Guidelines

### Colors

**Main Colors:**

- Dark: `#141413` - 主要文字和深色背景
- Light: `#faf9f5` - 淺色背景，以及深色底上的文字
- Mid Gray: `#b0aea5` - 次要元素
- Light Gray: `#e8e6dc` - 不顯眼的背景

**Accent Colors:**

- Orange: `#d97757` - 主要強調色
- Blue: `#6a9bcc` - 次要強調色
- Green: `#788c5d` - 第三強調色

### Typography

- **Headings**: Poppins（備用字體 Arial）
- **Body Text**: Lora（備用字體 Georgia）
- **Note**: 字體最好事先裝在你的環境裡，效果最好

## Features

### Smart Font Application

- 標題（24pt 以上）套用 Poppins 字體
- 內文套用 Lora 字體
- 自訂字體不可用時，自動退回 Arial/Georgia
- 在所有系統上都保持可讀性

### Text Styling

- 標題（24pt 以上）：Poppins 字體
- 內文：Lora 字體
- 依背景自動挑選文字顏色
- 保留文字的層級和格式

### Shape and Accent Colors

- 非文字的形狀使用強調色
- 依序輪流使用橘、藍、綠三種強調色
- 維持視覺趣味，同時不脫離品牌

## Technical Details

### Font Management

- 有的話就使用系統已安裝的 Poppins 和 Lora 字體
- 自動退回 Arial（標題）和 Georgia（內文）
- 不需要安裝字體，用現有的系統字體就能運作
- 要達到最佳效果，請事先在環境裡安裝 Poppins 和 Lora 字體

### Color Application

- 使用 RGB 色值，確保精準符合品牌色
- 透過 python-pptx 的 RGBColor 類別套用
- 在不同系統之間維持色彩一致
~~~~~
{% endraw %}

</section>
<section markdown="1">

## 英文原文

{% raw %}
~~~~~markdown
---
name: brand-guidelines
description: Applies Anthropic's official brand colors and typography to any sort of artifact that may benefit from having Anthropic's look-and-feel. Use it when brand colors or style guidelines, visual formatting, or company design standards apply.
license: Complete terms in LICENSE.txt
---

# Anthropic Brand Styling

## Overview

To access Anthropic's official brand identity and style resources, use this skill.

**Keywords**: branding, corporate identity, visual identity, post-processing, styling, brand colors, typography, Anthropic brand, visual formatting, visual design

## Brand Guidelines

### Colors

**Main Colors:**

- Dark: `#141413` - Primary text and dark backgrounds
- Light: `#faf9f5` - Light backgrounds and text on dark
- Mid Gray: `#b0aea5` - Secondary elements
- Light Gray: `#e8e6dc` - Subtle backgrounds

**Accent Colors:**

- Orange: `#d97757` - Primary accent
- Blue: `#6a9bcc` - Secondary accent
- Green: `#788c5d` - Tertiary accent

### Typography

- **Headings**: Poppins (with Arial fallback)
- **Body Text**: Lora (with Georgia fallback)
- **Note**: Fonts should be pre-installed in your environment for best results

## Features

### Smart Font Application

- Applies Poppins font to headings (24pt and larger)
- Applies Lora font to body text
- Automatically falls back to Arial/Georgia if custom fonts unavailable
- Preserves readability across all systems

### Text Styling

- Headings (24pt+): Poppins font
- Body text: Lora font
- Smart color selection based on background
- Preserves text hierarchy and formatting

### Shape and Accent Colors

- Non-text shapes use accent colors
- Cycles through orange, blue, and green accents
- Maintains visual interest while staying on-brand

## Technical Details

### Font Management

- Uses system-installed Poppins and Lora fonts when available
- Provides automatic fallback to Arial (headings) and Georgia (body)
- No font installation required - works with existing system fonts
- For best results, pre-install Poppins and Lora fonts in your environment

### Color Application

- Uses RGB color values for precise brand matching
- Applied via python-pptx's RGBColor class
- Maintains color fidelity across different systems
~~~~~
{% endraw %}

</section>
</div>
