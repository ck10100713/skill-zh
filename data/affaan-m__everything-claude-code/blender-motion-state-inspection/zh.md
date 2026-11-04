---
name: blender-motion-state-inspection
description: 檢查 Blender 角色、rig、姿勢、動畫 retargeting、地面接觸、朝向，或模型與動作是否對齊，而且光靠截圖不夠用的時候，使用這個 skill。
metadata:
  origin: ECC
tools: Read, Write, Edit, Bash, Grep, Glob
---

# Blender Motion State Inspection

## 何時使用

- Blender 角色在動畫裡看起來扭曲、鏡像、被壓扁、偏移，或腳在滑動。
- 使用者問匯入的 avatar、armature 或 retarget 過的動作，是否符合預期的姿勢。
- 你需要把渲染出來的證據，跟結構化的事實（例如骨骼、邊界框、接觸、朝向向量）做比較。
- 某個工作流程取決於判斷一個模型是角色、道具、代理網格、控制 rig，還是壞掉的匯入。

## 核心原則

不要只靠截圖來判斷有動畫的 3D 資產。截圖是 review 的證據，但它們會隱藏座標軸慣例、骨骼名稱、物件縮放、局部變換、有 parent 的網格、材質槽，以及逐格的接觸狀態。

先擷取結構化的 Blender 狀態，再用 viewport 截圖或渲染圖，來確認這些事實所暗示的結果。

## 運作方式

1. 在判斷動作之前，先建立乾淨的場景和資產基準線。
2. 用 exporter，或在 Blender 自己的直譯器內執行 Blender Python，從 Blender 擷取結構化的事實。
3. 取樣最可能暴露接觸、朝向、縮放和 retargeting 錯誤的那些影格。
4. 把量測到的事實，跟使用者預期的姿勢、方向、地平面和渲染目標做比較。
5. 回傳一份簡潔的報告，把已確認的事實、可能的原因和必要的修正分開。

## 檢查流程

1. 盤點場景。
   - 列出網格、armature、empty、相機、燈光、modifier、parent 關係和隱藏的物件。
   - 判斷 avatar 之前，先把角色網格跟輔助/代理幾何分開。
   - 記錄物件空間和世界空間的邊界框。

2. 辨識骨架。
   - 擷取 armature 名稱、pose bone、骨骼的 head/tail、roll、parent 鏈、constraint，以及 rest pose 的座標軸。
   - 對應語意上的骨骼，例如髖部、脊椎、頸部、頭部、肩膀、手肘、手、大腿、膝蓋、腳踝和腳。
   - 標出缺少的左/右成對骨骼，以及不尋常的命名方式。

3. 判斷前方、上方和側邊的座標軸。
   - 同時使用骨盆、脊椎、肩膀、髖部、頭部和腳；不要只靠單一網格法線。
   - 把 armature 的局部座標軸，跟世界座標軸及匯入檔案的慣例（例如 glTF 的 Y-up 對 Blender 的 Z-up）做比較。
   - 當臉部/頭部/腳的方向跟 root 的移動方向衝突時，標出可能鏡像或反向的匯入。

4. 取樣動畫影格。
   - 檢查第一格、中間、接觸、騰空和極端姿勢的影格。
   - 記錄 root 位置、root 朝向、骨盆高度、軀幹傾斜、四肢方向、腳離地距離和網格邊界。
   - 長或快的動作，要在翻轉、落地、轉身、碰撞和地板接觸附近取樣得更密。

5. 在怪罪 retargeting 之前，先檢查模型的完整性。
   - 套用動畫之前，先確認乾淨的基準形狀。
   - 保留原本的網格、材質、armature 和 skinning，除非使用者明確要求修復。
   - 把無法解釋的球狀團塊、巨大的代理網格或被壓扁的身體，視為匯入/選取問題，除非證明不是。

6. 診斷接觸和動作的問題。
   - 穿透地面：逐格比較最低的腳或鞋子頂點與地板高度。
   - 腳滑：比較腳著地的各格中，腳的世界位置。
   - 腿交叉：比較左/右大腿、膝蓋、腳踝和腳的左右順序。
   - 扭轉損壞：把骨骼的擺動方向，跟繞著肢體軸的 roll/twist 分開比較。
   - 縮放漂移：把有動畫的網格邊界，跟乾淨基準線的邊界做比較。

7. 先報告事實，再講意見。
   - 包含影格編號、物件名稱、骨骼名稱、世界座標和閾值。
   - 把已確認的失敗，跟視覺上的懷疑分開。
   - 要等結構化的狀態解釋了該看什麼之後，才附上截圖。

