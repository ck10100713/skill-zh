---
name: pytorch-patterns
description: PyTorch 深度學習的模式與最佳實踐，用來建立穩健、有效率、可重現的訓練 pipeline、模型架構和資料載入。寫或 review PyTorch 訓練迴圈、模型架構、資料載入時使用，或是某次訓練跑不出一樣結果時使用。
metadata:
  origin: ECC
---

# PyTorch 開發模式

道地的 PyTorch 模式與最佳實踐，用來打造穩健、有效率、可重現的深度學習應用。

## 何時啟用

- 寫新的 PyTorch 模型或訓練腳本
- Review 深度學習程式碼
- 除錯訓練迴圈或資料 pipeline
- 最佳化 GPU 記憶體用量或訓練速度
- 建立可重現的實驗

## 核心原則

### 1. 不綁定裝置的程式碼

程式碼一律要能同時在 CPU 和 GPU 上跑，不要寫死裝置。

```python
# Good: 不綁定裝置
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = MyModel().to(device)
data = data.to(device)

# Bad: 寫死裝置
model = MyModel().cuda()  # 沒有 GPU 就會當掉
data = data.cuda()
```

### 2. 可重現性優先

把所有隨機種子都設好，結果才能重現。

```python
# Good: 完整的可重現設定
def set_seed(seed: int = 42) -> None:
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

# Bad: 沒有控制種子
model = MyModel()  # 每次跑的權重都不一樣
```

### 3. 明確管理 shape

tensor 的 shape 一定要寫註解，也要驗證。

```python
# Good: forward 有標註 shape
def forward(self, x: torch.Tensor) -> torch.Tensor:
    # x: (batch_size, channels, height, width)
    x = self.conv1(x)    # -> (batch_size, 32, H, W)
    x = self.pool(x)     # -> (batch_size, 32, H//2, W//2)
    x = x.view(x.size(0), -1)  # -> (batch_size, 32*H//2*W//2)
    return self.fc(x)    # -> (batch_size, num_classes)

# Bad: 沒有追蹤 shape
def forward(self, x):
    x = self.conv1(x)
    x = self.pool(x)
    x = x.view(x.size(0), -1)  # 這是什麼 size？
    return self.fc(x)           # 這樣真的能跑嗎？
```

## 模型架構模式

### 乾淨的 nn.Module 結構

```python
# Good: 結構清楚的 module
class ImageClassifier(nn.Module):
    def __init__(self, num_classes: int, dropout: float = 0.5) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(64 * 16 * 16, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        x = x.view(x.size(0), -1)
        return self.classifier(x)

# Bad: 什麼都塞在 forward
class ImageClassifier(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, x):
        x = F.conv2d(x, weight=self.make_weight())  # 每次呼叫都重新建 weight！
        return x
```

### 正確的權重初始化

```python
# Good: 明確初始化
def _init_weights(self, module: nn.Module) -> None:
    if isinstance(module, nn.Linear):
        nn.init.kaiming_normal_(module.weight, mode="fan_out", nonlinearity="relu")
        if module.bias is not None:
            nn.init.zeros_(module.bias)
    elif isinstance(module, nn.Conv2d):
        nn.init.kaiming_normal_(module.weight, mode="fan_out", nonlinearity="relu")
    elif isinstance(module, nn.BatchNorm2d):
        nn.init.ones_(module.weight)
        nn.init.zeros_(module.bias)

model = MyModel()
model.apply(model._init_weights)
```

## 訓練迴圈模式

### 標準訓練迴圈

```python
# Good: 完整的訓練迴圈，帶著最佳實踐
def train_one_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: torch.device,
    scaler: torch.amp.GradScaler | None = None,
) -> float:
    model.train()  # 一律要設成 train 模式
    total_loss = 0.0

    for batch_idx, (data, target) in enumerate(dataloader):
        data, target = data.to(device), target.to(device)

        optimizer.zero_grad(set_to_none=True)  # 比 zero_grad() 更有效率

        # 混合精度訓練
        with torch.amp.autocast("cuda", enabled=scaler is not None):
            output = model(data)
            loss = criterion(output, target)

        if scaler is not None:
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            scaler.step(optimizer)
            scaler.update()
        else:
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

        total_loss += loss.item()

    return total_loss / len(dataloader)
```

### 驗證迴圈

```python
# Good: 正確的評估方式
@torch.no_grad()  # 比在函式裡包 torch.no_grad() 區塊更有效率
def evaluate(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> tuple[float, float]:
    model.eval()  # 一律要設成 eval 模式，會關掉 dropout、改用 BN 的 running 統計
    total_loss = 0.0
    correct = 0
    total = 0

    for data, target in dataloader:
        data, target = data.to(device), target.to(device)
        output = model(data)
        total_loss += criterion(output, target).item()
        correct += (output.argmax(1) == target).sum().item()
        total += target.size(0)

    return total_loss / len(dataloader), correct / total
```

## 資料 pipeline 模式

### 自訂 Dataset

```python
# Good: 乾淨的 Dataset，帶 type hint
class ImageDataset(Dataset):
    def __init__(
        self,
        image_dir: str,
        labels: dict[str, int],
        transform: transforms.Compose | None = None,
    ) -> None:
        self.image_paths = list(Path(image_dir).glob("*.jpg"))
        self.labels = labels
        self.transform = transform

    def __len__(self) -> int:
        return len(self.image_paths)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, int]:
        img = Image.open(self.image_paths[idx]).convert("RGB")
        label = self.labels[self.image_paths[idx].stem]

        if self.transform:
            img = self.transform(img)

        return img, label
```

