---
name: godot-gdscript-patterns
description: 精通 Godot 4 的 GDScript 模式，包含 signal、scene、狀態機與最佳化。適用於用 Godot 做遊戲、實作遊戲系統，或學習 GDScript 最佳實務的時候。
---

# Godot GDScript 模式

Godot 4.x 遊戲開發的 production 模式，使用 GDScript，涵蓋架構、signal、scene 與最佳化。

## 什麼時候用這個 Skill

- 用 Godot 4 做遊戲
- 用 GDScript 實作遊戲系統
- 設計 scene 架構
- 管理遊戲狀態
- 最佳化 GDScript 效能
- 學習 Godot 最佳實務

## 核心概念

### 1. Godot 架構

```
Node：基本建構單元
├── Scene：可重複使用的節點樹（存成 .tscn）
├── Resource：資料容器（存成 .tres）
├── Signal：事件通訊
└── Group：節點分類
```

### 2. GDScript 基礎

```gdscript
class_name Player
extends CharacterBody2D

# Signal
signal health_changed(new_health: int)
signal died

# Export（可在 Inspector 編輯）
@export var speed: float = 200.0
@export var max_health: int = 100
@export_range(0, 1) var damage_reduction: float = 0.0
@export_group("Combat")
@export var attack_damage: int = 10
@export var attack_cooldown: float = 0.5

# Onready（準備好時才初始化）
@onready var sprite: Sprite2D = $Sprite2D
@onready var animation: AnimationPlayer = $AnimationPlayer
@onready var hitbox: Area2D = $Hitbox

# 私有變數（慣例：底線開頭）
var _health: int
var _can_attack: bool = true

func _ready() -> void:
    _health = max_health

func _physics_process(delta: float) -> void:
    var direction := Input.get_vector("left", "right", "up", "down")
    velocity = direction * speed
    move_and_slide()

func take_damage(amount: int) -> void:
    var actual_damage := int(amount * (1.0 - damage_reduction))
    _health = max(_health - actual_damage, 0)
    health_changed.emit(_health)

    if _health <= 0:
        died.emit()
```

## 詳細模式與實作範例

詳細的模式文件放在 `references/details.md`，上面這一層導覽不夠用的時候再去讀那份檔案。

