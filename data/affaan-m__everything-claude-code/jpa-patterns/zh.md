---
name: jpa-patterns
description: Spring Boot 中的 JPA/Hibernate 模式，涵蓋 entity 設計、關聯、查詢最佳化、交易、稽核、索引、分頁和連線池。設計 JPA entity 或關聯，或需要修正 Hibernate 查詢、交易或 N+1 問題時使用。
metadata:
  origin: ECC
---

# JPA/Hibernate Patterns

用於 Spring Boot 中的資料建模、repository 和效能調校。

## When to Activate

- 設計 JPA entity 與資料表對應
- 定義關聯（@OneToMany、@ManyToOne、@ManyToMany）
- 最佳化查詢（避免 N+1、fetch 策略、projection）
- 設定交易、稽核或軟刪除
- 設定分頁、排序或自訂 repository 方法
- 調校連線池（HikariCP）或二級快取

## Entity Design

```java
@Entity
@Table(name = "markets", indexes = {
  @Index(name = "idx_markets_slug", columnList = "slug", unique = true)
})
@EntityListeners(AuditingEntityListener.class)
public class MarketEntity {
  @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @Column(nullable = false, length = 200)
  private String name;

  @Column(nullable = false, unique = true, length = 120)
  private String slug;

  @Enumerated(EnumType.STRING)
  private MarketStatus status = MarketStatus.ACTIVE;

  @CreatedDate private Instant createdAt;
  @LastModifiedDate private Instant updatedAt;
}
```

啟用稽核：
```java
@Configuration
@EnableJpaAuditing
class JpaConfig {}
```

## Relationships and N+1 Prevention

```java
@OneToMany(mappedBy = "market", cascade = CascadeType.ALL, orphanRemoval = true)
private List<PositionEntity> positions = new ArrayList<>();
```

- 預設用 lazy loading；需要時在查詢裡用 `JOIN FETCH`
- 集合上避免用 `EAGER`；讀取路徑用 DTO projection

```java
@Query("select m from MarketEntity m left join fetch m.positions where m.id = :id")
Optional<MarketEntity> findWithPositions(@Param("id") Long id);
```

## Repository Patterns

```java
public interface MarketRepository extends JpaRepository<MarketEntity, Long> {
  Optional<MarketEntity> findBySlug(String slug);

  @Query("select m from MarketEntity m where m.status = :status")
  Page<MarketEntity> findByStatus(@Param("status") MarketStatus status, Pageable pageable);
}
```

- 輕量查詢用 projection：
```java
public interface MarketSummary {
  Long getId();
  String getName();
  MarketStatus getStatus();
}
Page<MarketSummary> findAllBy(Pageable pageable);
```

## Transactions

- service 方法加上 `@Transactional`
- 讀取路徑用 `@Transactional(readOnly = true)` 來最佳化
- 謹慎選擇 propagation；避免長時間執行的交易

```java
@Transactional
public Market updateStatus(Long id, MarketStatus status) {
  MarketEntity entity = repo.findById(id)
      .orElseThrow(() -> new EntityNotFoundException("Market"));
  entity.setStatus(status);
  return Market.from(entity);
}
```

## Pagination

```java
PageRequest page = PageRequest.of(pageNumber, pageSize, Sort.by("createdAt").descending());
Page<MarketEntity> markets = repo.findByStatus(MarketStatus.ACTIVE, page);
```

類似 cursor 的分頁，要在 JPQL 裡加上 `id > :lastId` 並搭配排序。

## Indexing and Performance

- 為常用的過濾條件加索引（`status`、`slug`、外鍵）
- 使用符合查詢模式的複合索引（`status, created_at`）
- 避免 `select *`；只 project 需要的欄位
- 用 `saveAll` 和 `hibernate.jdbc.batch_size` 做批次寫入

## Connection Pooling (HikariCP)

建議的屬性：
```
spring.datasource.hikari.maximum-pool-size=20
spring.datasource.hikari.minimum-idle=5
spring.datasource.hikari.connection-timeout=30000
spring.datasource.hikari.validation-timeout=5000
```

PostgreSQL 處理 LOB 時，要加上：
```
spring.jpa.properties.hibernate.jdbc.lob.non_contextual_creation=true
```

## Caching

- 一級快取是每個 EntityManager 各自一份；避免讓 entity 跨交易存活
- 讀取量大的 entity，可以謹慎考慮二級快取；要驗證驅逐策略

## Migrations

- 用 Flyway 或 Liquibase；正式環境絕對不要依賴 Hibernate 的自動 DDL
- migration 要保持冪等且只加不減；沒有計畫就不要刪欄位

## Testing Data Access

- 優先用 `@DataJpaTest` 搭配 Testcontainers 來貼近正式環境
- 用 log 斷言 SQL 效率：設定 `logging.level.org.hibernate.SQL=DEBUG` 和 `logging.level.org.hibernate.orm.jdbc.bind=TRACE` 來看參數值

**記住**：entity 要精簡、查詢要有意圖、交易要短。用 fetch 策略和 projection 避免 N+1，並針對你的讀寫路徑建立索引。
