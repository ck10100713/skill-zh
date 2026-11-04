---
name: ponytail-debt
description: >
  把每一則 `shortcut:` 註解（以及較舊的 `ponytail:`）列成技術債帳本。一次性報告，
  不改任何東西。用於「ponytail debt」、「what did ponytail defer」、「list the
  shortcuts」、/ponytail-debt。
---

每個刻意的 ponytail 捷徑，都會用一則 `shortcut:` 註解標出它的上限和升級路徑
（較舊的程式碼可能寫 `ponytail:`）。這個 skill 把它們集中成一份帳本，讓延後處理的事
不會悄悄變成永久的。

## 掃描

在 repo 裡 grep 註解標記，跳過 `.git` 和所有被
`.gitignore` 忽略的東西（相依套件、build 輸出、快取，不管哪種技術堆疊）：

`git grep --no-index --exclude-standard -nE '(#|//|/[*]) ?(shortcut|ponytail):'`  （如果你的技術堆疊用其他的註解前綴，就加上去）

如果使用者指定了自己的標記字（`/ponytail-debt TODO`），就改 grep 那個字。

每個命中是帳本的一列。註解前綴能讓只是提到這個慣例的
文字不被放進帳本。要跳過不是延後處理的命中，例如
講鍵盤快捷鍵（keyboard shortcut）的註解。

## 輸出

每個標記一列，依檔案分組：

`<file>:<line>, <what was simplified>. ceiling: <the limit named>. upgrade: <the trigger to revisit>.`

慣例是 `shortcut: <ceiling>, <upgrade path>`，所以直接從註解裡取出上限
和觸發條件。想要每列也附上負責人？加上
`git blame -L<line>,<line>`。

標出會腐爛的風險：任何沒寫升級路徑或
觸發條件的標記註解，都加上 `no-trigger` 標籤，那些就是會悄悄腐爛的。

結尾寫 `<N> markers, <M> with no trigger.` 什麼都沒找到：寫 `No shortcut debt. Clean ledger.`

## 範圍界線

只讀取並回報，不改任何東西。想存下來的話，跟它說一聲，它會把
帳本寫進檔案（例如 `PONYTAIL-DEBT.md`）。一次性。
