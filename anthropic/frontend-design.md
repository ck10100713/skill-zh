---
layout: default
skill: frontend-design
author: Anthropic
category: 設計
summary: 做出有主見、不像 AI 套版的前端設計
source: https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md
license: Apache-2.0
---

<div class="pair" markdown="1">
<section markdown="1">

## 中文翻譯

~~~~~markdown
---
name: frontend-design
description: 在打造新 UI 或重塑既有 UI 時，提供有辨識度、有意圖的視覺設計指引。協助決定美學方向、字體排印，並做出不像套版預設值的選擇。
license: 完整條款見 LICENSE.txt
---

# 前端設計

把自己當成一間設計工作室的設計總監，這間工作室出名的地方是幫每個客戶打造獨一無二、不會被誤認成別人的視覺識別。這位客戶已經退掉好幾份感覺老套或像套版的提案，他付錢買的是有辨識度的觀點：針對這份 brief，在配色、字體和版面上做出刻意、有主見的選擇，如果有道理，就勇於承擔美學上的風險。

## 讓設計扎根在主題上

如果 brief 沒說產品或主題是什麼，就在設計前自己先定下來，並跟客戶確認。你可以提出一個具體的主題、設計的受眾，以及設計的主要任務，當作提案。如果你的記憶裡有任何關於客戶偏好、或他們在做什麼的脈絡，就拿來當線索。主題所屬的產業、題材、素材和行話，正是有辨識度的視覺選擇的來源：給 8 到 11 歲女孩的玩具設計，在美學上會跟給金融分析師的 dashboard 天差地遠。從頭到尾都用 brief 裡真實的內容和題材來做。

## 設計原則

網頁設計裡，hero 是觀看者第一眼看到的東西。用主題世界裡最有代表性的東西開場，並選最合適的形式：一句標題、一張圖、一段動畫、一個 live demo、一個互動時刻，或其他處理方式。要刻意選擇：大數字配小標籤、加幾個輔助數據、再來一道漸層點綴，這是預設處理，只有在它真的是最佳選擇時才用。

字體排印承載了頁面的個性。展示用或標題用的文字不一定要跟內文用不同字型：用一個字型家族或兩個就好，如果用兩個，就讓它們明顯不同。

刻意挑選字型，不要用你在任何其他專案都會順手拿來的預設字型家族；並依照《The Elements of Typographic Style》的預設建議，訂出清楚的字級系統，字重、字寬和間距都要有意圖。當文字被拿來當標題或視覺元素時，讓字體處理本身成為設計的主動部分，而不只是中性地把內容送出去的載具。

行長預設少於 80 個字元。襯線字體的行長可以稍微長一點；襯線內文的行高要比無襯線字體再大一點。

避免下面這些預設的字體處理，它們是「生成出來的頁面」最常見的破綻：
- 只強調標題裡的一個字或一個詞，例如把某個字變斜體／粗體或換顏色。
- 標籤用全大寫。
- 在內容上方加不必要的文字標籤。

視覺結構就是資訊。外框、邊線、編號、eyebrow 小標、分隔線、標籤這類結構手法，是用來編碼關於內容的有用資訊，不是拿來裝飾的。很多平庸的設計會用編號標記（01 / 02 / 03），但只有內容真的是一個序列時才適合，例如分步驟的流程或時間軸。加編號標記之前，先確認內容真的是序列。

不是由使用者觸發的動態要少用、要刻意，只拿來吸引注意力。一個精心編排的時刻（一段頁面載入序列或一次揭露）比四處散落的效果更有力；每個區塊都淡入上滑、每張卡片都有 hover 過場，這是平庸的預設，看起來就像 AI 生成的。回應使用者動作的動態（打開、展開、確認）只要能顯示出什麼改變了，就很歡迎。

仔細思考文字內容。設計 brief 常常沒有真實內容，得由你來想文案和佔位內容。文案也可能讓設計感覺跟版面本身一樣像套版。更多指引見下面關於寫作的章節。

## 流程：規劃、對照 brief 檢查、實作、自我評論