## 建議的報告格式

```markdown
## Blender Motion Inspection

### Scene Inventory
- Character candidates:
- Armatures:
- Helper/proxy objects:
- Cameras/lights:

### Orientation
- World up:
- Character forward:
- Root heading:
- Mirrored/backwards risk:

### Baseline Integrity
- Clean mesh bounds:
- Animated mesh bounds:
- Materials/skin preserved:
- Suspicious non-character meshes:

### Frame Findings
| Frame | Finding | Evidence |
| --- | --- | --- |
| 1 | Clean baseline pose | hips/spine/feet aligned |
| 96 | Foot penetrates floor | left_foot min_z = -0.04 |

### Verdict
- Pass/fail:
- Required fix:
- Render readiness:
```

## 範例

### 腳滑的走路循環

情境：retarget 過的角色在走路循環中看起來像在溜冰，但正面的鏡頭角度讓腳的接觸很難判斷。

套用這個流程：
- 盤點場景：角色網格 `HeroBody`、armature `HeroRig`、地面 `Floor`，沒有隱藏的代理網格。
- 辨識骨架：語意上的腳是 `foot.L` 和 `foot.R`；髖部是 `pelvis`；root 骨骼是 `root`。
- 取樣動畫影格：在腳著地的時刻前後，檢查第 1、18、24、30、42 和 48 格。
- 診斷接觸和動作的問題：比較腳著地各格中，腳在世界空間的位置。

擷取到的事實：

| Frame | Fact | Evidence |
| --- | --- | --- |
| 18 | 左腳著地 | `foot.L min_z = 0.004`，腳尖和腳跟都靠近地板 |
| 24 | 左腳著地時在滑動 | 六格之間 `foot.L x = 0.21 -> 0.28` |
| 30 | 骨盆持續向前移動 | `pelvis y = 1.14 -> 1.31` |

結論：渲染就緒度不通過。這個動作需要清理 foot-lock，或檢視 retargeting 的 constraint；身體網格不需要改比例。

### 反向匯入的角色

情境：角色在靜止影格裡看起來正確，但動畫往預期行進方向的反方向移動。

套用這個流程：
- 判斷前方、上方和側邊的座標軸：比較頭部、胸部、腳和 root 的移動。
- 取樣動畫影格：檢查第 1 格和行進路徑的中點。
- 先報告事實，再講意見：把 root 的朝向和模型面對的方向分開列出。

擷取到的事實：

| Frame | Fact | Evidence |
| --- | --- | --- |
| 1 | 角色的臉朝向世界的 `-Y` | 從 `neck` 到 `head` 的頭/胸向量，解出來是 `-Y` |
| 72 | Root 往世界的 `+Y` 移動 | `root y = 0.0 -> 2.8` |
| 72 | 腳在視覺上朝前，跟行進方向相反 | 腳趾骨骼指向 `-Y`，而位移是 `+Y` |

結論：很可能是反向匯入，或 retargeting 的前方座標軸對應不一致。在編輯動畫曲線之前，先修正匯入/retarget 的座標軸對應。

## 實用閾值

- 除非場景的單位縮放另有設定，否則假設 Blender 預設的公尺單位。
- 除非地板是軟的或刻意風格化，否則超過 1 到 2 公分的穿透地面都算看得出來。
- 突然超過 5% 的縮放變化，很可能是 rig、constraint 或變換繼承的問題。
- 在騰空倒立的動作中，左/右腳踝的左右順序翻轉，就算之後恢復了，也要視為腿交叉的風險。
- 除非來源動作包含瞬間轉身，否則 root 朝向每格跳超過 30 度都很可疑。

## 反面模式

- 除非任務明確是網格修復，否則不要為了硬湊姿勢而修改身體比例。
- 記錄乾淨的基準線之前，不要把它 bake 掉。
- 不要拿單一個渲染鏡頭角度，當成姿勢正確的證明。
- 在記錄下它們為什麼不屬於角色之前，不要刪除輔助物件。
- 沒有同時檢查頭部、腳、軀幹和 root 的移動之前，不要假設 avatar 面向 +Y、-Y、+X 或 -X。

## 工具備註

如果有 Blender 狀態 exporter，優先用包含網格、armature、pose bone、材質、接觸、邊界框和取樣動畫影格的 JSON。如果沒有 exporter，就透過 Blender 本身執行一支小小的 Blender Python script，例如 `blender --background scene.blend --python collect_motion_state.py`，因為 `bpy` 在一般的系統 Python 直譯器裡沒辦法用。
