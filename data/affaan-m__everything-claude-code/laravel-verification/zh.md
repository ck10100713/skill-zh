---
name: laravel-verification
description: "Laravel 專案的驗證循環：環境檢查、linting、靜態分析、含覆蓋率的測試、安全掃描與部署就緒檢查。在 merge 或 deploy 前驗證 Laravel 專案時使用（lint、靜態分析、測試、覆蓋率、安全）。"
metadata:
  origin: ECC
---

# Laravel 驗證循環

在開 PR 前、重大變更後與部署前執行。

## 何時使用

- 為 Laravel 專案開 pull request 之前
- 大型重構或依賴升級之後
- staging 或 production 的部署前驗證
- 執行完整的 lint -> test -> security -> deploy readiness 流程

## 運作方式

- 依序執行各階段，從環境檢查一路到部署就緒，讓每一層都建立在前一層之上。
- 環境與 Composer 檢查是所有後續步驟的關卡，失敗就立刻停下來。
- 跑完整測試與覆蓋率之前，linting/靜態分析要先乾淨。
- 安全與 migration 的 review 放在測試之後，先驗證行為，再處理資料或發版步驟。
- Build/部署就緒與 queue/scheduler 檢查是最後的關卡，任何一項失敗都擋住發版。

## 階段 1：環境檢查

```bash
php -v
composer --version
php artisan --version
```

- 確認 `.env` 存在，且必要的 key 都有
- production 環境確認 `APP_DEBUG=false`
- 確認 `APP_ENV` 符合目標部署環境（`production`、`staging`）

如果在本機用 Laravel Sail：

```bash
./vendor/bin/sail php -v
./vendor/bin/sail artisan --version
```

## 階段 1.5：Composer 與 Autoload

```bash
composer validate
composer dump-autoload -o
```

## 階段 2：Linting 與靜態分析

```bash
vendor/bin/pint --test
vendor/bin/phpstan analyse
```

如果你的專案用 Psalm 而不是 PHPStan：

```bash
vendor/bin/psalm
```

## 階段 3：測試與覆蓋率

```bash
php artisan test
```

覆蓋率（CI）：

```bash
XDEBUG_MODE=coverage php artisan test --coverage
```

CI 範例（format -> 靜態分析 -> 測試）：

```bash
vendor/bin/pint --test
vendor/bin/phpstan analyse
XDEBUG_MODE=coverage php artisan test --coverage
```

## 階段 4：安全與依賴檢查

```bash
composer audit
```

## 階段 5：資料庫與 Migration

```bash
php artisan migrate --pretend
php artisan migrate:status
```

- 仔細 review 具破壞性的 migration
- 確認 migration 檔名遵循 `Y_m_d_His_*`（例如 `2025_03_14_154210_create_orders_table.php`），且清楚描述變更內容
- 確保可以 rollback
- 檢查 `down()` method，沒有明確備份就不要造成無法復原的資料遺失

## 階段 6：Build 與部署就緒

```bash
php artisan optimize:clear
php artisan config:cache
php artisan route:cache
php artisan view:cache
```

- 確認 production 設定下的快取預熱能成功
- 確認 queue worker 與 scheduler 都已設定
- 確認目標環境中 `storage/` 與 `bootstrap/cache/` 可寫入

## 階段 7：Queue 與 Scheduler 檢查

```bash
php artisan schedule:list
php artisan queue:failed
```

如果有用 Horizon：

```bash
php artisan horizon:status
```

如果可以用 `queue:monitor`，就用它檢查積壓量，不用真的處理 job：

```bash
php artisan queue:monitor default --max=100
```

主動驗證（僅限 staging）：把一個空操作 job 派發到專用的 queue，再跑單一 worker 處理它（確認已設定非 `sync` 的 queue connection）。

```bash
php artisan tinker --execute="dispatch((new App\\Jobs\\QueueHealthcheck())->onQueue('healthcheck'))"
php artisan queue:work --once --queue=healthcheck
```

確認該 job 產生了預期的副作用（log 紀錄、healthcheck 資料表的資料列，或 metric）。

只在處理測試 job 很安全的非 production 環境執行。

## 範例

最小流程：

```bash
php -v
composer --version
php artisan --version
composer validate
vendor/bin/pint --test
vendor/bin/phpstan analyse
php artisan test
composer audit
php artisan migrate --pretend
php artisan config:cache
php artisan queue:failed
```

CI 風格的 pipeline：

```bash
composer validate
composer dump-autoload -o
vendor/bin/pint --test
vendor/bin/phpstan analyse
XDEBUG_MODE=coverage php artisan test --coverage
composer audit
php artisan migrate --pretend
php artisan optimize:clear
php artisan config:cache
php artisan route:cache
php artisan view:cache
php artisan schedule:list
```