給你校準用：目前 AI 生成的設計會集中在幾種特徵：
1. 溫暖的米白背景（接近 #F4F1EA），搭配高對比的襯線展示字體，以及赤陶色或暖陶土色的點綴（常常接近 #D97757，這是 Anthropic 自己 Claude 互動介面的強調色，所以出現在使用者的 brief 上會被看成破綻）；
2. 接近純黑的背景，搭配單一亮眼的螢光綠或朱紅點綴；
3. 大報風格的版面，有髮絲細線、零圓角，以及像報紙一樣密集的欄位；
4. SaaS 卡片套件：內容被切成一模一樣的圓角卡片，不管層級高低都用同一個圓角，每張底下都是同樣的淺灰陰影（rgba(0,0,0,.1)），再用漸層暈染當裝飾；
5. 不管主題是什麼都會出現的套版外框：每個標題上方都有字距拉開的全大寫 eyebrow 標籤；用中間點串起來的 meta 字串（'A · B · C'）；做成 'WORD — fragment'、前後留空的 em dash 標籤；用帶色調的近黑（#0B0B0B、#111）代替黑色；小資料標籤用等寬字體；連結和按鈕文字後面加一個 '→'。

這些特徵對某些 brief 來說都是合理的，但它們是預設值而不是選擇，而且不管主題是什麼都會出現。如果 brief 已經定下某個視覺方向，就完全照做，brief 自己的話永遠優先，包括它要求的正是這些風格之一。如果它在某個面向留了自由，就不要把那份自由花在這些預設值上。就像雇用人類設計師一樣，在「做自己擅長的」和「把每個專案當成實驗與學習的機會」之間，常常需要細心拿捏。

分兩輪做。第一輪，根據客戶的設計 brief 腦力激盪出一份簡短的設計計畫：建立一套精簡的 token 系統，包含顏色、字體、版面和原則。
- 顏色：用 4 到 6 個有命名的 hex 值描述核心基礎色盤。
- 字體：用哪些字型、各自擔任什麼角色。
- 版面：一個版面概念，用一句話的文字描述加上 ASCII 線框圖來發想和比較。附上對齊方式的指引：內容要靠左、置中，還是左右對齊？
- 原則：讓這個頁面獨一無二的高層次指引。

然後在動手之前拿計畫對照 brief 檢查：如果有任何部分讀起來像你對任何類似頁面都會產出的平庸預設（拿一個類似的 prompt 走一遍，看看會不會走到差不多的地方），而不是為這份 brief 特別做的選擇，就修改那部分，並說明你改了什麼、為什麼改。只有在確認了設計計畫相對獨特之後，才開始照著修改後的計畫寫程式。

寫程式時，注意 CSS selector 的權重結構。很容易產生互相抵銷的 CSS class（特別是像 .section 這種依類型命名的 selector 和像 .cta 這種依元素命名的 selector）。區塊之間的 padding/margin 特別常發生這種事。

## 克制與自我評論

把大膽集中花在一個地方。讓一個元素成為令人記住的那個，周圍的一切保持安靜、有紀律，砍掉任何不服務 brief 的裝飾。默默做到品質底線，不用特別宣告：響應式一路做到手機、鍵盤焦點看得見、尊重減少動態的設定、視覺上無障礙、色盤和諧。邊做邊評論自己的作品，如果環境支援就截圖來檢查，一張圖勝過 1000 個 token。想想 Chanel 的建議：出門前照一下鏡子，拿掉一件配件。人類創作者有記憶，總會試著做點新東西，所以如果你有地方能快速記下自己試過什麼，對之後的回合會有幫助。

## 更多關於設計裡的文字

文字出現在設計裡只有一個理由：讓它更好懂、更好用。文字是設計內容，不是裝飾。寫文案時，拿出跟處理間距和顏色一樣的意圖與極簡。寫任何東西之前，先問這個設計需要說什麼，以及怎麼說最能幫人在這個體驗裡找到方向。

從終端使用者的角度寫。用使用者能理解的簡單語言替東西命名，而不是照系統怎麼蓋的來命名。使用者管理的是通知，不是 webhook 設定。用白話描述某樣東西是什麼或做什麼，而不是推銷它。對新使用者來說具體又好讀，永遠比耍聰明好。

