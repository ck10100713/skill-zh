---
name: airflow-dag-patterns
description: 用 operator、sensor、測試和部署的最佳實務，建構可上線的 Apache Airflow DAG。在建立資料 pipeline、編排工作流程或排程批次作業時使用。
---

# Apache Airflow DAG 模式

可上線的 Apache Airflow 模式，涵蓋 DAG 設計、operator、sensor、測試和部署策略。

## 何時使用這個 Skill

- 用 Airflow 建立資料 pipeline 編排
- 設計 DAG 結構和相依關係
- 實作自訂的 operator 和 sensor
- 在本機測試 Airflow DAG
- 在正式環境架設 Airflow
- 除錯失敗的 DAG 執行

## 核心概念

### 1. DAG 設計原則

| 原則       | 說明                         |
| --------------- | ----------------------------------- |
| **Idempotent**  | 跑兩次得到相同結果  |
| **Atomic**      | task 要嘛完全成功，要嘛完全失敗    |
| **Incremental** | 只處理新增或有變動的資料       |
| **Observable**  | 每一步都有 log、metric、警報 |

### 2. Task 相依關係

```python
# Linear
task1 >> task2 >> task3

# Fan-out
task1 >> [task2, task3, task4]

# Fan-in
[task1, task2, task3] >> task4

# Complex
task1 >> task2 >> task4
task1 >> task3 >> task4
```

## 快速開始

```python
# dags/example_dag.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(hours=1),
}

with DAG(
    dag_id='example_etl',
    default_args=default_args,
    description='Example ETL pipeline',
    schedule='0 6 * * *',  # 每天早上 6 點
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['etl', 'example'],
    max_active_runs=1,
) as dag:

    start = EmptyOperator(task_id='start')

    def extract_data(**context):
        execution_date = context['ds']
        # 在這裡寫 extract 邏輯
        return {'records': 1000}

    extract = PythonOperator(
        task_id='extract',
        python_callable=extract_data,
    )

    end = EmptyOperator(task_id='end')

    start >> extract >> end
```

## 詳細模式與實作範例

詳細的模式文件放在 `references/details.md`。上面的導覽層不夠用時，再讀那個檔案。

## 最佳實務

### 該做的

- **用 TaskFlow API** - 程式碼更乾淨，XCom 自動處理
- **設定 timeout** - 避免殭屍 task
- **用 `mode='reschedule'`** - 給 sensor 用，釋放 worker
- **測試 DAG** - 單元測試和整合測試
- **Idempotent 的 task** - 重試起來很安全

### 不該做的

- **不要用 `depends_on_past=True`** - 會造成瓶頸
- **不要寫死日期** - 用 `{{ ds }}` macro
- **不要用全域 state** - task 應該是無狀態的
- **不要盲目跳過 catchup** - 要先理解影響
- **不要把繁重的邏輯放在 DAG 檔案裡** - 從模組 import
