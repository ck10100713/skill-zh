---
name: cloudflare-one-migrations
description: 評估並規劃從既有 VPN、SWG 或 SASE 平台遷移到 Cloudflare One，包含 policy 對應、功能落差和上線步驟。
---

# Cloudflare One Migrations

產生確切的設定之前，先檢索最新的 Cloudflare 文件、Cloudflare API schema 和來源廠商的匯出文件。

## Workflow

1. 找出來源環境：Zscaler ZIA、Zscaler ZPA、Palo Alto NGFW/Prisma/GlobalProtect、傳統 VPN/SWG/SD-WAN，或其他。
2. 做對應之前，先索取匯出檔和 log。結構化的匯出檔優先，截圖或文字摘要次之。
3. 建立盤點清單：身分、群組、應用程式、目的地、connector/tunnel、DNS/URL/防火牆/DLP/TLS policy、物件／清單、據點／站點、例外、命中次數，以及合規 logging。
4. 產出對應計畫：來源物件、Cloudflare One 的目標資源、信心程度、前置條件、不支援／部分支援的對應，以及需要人工決定的事項。
5. 先建立依賴項：身分／[SCIM](https://developers.cloudflare.com/cloudflare-one/team-and-resources/users/scim/index.md)、connector／on-ramp、route/DNS、清單／物件、TLS bypass、Access 應用程式／policy、Gateway policy、DLP/CASB、logging。
6. 安全地分階段進行：用遷移專用的前綴，預設建立停用或 audit 模式的規則，先用小群組／小據點試跑、比對 log，再擴大上線。
7. 每一條來源規則都要交代。每條規則必須對應到一個 Cloudflare 物件，或是一列明確的「Not Migrated」，並附上原因和資安影響。

## Exports To Ask For

- ZIA：URL filtering、防火牆 filtering、SSL inspection、DLP、自訂 URL 分類、IP 群組、network service／service group、使用者／群組／部門、據點、GRE tunnel 和靜態 IP。
- ZPA：app segment、segment group、server group、app connector／connector group、存取 policy、IdP／群組對應、私有 DNS 網域、port 和 protocol。
- Palo Alto/Prisma：security/NAT/decryption 規則、address/service 物件和群組、URL 分類、HIP profile、GlobalProtect 設定、Prisma Access 的 remote network／service connection 設定、zone、tag、log 和命中次數。

## Mapping Heuristics

- ZIA/SWG 的 policy 通常對應到 [Gateway traffic policies](https://developers.cloudflare.com/cloudflare-one/traffic-policies/index.md) 和 Gateway 清單。
- ZPA 的私有應用程式存取，通常對應到 [Access application types](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/choose-application-type/index.md)、[Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/index.md)、私有網路的 routing/DNS，以及 [Access policies](https://developers.cloudflare.com/cloudflare-one/access-controls/policies/index.md)。
- Palo Alto 的規則，要先搞懂流量方向、zone、物件、使用者、app、decryption 和命中次數，才能對應。不要不加思索地把 zone 攤平成清單。
- 傳統 VPN 的替代方案，通常是 Access + Cloudflare One Client / WARP + Tunnel 或 Mesh 做應用程式存取。只有需要站對站流量時才用 [Cloudflare WAN](https://developers.cloudflare.com/cloudflare-wan/index.md)；目前的做法請看 [Network VPN migration design guide](https://developers.cloudflare.com/reference-architecture/design-guides/network-vpn-migration/index.md) 和 [Replace your VPN](https://developers.cloudflare.com/cloudflare-one/setup/replace-vpn/index.md) 文件。

## Migration Assessment Prompts

- 來源涵蓋範圍：哪些產品在範圍內、有哪些匯出檔可用，以及截圖／文字摘要是不是藏住了缺漏的物件檔。
- 規則數量與命中資料：各規則類型的數量、停用／過期的規則、零命中規則、高命中規則，以及攸關業務的例外。
- 物件依賴：address 物件、service 物件、群組、自訂分類、network service、app ID、zone、tag、connector 和 server group。
- 身分就緒度：IdP、SCIM／群組同步、群組名稱正規化、針對個別使用者的規則、本地群組、service account 和外包人員的身分。
- TLS/DLP 就緒度：來源的 decryption 規則、有憑證綁定（certificate pinning）的 bypass、[DLP](https://developers.cloudflare.com/cloudflare-one/data-loss-prevention/index.md) 的 engine／profile、自訂 regex、精確比對資料，以及對 payload logging 的期待。
- 連線就緒度：來源的 tunnel／connector、私有 DNS、[Split Tunnels](https://developers.cloudflare.com/cloudflare-one/team-and-resources/devices/cloudflare-one-client/configure/route-traffic/split-tunnels/index.md) 或 bypass 行為、來源 IP 保留、[egress IP](https://developers.cloudflare.com/cloudflare-one/traffic-policies/egress-policies/index.md) 白名單，以及站對站的需求。
- 上線就緒度：試跑的群組／據點、並行運作期間、rollback 負責人、來源環境的退場條件，以及監控／log 比對計畫。

## Source-Specific Traps

### Zscaler ZIA / SWG

- 自訂 URL 分類常常會拆成獨立的 IP、網域和 URL 清單。要算產生出來的清單數量，不只是來源的分類數量。
- 有 IP 的 ZIA location 可以當來源 IP 清單用，但它們不會自動變成 [Gateway DNS locations](https://developers.cloudflare.com/cloudflare-one/networks/resolvers-and-proxies/dns/locations/index.md) 來限定 DNS policy 的範圍。
- GRE tunnel 的來源 IP 可以當 policy 條件的參考，但傳輸層的遷移是另外一條 Cloudflare Mesh（前身是 WARP Connector）或 Cloudflare WAN 的工作。
- CAUTION/warn 行為在 Gateway 裡沒有完全對等的功能。把它當成客戶要明確做的決定，不要默默選成放行或封鎖。
- DLP engine 和自訂 regex 通常得手動在 Cloudflare DLP 重建 profile。佔位用的 policy 不准啟用，彷彿 DLP 已經完成。
- Network application group 和不支援的 protocol 屬於部分對應。啟用前要先檢視。
- 如果沒有 SCIM，以身分為範圍的來源規則會變得過度寬鬆，除非你加上能強制執行的替代方案，例如使用者／email 清單。建立這些規則之前，先查 [Gateway identity selectors](https://developers.cloudflare.com/cloudflare-one/traffic-policies/identity-selectors/index.md)。

### Zscaler ZPA / Private Access

- ZPA 的 app segment、server group 和 connector group 不是 1:1 對應。Cloudflare 把 Access app、tunnel route、DNS 和 policy 分開處理。
- 透過 API 建立 tunnel，並不代表 connector 部署完成。cloudflared 的安裝、驗證和 origin 可達性要另外規劃。
- 每個 ZPA connector group 都建一個 Cloudflare Tunnel，不管 connector 的執行狀態是什麼（AUTHENTICATED、DISCONNECTED 或停用）。狀態是營運面的，不是架構面的。已斷線或舊的 group，在 tunnel 描述裡標記起來，驗證完之後由客戶決定要不要退場。
- group 裡每個 ZPA connector instance，對應一個用該 tunnel token 跑的 cloudflared replica。每個 group 的 replica 數量要配合 connector instance 的數量，才能保留相同的拓樸。一個 tunnel token 支援多個同時運行的 cloudflared 程序。建議把 replica 裝在同一個資料中心，但放在不同主機或子網路。
- 對每個 connector group，找出所有連到它的 server group，以及指派給這些 server group 的所有 app segment。這些 app segment 裡的 IP 位址和 CIDR，變成對應 tunnel 上的 CIDR route；網域名稱則變成同一個 tunnel 上的 hostname route。如果一個大的子網路就涵蓋了 app segment 的所有 IP，優先用一條 CIDR route 涵蓋整個子網路，不要每台主機各一條 /32 route。
- ZPA 的 bypass 在 Cloudflare 裡指的是 split-tunnel bypass，不是 Access 的 `bypass` 決策。Bypass 規則對應到 Cloudflare One Client 的 [Split Tunnel](https://developers.cloudflare.com/cloudflare-one/team-and-resources/devices/cloudflare-one-client/configure/route-traffic/split-tunnels/index.md) 排除項目。這是人工設定的步驟，沒有 API 可以自動化，客戶得透過 dashboard，把要 bypass 的網域和 IP 加到裝置 profile 的 split tunnel 排除清單。
- 無 agent／瀏覽器的 app，可能會變成每個網域各一個的公開 hostname Access app。WARP 的私有 app 則維持私有目的地的 app。
- Cloudflare Access 應用程式預設的目的地上限是每個 app 5 個 hostname。ZPA 遷移如果有很大的 app segment，實作前要聯絡 Cloudflare 的帳號團隊申請調高（最高 50）。建立 app 之前，要確認帳號上這個上限已經生效，否則大的 segment 必須拆成多個 policy 一模一樣的 app，物件數量會大幅增加。
- 綁定 IP 的 app，遷移前需要明確決定 egress 的處理：透過客戶自己的 egress 保留來源 IP、在可用的地方使用 Cloudflare 的[專屬 egress](https://developers.cloudflare.com/cloudflare-one/traffic-policies/egress-policies/index.md)，或接受目標服務必須更新、允許新的來源 IP。這是客戶要做的決定，沒解決的話會卡住實作。
- Resolver policy 可能是整個帳號層級的。跨據點或虛擬網路有重疊的私有 DNS 命名空間時要小心；改 DNS 之前，先檢索 [resolver policy](https://developers.cloudflare.com/cloudflare-one/traffic-policies/resolver-policies/index.md) 文件。
- 每條 ZPA access policy 規則，對應一個 Cloudflare 可重複使用的 Access policy。把它們掛到 Access app 之前，先把所有可重複使用的 policy 建好。在預設拒絕的 Gateway Network 環境裡，還要另外建一條 Network 允許規則，selector 用 "Self-hosted Access App with Private Address is Present"（wirefilter：`any(access.private_app[*] in {"*"})`），優先順序要高於任何廣泛的 L4 封鎖規則。沒有這條，Gateway 會在 Access policy 評估之前就把私有 app 的流量擋掉。
- 在 ZIA 和 ZPA 一起遷移的情況下，Gateway Network 規則可能會意外擋掉 Access 私有 app 的流量。上面那條 Gateway Network 允許規則就是解法：優先順序要比 ZIA 遷移過來的封鎖規則更高（編號更小）。啟用廣泛的 L4 封鎖之前，先加上這條規則並驗證。

### Palo Alto / Prisma / NGFW

- 一條 Palo Alto 規則可能產生多個 Cloudflare 資源。要保留的是規則的意圖，不是規則的數量。
- App-ID、URL 分類、zone、HIP、排程和 decryption 的行為很少能精確轉換。標記成部分對應，不要硬湊出假的對等。
- 匯出規則時，address/service 物件和群組要一起匯出。沒匯出物件的話，會出現看起來像默默遺失的情況，除非明確偵測。
- 範圍很廣的 `any` 目的地／服務規則，以及非常大的 CIDR，需要人工檢視。不要自動建立廣泛的 catchall。
- HIP／裝置檢查在強制執行之前，要先有 Cloudflare [device posture](https://developers.cloudflare.com/cloudflare-one/reusable-components/posture-checks/index.md) 的整合。

## Gotchas

- 來源的匯出檔常把引用拆在多個檔案裡。在宣告某條規則無法對應之前，先拿 ID 去物件、service 和 group 檔案裡查。
- 個別使用者、本地群組、部門和動態的 application ID，常常需要身分正規化。SCIM／群組同步是群組 selector 的先決條件。
- Zscaler 的 caution/warn 行為、Palo Alto 的 App-ID 行為，以及 TLS/decryption 的例外，可能沒有精確對等的功能。把它們標記成決策點，不要硬做 1:1 對應。
- 有的話，保留來源規則的順序和命中次數。停用或刪除過期／零命中的規則，一定要經過使用者同意。
- 除非使用者明確要求而且有時間限制，否則絕對不要為了維持連線而建立廣泛的全部放行 catchall。

## Validation Gates

- 每個遷移階段結束後，拿 Cloudflare 的物件數量跟解析出來的來源數量比對。不一致就停。
- 啟用 policy 之前，要檢視每一個 `unsupported`、`partial`、`unmapped`、`needs_identity`、`needs_posture` 和 `manual_review` 項目。
- SCIM 同步並重新驗證之後，用真實的試跑使用者驗證群組比對。
- 廣泛啟用 HTTP/DLP 封鎖之前，先測試 TLS inspection 和 Do Not Inspect 的行為。
- rollback 的路徑要明確：依前綴停用遷移過來的規則、恢復來源的 routing，或是撤回試跑的群組／據點。
- 宣告完成之前，產出一份來源規則的對帳表：每一項的已遷移物件、部分對應、未遷移的原因、資安影響，以及每個人工動作的負責人。

## Assessment Template

```markdown
## Migration Assessment

Source stack:
Artifacts reviewed:
Assumptions / missing exports:
Recommended Cloudflare One target:
Mapping summary:
Risks / partial mappings:
Not migrated:
Pilot plan:
Validation:
Rollback:
```

## Skill feedback

如果使用者反映這個 skill 給了錯誤或過時的指引，或是缺了資訊，就去讀 [references/skill-feedback.md](references/skill-feedback.md)。