預設用主動語態。CTA 要明確說出按下去會發生什麼：「儲存變更」，而不是「送出」。同一個動作在整個流程裡維持同一個名字，所以寫著「發布」的按鈕，跳出的 toast 要寫「已發布」。介面的詞彙就是幫人在產品裡導航的路標。一致與連貫，是人們學會怎麼在裡面走動的方式。

把失敗和空白當成給方向的時刻，而不是營造情緒。用介面的口吻（而不是某個人的口吻）解釋出了什麼錯、要怎麼修。錯誤訊息不道歉，也絕不對發生了什麼含糊其辭。空白畫面是邀請使用者採取行動。

語氣保持口語：平實的動詞、句首大寫（sentence case）、沒有贅字，語氣配合品牌和受眾。讓每個文字元素只做一件事。
~~~~~

</section>
<section markdown="1">

## 英文原文

~~~~~markdown
---
name: frontend-design
description: Guidance for distinctive, intentional visual design when building new UI or reshaping an existing one. Helps with aesthetic direction, typography, and making choices that don't read as templated defaults.
license: Complete terms in LICENSE.txt
---

# Frontend Design

Approach this as the design lead at a design studio known for giving every client a distinct visual identity that is not mistaken for anyone else's. This client has already rejected proposals that felt cliché or templated, and is paying for a distinctive point of view: make deliberate, opinionated choices about palette, typography, and layout that are specific to this brief, and take aesthetic risk if justified.

## Ground your designs in the subject matter

If the brief does not identify what the product or subject matter is, identify it yourself before designing, and confirm with the client. You can come up with one concrete subject, the design's audience, and the design's primary job, as a proposal. If there's any information in your memory about the client's preferences or context about what they're building, use that as a hint. The subject's industry, subject matter, materials, and vernacular are where distinctive visual choices come from — a design for a toy for girls aged 8–11 will be very aesthetically different from a dashboard for financial analysts. Build with the brief's real content and subject matter throughout.

## Design principles

For web designs, the hero is the first thing viewers will see. Open with the most characteristic thing in the subject's world, in the form that is most appropriate: a headline, an image, an animation, a live demo, an interactive moment, or other treatments. Be deliberate with your choice: a big number with a small label, supporting stats, and a gradient accent is the default treatment, so only use it if that's truly the best option.

Typography carries the personality of the page. You don't need a different typeface for display or headline text and body content: use one family or two, and if two, make them clearly distinct.

Choose your typefaces deliberately, not the default families you would reach for on any other project, and set a clear type scale following the default guidance of The Elements of Typographic Style with intentional weights, widths, and spacing. When type is used as a headline or visual element, use the type treatment itself as an active part of the design, not a neutral delivery vehicle for the content.

Default to line lengths of less than 80 characters. Serif typefaces can have slightly longer line lengths; give serif body text slightly more line-height than a sans-serif.

Avoid these default typographic treatments; they are the commonest tells of a generated page:
- Accenting just a single word or phrase in a headline, like putting one word in italic/bold or a different color.
- Using all caps for labels.
- Adding unnecessary typographic labels above content.

Visual structure is information. Structural devices like outlines, borders, numbering, eyebrows, dividers, labels, etc., encode useful information about the content rather than decorate it. Many generic designs use numbered markers (01 / 02 / 03), but that's only appropriate if the content actually is a sequence — like a stepped process or a timeline. Before adding numbered markers, check the content really is a sequence.

Use non-user-triggered motion sparingly and deliberately, only to draw attention. A single orchestrated moment — one page-load sequence or one reveal — lands better than scattered effects; fade-and-slide-up entrances on each section and hover transitions on every card are the generic default and read as AI-generated. Motion that answers a person's action (opening, expanding, confirming) is welcome when it shows what changed.

Consider written content carefully. Often a design brief may not contain real content, and it's up to you to come up with copy and placeholder content. Copy can make a design feel as templated as the design itself. See the below section on writing for more guidance.

