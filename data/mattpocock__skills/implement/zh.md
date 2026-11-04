---
name: implement
description: "依據 spec 或一組 ticket 實作一項工作。"
disable-model-invocation: true
---

實作使用者在 spec 或 ticket 裡描述的工作。

如果使用者給的是 ticket 參照，先去 issue tracker 抓下來，開工前先講出它的標題。如果參照有歧義，就問。

可行的話，用 Skill 工具呼叫 "tdd"，並且在事先講好的 seam 上做。

型別檢查要常跑，單一測試檔要常跑，完整測試套件最後跑一次就好。

做完之後，用 Skill 工具呼叫 "code-review" 來 review 這次的工作。

把你的成果 commit 到目前的 branch。
