---
name: azure-ai-anomalydetector-java
description: 用 Azure AI Anomaly Detector SDK（Java 版）建立異常偵測應用程式。在實作單變量／多變量異常偵測、時間序列分析或 AI 驅動的監控時使用。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: com.azure:azure-ai-anomalydetector
---

# Azure AI Anomaly Detector SDK（Java）

用 Azure AI Anomaly Detector SDK（Java 版）建立異常偵測應用程式。

## 安裝

```xml
<dependency>
  <groupId>com.azure</groupId>
  <artifactId>azure-ai-anomalydetector</artifactId>
  <version>3.0.0-beta.6</version>
</dependency>
```

## 建立 Client

### 同步與非同步 Client

```java
import com.azure.ai.anomalydetector.AnomalyDetectorClientBuilder;
import com.azure.ai.anomalydetector.MultivariateClient;
import com.azure.ai.anomalydetector.UnivariateClient;
import com.azure.core.credential.AzureKeyCredential;

String endpoint = System.getenv("AZURE_ANOMALY_DETECTOR_ENDPOINT");
String key = System.getenv("AZURE_ANOMALY_DETECTOR_API_KEY");

// 多變量 client，處理多個彼此相關的訊號
MultivariateClient multivariateClient = new AnomalyDetectorClientBuilder()
    .credential(new AzureKeyCredential(key))
    .endpoint(endpoint)
    .buildMultivariateClient();

// 單變量 client，處理單一變數的分析
UnivariateClient univariateClient = new AnomalyDetectorClientBuilder()
    .credential(new AzureKeyCredential(key))
    .endpoint(endpoint)
    .buildUnivariateClient();
```

### 使用 DefaultAzureCredential

```java
import com.azure.core.credential.TokenCredential;
import com.azure.identity.AzureIdentityEnvVars;
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.identity.ManagedIdentityCredentialBuilder;

TokenCredential credential = new DefaultAzureCredentialBuilder()
    .requireEnvVars(AzureIdentityEnvVars.AZURE_TOKEN_CREDENTIALS)
    .build();
// 或在正式環境直接使用指定的 credential：
// See https://learn.microsoft.com/java/api/overview/azure/identity-readme?view=azure-java-stable#credential-classes
// TokenCredential credential = new ManagedIdentityCredentialBuilder().build();

MultivariateClient client = new AnomalyDetectorClientBuilder()
    .credential(credential)
    .endpoint(endpoint)
    .buildMultivariateClient();
```

## 核心概念

### 單變量異常偵測
- **批次偵測**：一次分析整段時間序列
- **串流偵測**：對最新的資料點做即時偵測
- **變化點偵測**：偵測時間序列的趨勢變化

### 多變量異常偵測
- 可在 300 個以上彼此相關的訊號中偵測異常
- 用 Graph Attention Network 處理訊號之間的相關性
- 三個步驟：訓練 → 推論 → 取得結果

## 核心模式

### 單變量批次偵測

```java
import com.azure.ai.anomalydetector.models.*;
import java.time.OffsetDateTime;
import java.util.List;

List<TimeSeriesPoint> series = List.of(
    new TimeSeriesPoint(OffsetDateTime.parse("2023-01-01T00:00:00Z"), 1.0),
    new TimeSeriesPoint(OffsetDateTime.parse("2023-01-02T00:00:00Z"), 2.5),
    // ... 更多資料點（至少需要 12 個點）
);

UnivariateDetectionOptions options = new UnivariateDetectionOptions(series)
    .setGranularity(TimeGranularity.DAILY)
    .setSensitivity(95);

UnivariateEntireDetectionResult result = univariateClient.detectUnivariateEntireSeries(options);

// 檢查異常
for (int i = 0; i < result.getIsAnomaly().size(); i++) {
    if (result.getIsAnomaly().get(i)) {
        System.out.printf("Anomaly detected at index %d with value %.2f%n",
            i, series.get(i).getValue());
    }
}
```

### 單變量最新資料點偵測（串流）

```java
UnivariateLastDetectionResult lastResult = univariateClient.detectUnivariateLastPoint(options);

if (lastResult.isAnomaly()) {
    System.out.println("Latest point is an anomaly!");
    System.out.printf("Expected: %.2f, Upper: %.2f, Lower: %.2f%n",
        lastResult.getExpectedValue(),
        lastResult.getUpperMargin(),
        lastResult.getLowerMargin());
}
```

### 變化點偵測

```java
UnivariateChangePointDetectionOptions changeOptions = 
    new UnivariateChangePointDetectionOptions(series, TimeGranularity.DAILY);

UnivariateChangePointDetectionResult changeResult = 
    univariateClient.detectUnivariateChangePoint(changeOptions);

for (int i = 0; i < changeResult.getIsChangePoint().size(); i++) {
    if (changeResult.getIsChangePoint().get(i)) {
        System.out.printf("Change point at index %d with confidence %.2f%n",
            i, changeResult.getConfidenceScores().get(i));
    }
}
```