### 高效率的 DataLoader 設定

```python
# Good: 最佳化過的 DataLoader
dataloader = DataLoader(
    dataset,
    batch_size=32,
    shuffle=True,            # 訓練時要洗牌
    num_workers=4,           # 平行載入資料
    pin_memory=True,         # CPU->GPU 傳輸更快
    persistent_workers=True, # 讓 worker 在 epoch 之間保持存活
    drop_last=True,          # 讓 BatchNorm 的 batch 大小一致
)

# Bad: 慢吞吞的預設值
dataloader = DataLoader(dataset, batch_size=32)  # num_workers=0，沒有 pin_memory
```

### 處理變動長度資料的自訂 collate

```python
# Good: 在 collate_fn 裡做序列 padding
def collate_fn(batch: list[tuple[torch.Tensor, int]]) -> tuple[torch.Tensor, torch.Tensor]:
    sequences, labels = zip(*batch)
    # padding 到 batch 內的最大長度
    padded = nn.utils.rnn.pad_sequence(sequences, batch_first=True, padding_value=0)
    return padded, torch.tensor(labels)

dataloader = DataLoader(dataset, batch_size=32, collate_fn=collate_fn)
```

## Checkpoint 模式

### 儲存與載入 checkpoint

```python
# Good: 完整的 checkpoint，包含所有訓練狀態
def save_checkpoint(
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    epoch: int,
    loss: float,
    path: str,
) -> None:
    torch.save({
        "epoch": epoch,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "loss": loss,
    }, path)

def load_checkpoint(
    path: str,
    model: nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
) -> dict:
    checkpoint = torch.load(path, map_location="cpu", weights_only=True)
    model.load_state_dict(checkpoint["model_state_dict"])
    if optimizer:
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
    return checkpoint

# Bad: 只存模型權重（沒辦法接著訓練）
torch.save(model.state_dict(), "model.pt")
```

## 效能最佳化

### 混合精度訓練

```python
# Good: AMP 搭配 GradScaler
scaler = torch.amp.GradScaler("cuda")
for data, target in dataloader:
    with torch.amp.autocast("cuda"):
        output = model(data)
        loss = criterion(output, target)
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
    optimizer.zero_grad(set_to_none=True)
```

### 大模型用 gradient checkpointing

```python
# Good: 用運算換記憶體
from torch.utils.checkpoint import checkpoint

class LargeModel(nn.Module):
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # backward 時重算 activation 來省記憶體
        x = checkpoint(self.block1, x, use_reentrant=False)
        x = checkpoint(self.block2, x, use_reentrant=False)
        return self.head(x)
```

### 用 torch.compile 加速

```python
# Good: 編譯模型讓執行更快（PyTorch 2.0+）
model = MyModel().to(device)
model = torch.compile(model, mode="reduce-overhead")

# 模式："default"（最穩）、"reduce-overhead"（更快）、"max-autotune"（最快）
```

## 速查：PyTorch 慣用寫法

| 慣用寫法 | 說明 |
|-------|-------------|
| `model.train()` / `model.eval()` | 訓練或評估前一定要先設好模式 |
| `torch.no_grad()` | 推論時關掉梯度 |
| `optimizer.zero_grad(set_to_none=True)` | 清梯度更有效率 |
| `.to(device)` | 不綁定裝置地放置 tensor / 模型 |
| `torch.amp.autocast` | 混合精度，速度約 2 倍 |
| `pin_memory=True` | CPU→GPU 資料傳輸更快 |
| `torch.compile` | JIT 編譯加速（2.0+） |
| `weights_only=True` | 安全地載入模型 |
| `torch.manual_seed` | 可重現的實驗 |
| `gradient_checkpointing` | 用運算換記憶體 |

## 要避免的反模式

```python
# Bad: 驗證時忘了 model.eval()
model.train()
with torch.no_grad():
    output = model(val_data)  # dropout 還開著！BatchNorm 用的是 batch 統計！

# Good: 一律設成 eval 模式
model.eval()
with torch.no_grad():
    output = model(val_data)

# Bad: in-place 運算破壞 autograd
x = F.relu(x, inplace=True)  # 可能破壞梯度計算
x += residual                  # in-place 相加會破壞 autograd graph

# Good: 用非 in-place 運算
x = F.relu(x)
x = x + residual

# Bad: 在訓練迴圈裡反覆把東西搬到 GPU
for data, target in dataloader:
    model = model.cuda()  # 每次迭代都搬一次模型！

# Good: 迴圈前只搬一次模型
model = model.to(device)
for data, target in dataloader:
    data, target = data.to(device), target.to(device)

# Bad: backward 前就用 .item()
loss = criterion(output, target).item()  # 已經脫離計算圖了！
loss.backward()  # 錯誤：.item() 之後不能 backprop

# Good: .item() 只用在 logging
loss = criterion(output, target)
loss.backward()
print(f"Loss: {loss.item():.4f}")  # backward 之後用 .item() 就沒問題

# Bad: torch.save 用法不對
torch.save(model, "model.pt")  # 會存整個模型（很脆弱，不好移植）

# Good: 存 state_dict
torch.save(model.state_dict(), "model.pt")
```

__記住__：PyTorch 程式碼要不綁裝置、可重現、顧到記憶體。拿不定主意時，用 `torch.profiler` 做 profiling，再用 `torch.cuda.memory_summary()` 看 GPU 記憶體。
