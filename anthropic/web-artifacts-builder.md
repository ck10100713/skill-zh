---
layout: "default"
skill: "web-artifacts-builder"
author: "Anthropic"
category: "設計與前端"
summary: "用 React、Tailwind、shadcn/ui 做複雜 artifact，再打包成單一 HTML"
source: "https://github.com/anthropics/skills/blob/main/skills/web-artifacts-builder/SKILL.md"
license: "Apache-2.0"
---

<div class="pair" markdown="1">
<section markdown="1">

## 中文翻譯

{% raw %}
~~~~~markdown
---
name: web-artifacts-builder
description: 一套用現代前端技術（React、Tailwind CSS、shadcn/ui）建立複雜、多元件 claude.ai HTML artifact 的工具。適用於需要狀態管理、路由或 shadcn/ui 元件的複雜 artifact，不適合簡單的單檔 HTML/JSX artifact。
license: Complete terms in LICENSE.txt
---

# Web Artifacts Builder

要建立功能強大的前端 claude.ai artifact，照這些步驟做：
1. 用 `scripts/init-artifact.sh` 初始化前端 repo
2. 編輯產生出來的程式碼來開發你的 artifact
3. 用 `scripts/bundle-artifact.sh` 把所有程式碼打包成單一 HTML 檔
4. 把 artifact 顯示給使用者
5. （選用）測試 artifact

**Stack**: React 18 + TypeScript + Vite + Parcel (bundling) + Tailwind CSS + shadcn/ui

## Design & Style Guidelines

非常重要：為了避免常說的「AI slop」，不要用過多的置中版面、紫色漸層、一致的圓角，也不要用 Inter 字體。

## Quick Start

### Step 1: Initialize Project

執行初始化腳本，建立新的 React 專案：
```bash
bash scripts/init-artifact.sh <project-name>
cd <project-name>
```

這會建出一個設定完整的專案，包含：
- ✅ React + TypeScript（透過 Vite）
- ✅ Tailwind CSS 3.4.1，附 shadcn/ui 主題系統
- ✅ 已設定好路徑別名（`@/`）
- ✅ 預先安裝 40 個以上的 shadcn/ui 元件
- ✅ 包含所有 Radix UI 相依套件
- ✅ 已設定好用 Parcel 打包（透過 .parcelrc）
- ✅ 相容 Node 18+（自動偵測並鎖定 Vite 版本）

### Step 2: Develop Your Artifact

要建立 artifact，就編輯產生出來的檔案。開發指引請看下面的 **Common Development Tasks**。

### Step 3: Bundle to Single HTML File

要把 React app 打包成單一 HTML artifact：
```bash
bash scripts/bundle-artifact.sh
```

這會產生 `bundle.html`，是一個自給自足的 artifact，所有 JavaScript、CSS 和相依套件都已內嵌。這個檔案可以直接當作 artifact 在 Claude 對話中分享。

**Requirements**: 你的專案根目錄必須有 `index.html`。

**What the script does**:
- 安裝打包用的相依套件（parcel、@parcel/config-default、parcel-resolver-tspaths、html-inline）
- 建立支援路徑別名的 `.parcelrc` 設定
- 用 Parcel 建置（不產生 source map）
- 用 html-inline 把所有資源內嵌成單一 HTML

### Step 4: Share Artifact with User

最後，在對話中把打包好的 HTML 檔分享給使用者，讓他們能以 artifact 的形式檢視。

### Step 5: Testing/Visualizing the Artifact (Optional)

注意：這一步完全是選用的。只有必要或使用者要求時才做。

要測試/視覺化 artifact，用手邊可用的工具（包括其他 Skill，或內建工具如 Playwright、Puppeteer）。一般來說，不要一開始就測試 artifact，因為這會拉長從提出需求到看到成品之間的等待。等先把 artifact 呈現出來，之後有人要求或出問題再測。

## Reference

- **shadcn/ui components**: https://ui.shadcn.com/docs/components
~~~~~
{% endraw %}

</section>
<section markdown="1">

## 英文原文

{% raw %}
~~~~~markdown
---
name: web-artifacts-builder
description: Suite of tools for creating elaborate, multi-component claude.ai HTML artifacts using modern frontend web technologies (React, Tailwind CSS, shadcn/ui). Use for complex artifacts requiring state management, routing, or shadcn/ui components - not for simple single-file HTML/JSX artifacts.
license: Complete terms in LICENSE.txt
---

# Web Artifacts Builder

To build powerful frontend claude.ai artifacts, follow these steps:
1. Initialize the frontend repo using `scripts/init-artifact.sh`
2. Develop your artifact by editing the generated code
3. Bundle all code into a single HTML file using `scripts/bundle-artifact.sh`
4. Display artifact to user
5. (Optional) Test the artifact

**Stack**: React 18 + TypeScript + Vite + Parcel (bundling) + Tailwind CSS + shadcn/ui

## Design & Style Guidelines

VERY IMPORTANT: To avoid what is often referred to as "AI slop", avoid using excessive centered layouts, purple gradients, uniform rounded corners, and Inter font.

## Quick Start

### Step 1: Initialize Project

Run the initialization script to create a new React project:
```bash
bash scripts/init-artifact.sh <project-name>
cd <project-name>
```

This creates a fully configured project with:
- ✅ React + TypeScript (via Vite)
- ✅ Tailwind CSS 3.4.1 with shadcn/ui theming system
- ✅ Path aliases (`@/`) configured
- ✅ 40+ shadcn/ui components pre-installed
- ✅ All Radix UI dependencies included
- ✅ Parcel configured for bundling (via .parcelrc)
- ✅ Node 18+ compatibility (auto-detects and pins Vite version)

### Step 2: Develop Your Artifact

To build the artifact, edit the generated files. See **Common Development Tasks** below for guidance.

### Step 3: Bundle to Single HTML File

To bundle the React app into a single HTML artifact:
```bash
bash scripts/bundle-artifact.sh
```

This creates `bundle.html` - a self-contained artifact with all JavaScript, CSS, and dependencies inlined. This file can be directly shared in Claude conversations as an artifact.

**Requirements**: Your project must have an `index.html` in the root directory.

**What the script does**:
- Installs bundling dependencies (parcel, @parcel/config-default, parcel-resolver-tspaths, html-inline)
- Creates `.parcelrc` config with path alias support
- Builds with Parcel (no source maps)
- Inlines all assets into single HTML using html-inline

### Step 4: Share Artifact with User

Finally, share the bundled HTML file in conversation with the user so they can view it as an artifact.

### Step 5: Testing/Visualizing the Artifact (Optional)

Note: This is a completely optional step. Only perform if necessary or requested.

To test/visualize the artifact, use available tools (including other Skills or built-in tools like Playwright or Puppeteer). In general, avoid testing the artifact upfront as it adds latency between the request and when the finished artifact can be seen. Test later, after presenting the artifact, if requested or if issues arise.

## Reference

- **shadcn/ui components**: https://ui.shadcn.com/docs/components
~~~~~
{% endraw %}

</section>
</div>