### 多變量模型訓練

```java
import com.azure.ai.anomalydetector.models.*;
import com.azure.core.util.polling.SyncPoller;

// 用 blob storage 的資料準備訓練請求
ModelInfo modelInfo = new ModelInfo()
    .setDataSource("https://storage.blob.core.windows.net/container/data.zip?sasToken")
    .setStartTime(OffsetDateTime.parse("2023-01-01T00:00:00Z"))
    .setEndTime(OffsetDateTime.parse("2023-06-01T00:00:00Z"))
    .setSlidingWindow(200)
    .setDisplayName("MyMultivariateModel");

// 訓練模型（長時間執行的操作）
AnomalyDetectionModel trainedModel = multivariateClient.trainMultivariateModel(modelInfo);

String modelId = trainedModel.getModelId();
System.out.println("Model ID: " + modelId);

// 檢查訓練狀態
AnomalyDetectionModel model = multivariateClient.getMultivariateModel(modelId);
System.out.println("Status: " + model.getModelInfo().getStatus());
```

### 多變量批次推論

```java
MultivariateBatchDetectionOptions detectionOptions = new MultivariateBatchDetectionOptions()
    .setDataSource("https://storage.blob.core.windows.net/container/inference-data.zip?sasToken")
    .setStartTime(OffsetDateTime.parse("2023-07-01T00:00:00Z"))
    .setEndTime(OffsetDateTime.parse("2023-07-31T00:00:00Z"))
    .setTopContributorCount(10);

MultivariateDetectionResult detectionResult = 
    multivariateClient.detectMultivariateBatchAnomaly(modelId, detectionOptions);

String resultId = detectionResult.getResultId();

// 輪詢結果
MultivariateDetectionResult result = multivariateClient.getBatchDetectionResult(resultId);
for (AnomalyState state : result.getResults()) {
    if (state.getValue().isAnomaly()) {
        System.out.printf("Anomaly at %s, severity: %.2f%n",
            state.getTimestamp(),
            state.getValue().getSeverity());
    }
}
```

### 多變量最新資料點偵測

```java
MultivariateLastDetectionOptions lastOptions = new MultivariateLastDetectionOptions()
    .setVariables(List.of(
        new VariableValues("variable1", List.of("timestamp1"), List.of(1.0f)),
        new VariableValues("variable2", List.of("timestamp1"), List.of(2.5f))
    ))
    .setTopContributorCount(5);

MultivariateLastDetectionResult lastResult = 
    multivariateClient.detectMultivariateLastAnomaly(modelId, lastOptions);

if (lastResult.getValue().isAnomaly()) {
    System.out.println("Anomaly detected!");
    // 檢查造成異常的變數
    for (AnomalyContributor contributor : lastResult.getValue().getInterpretation()) {
        System.out.printf("Variable: %s, Contribution: %.2f%n",
            contributor.getVariable(),
            contributor.getContributionScore());
    }
}
```

### 模型管理

```java
// 列出所有模型
PagedIterable<AnomalyDetectionModel> models = multivariateClient.listMultivariateModels();
for (AnomalyDetectionModel m : models) {
    System.out.printf("Model: %s, Status: %s%n",
        m.getModelId(),
        m.getModelInfo().getStatus());
}

// 刪除模型
multivariateClient.deleteMultivariateModel(modelId);
```

## 錯誤處理

```java
import com.azure.core.exception.HttpResponseException;

try {
    univariateClient.detectUnivariateEntireSeries(options);
} catch (HttpResponseException e) {
    System.out.println("Status code: " + e.getResponse().getStatusCode());
    System.out.println("Error: " + e.getMessage());
}
```

## 環境變數

```bash
AZURE_ANOMALY_DETECTOR_ENDPOINT=https://<resource>.cognitiveservices.azure.com/ # 所有認證方式都必填
AZURE_ANOMALY_DETECTOR_API_KEY=<your-api-key> # 只有用 AzureKeyCredential 認證時才需要
AZURE_TOKEN_CREDENTIALS=prod  # 只有在正式環境用 DefaultAzureCredential 時才需要
```

## 最佳實務

1. **最少資料點數**：單變量至少需要 12 個點；資料越多越準
2. **粒度要對齊**：`TimeGranularity` 要和實際的資料頻率一致
3. **調整靈敏度**：值越高（0-99）偵測到的異常越多
4. **多變量訓練**：依模式的複雜度，滑動視窗用 200-1000
5. **錯誤處理**：API 錯誤一律要處理 `HttpResponseException`

## 觸發詞

- "anomaly detection Java"
- "detect anomalies time series"
- "multivariate anomaly Java"
- "univariate anomaly detection"
- "streaming anomaly detection"
- "change point detection"
- "Azure AI Anomaly Detector"
