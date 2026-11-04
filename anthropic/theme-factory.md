---
layout: "default"
skill: "theme-factory"
author: "Anthropic"
category: "設計與前端"
summary: "從 10 套預設主題挑一套，或即時生成新主題來套用到簡報和文件"
source: "https://github.com/anthropics/skills/blob/main/skills/theme-factory/SKILL.md"
license: "Apache-2.0"
---

<div class="pair" markdown="1">
<section markdown="1">

## 中文翻譯

{% raw %}
~~~~~markdown
---
name: theme-factory
description: 用主題替產出物設定樣式的工具包。這些產出物可以是簡報、文件、報告、HTML 登陸頁等。內建 10 套預設主題（含配色和字體），可以套用到任何已經做好的產出物，也可以即時生成新主題。
license: Complete terms in LICENSE.txt
---


# Theme Factory Skill

這個 skill 提供一組精心挑選的專業字體與配色主題，每套都有仔細選過的色票和字體搭配。選定主題之後，就能套用到任何產出物上。

## Purpose

要替簡報投影片套用一致又專業的樣式，就用這個 skill。每套主題包含：
- 一組協調的色票，附色碼（hex code）
- 搭配好的標題和內文字體組合
- 獨特的視覺識別，適合不同情境和受眾

## Usage Instructions

要替投影片或其他產出物套用樣式：

1. **展示主題總覽**：把 `theme-showcase.pdf` 檔案顯示給使用者，讓他們直接看到所有可用主題。不要對它做任何修改，只要讓使用者看就好。
2. **詢問選擇**：問使用者要把哪一套主題套用到這份簡報
3. **等待選定**：取得使用者對所選主題的明確確認
4. **套用主題**：主題選定後，把所選主題的顏色和字體套用到簡報/產出物上

## Themes Available

以下 10 套主題都可以用，都展示在 `theme-showcase.pdf` 裡：

1. **Ocean Depths** - 專業又沉靜的海洋主題
2. **Sunset Boulevard** - 溫暖又鮮豔的日落色調
3. **Forest Canopy** - 自然沉穩的大地色系
4. **Modern Minimalist** - 乾淨現代的灰階
5. **Golden Hour** - 濃郁溫暖的秋天色盤
6. **Arctic Frost** - 冷冽清爽的冬季風格主題
7. **Desert Rose** - 柔和又精緻的灰調色系
8. **Tech Innovation** - 大膽現代的科技感
9. **Botanical Garden** - 清新自然的花園色彩
10. **Midnight Galaxy** - 戲劇感十足的宇宙深色調

## Theme Details

每套主題都定義在 `themes/` 目錄裡，有完整規格，包含：
- 協調的色票，附色碼（hex code）
- 搭配好的標題和內文字體組合
- 獨特的視覺識別，適合不同情境和受眾

## Application Process

選好主題之後：
1. 從 `themes/` 目錄讀取對應的主題檔
2. 把指定的顏色和字體一致地套用到整份簡報
3. 確保對比度和可讀性足夠
4. 在所有投影片上維持該主題的視覺識別

## Create your Own Theme
如果現有主題都不適合某個產出物，就建立自訂主題。根據使用者提供的輸入，生成一套跟上面類似的新主題。替它取一個類似的名字，描述這組字體/顏色搭配代表什麼。用使用者給的任何簡單描述來挑選合適的顏色和字體。生成主題之後，先展示出來讓使用者檢視確認，再依上面的方式套用。
~~~~~
{% endraw %}

</section>
<section markdown="1">

## 英文原文

{% raw %}
~~~~~markdown
---
name: theme-factory
description: Toolkit for styling artifacts with a theme. These artifacts can be slides, docs, reportings, HTML landing pages, etc. There are 10 pre-set themes with colors/fonts that you can apply to any artifact that has been creating, or can generate a new theme on-the-fly.
license: Complete terms in LICENSE.txt
---


# Theme Factory Skill

This skill provides a curated collection of professional font and color themes themes, each with carefully selected color palettes and font pairings. Once a theme is chosen, it can be applied to any artifact.

## Purpose

To apply consistent, professional styling to presentation slide decks, use this skill. Each theme includes:
- A cohesive color palette with hex codes
- Complementary font pairings for headers and body text
- A distinct visual identity suitable for different contexts and audiences

## Usage Instructions

To apply styling to a slide deck or other artifact:

1. **Show the theme showcase**: Display the `theme-showcase.pdf` file to allow users to see all available themes visually. Do not make any modifications to it; simply show the file for viewing.
2. **Ask for their choice**: Ask which theme to apply to the deck
3. **Wait for selection**: Get explicit confirmation about the chosen theme
4. **Apply the theme**: Once a theme has been chosen, apply the selected theme's colors and fonts to the deck/artifact

## Themes Available

The following 10 themes are available, each showcased in `theme-showcase.pdf`:

1. **Ocean Depths** - Professional and calming maritime theme
2. **Sunset Boulevard** - Warm and vibrant sunset colors
3. **Forest Canopy** - Natural and grounded earth tones
4. **Modern Minimalist** - Clean and contemporary grayscale
5. **Golden Hour** - Rich and warm autumnal palette
6. **Arctic Frost** - Cool and crisp winter-inspired theme
7. **Desert Rose** - Soft and sophisticated dusty tones
8. **Tech Innovation** - Bold and modern tech aesthetic
9. **Botanical Garden** - Fresh and organic garden colors
10. **Midnight Galaxy** - Dramatic and cosmic deep tones

## Theme Details

Each theme is defined in the `themes/` directory with complete specifications including:
- Cohesive color palette with hex codes
- Complementary font pairings for headers and body text
- Distinct visual identity suitable for different contexts and audiences

## Application Process

After a preferred theme is selected:
1. Read the corresponding theme file from the `themes/` directory
2. Apply the specified colors and fonts consistently throughout the deck
3. Ensure proper contrast and readability
4. Maintain the theme's visual identity across all slides

## Create your Own Theme
To handle cases where none of the existing themes work for an artifact, create a custom theme. Based on provided inputs, generate a new theme similar to the ones above. Give the theme a similar name describing what the font/color combinations represent. Use any basic description provided to choose appropriate colors/fonts. After generating the theme, show it for review and verification. Following that, apply the theme as described above.
~~~~~
{% endraw %}

</section>
</div>