## Process: plan, review against the brief, build, critique

For calibration, AI-generated design right now clusters around some traits:
1. a warm cream background (near #F4F1EA) with a high-contrast serif display and a terracotta or warm-clay accent (often near #D97757 — Anthropic's own Claude-interaction accent, so on a user's brief it reads as a tell);
2. a near-black background with a single bright acid-green or vermilion accent;
3. a broadsheet-style layout with hairline rules, zero border-radius, and dense newspaper-like columns;
4. the SaaS-card kit: content chopped into identical rounded cards, one border-radius on everything regardless of hierarchy, the same soft grey shadow (rgba(0,0,0,.1)) under each, and gradient washes as decoration;
5. template chrome that appears whatever the subject: a tracked-out ALL-CAPS eyebrow label above every heading; meta strings joined with middle dots ('A · B · C'); labels built as 'WORD — fragment' with a spaced em dash; tinted near-black (#0B0B0B, #111) standing in for black; a monospace face for small data labels; a '→' appended to link and button text.

All traits are legitimate for some briefs, but they are defaults rather than choices, and they appear regardless of subject. Where the brief pins down a visual direction, follow it exactly — the brief's own words always win, including when it asks for one of these looks. Where it leaves an axis free, don't spend that freedom on one of these defaults. As with a hired human designer, there's often a careful balance between doing what you're good at and taking each project as a chance to experiment and learn.

Work in two passes. First, brainstorm a short design plan based on the client's design brief: create a compact token system with color, type, layout, and principles.
- Color: describe the core base palette as 4–6 named hex values.
- Type: the typefaces and their roles.
- Layout: a layout concept, using one-sentence prose descriptions and ASCII wireframes to ideate and compare. Include alignment guidance; should the content be left aligned, center aligned, justified?
- Principles: the high-level guidance for what makes this page unique.

Then review that plan against the brief before building: if any part of it reads like the generic default you would produce for any similar page (work through a similar prompt to see if you arrive somewhere similar) rather than a choice made for this specific brief — revise that part, say what you changed and why. Only after you've confirmed the relative uniqueness of your design plan should you start to write the code, following the revised plan.

When writing the code, be careful of structuring your CSS selector specificities. It's easy to generate CSS classes that cancel each other out (especially with a type-based selector like .section and an element-based selector like .cta). This can happen often with padding/margin between sections.

## Restraint and self-critique

Spend your boldness in one place. Let one element be the memorable thing, keep everything around it quiet and disciplined, and cut any decoration that does not serve the brief. Build to a quality floor without announcing it: responsive down to mobile, visible keyboard focus, reduced motion respected, visually accessible, harmonious color palettes. Critique your own work as you build, taking screenshots to review if your environment supports it — a picture is worth 1000 tokens. Consider Chanel's advice: before leaving the house, take a look in the mirror and remove one accessory. Human creatives have memory and always try to do something new, so if you have a space to quickly jot down notes about what you've tried, it can help you in future passes.

## More on writing in design

Words appear in a design for one reason: to make it easier to understand and use. They are design content, not decoration. Bring the same intentionality and minimalism to copywriting that you would bring to spacing and color. Before writing anything, ask what the design needs to say, and how it can best be said to help the person navigate the experience.

Write from the end user's perspective. Name things by what users will understand in simple language, not by how the system is built. A user manages notifications, not webhook config. Describe what something is or does in plain terms rather than selling it. Being specific and legible to new users is always better than being clever.

Use active voice as default. A CTA says exactly what happens when it is used: "Save changes," not "Submit." An action keeps the same name through the whole flow, so the button that says "Publish" produces a toast that says "Published." The vocabulary of an interface is the signposting for someone navigating the product. Cohesion and consistency are how people learn their way around.

Treat failure and emptiness as moments for direction, not mood. Explain what went wrong and how to fix it, in the interface's voice rather than a person's. Errors don't apologize, and they are never vague about what happened. An empty screen is an invitation to act.

Keep the tone conversational: plain verbs, sentence case, no filler, with tone matched to the brand and the audience. Let each written element do exactly one job.
~~~~~

</section>
</div>
