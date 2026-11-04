---
name: cloudflare-one
description: 設計、設定、排查或審查 Cloudflare One 的 Zero Trust 和 SASE 部署。從其他廠商遷移的規劃請用 cloudflare-one-migrations。
---

# Cloudflare One

引用限制、設定、API 欄位、分類 ID 或確切的 UI 路徑之前，先從 [Cloudflare One docs](https://developers.cloudflare.com/cloudflare-one/index.md)、Cloudflare docs MCP server 或 Cloudflare API schema 檢索最新資訊。

## Workflow

1. 先分類需求：架構、設定、排查、遷移或審查。
2. 收集背景：帳號 ID、使用者／據點／app、身分提供者、SCIM／群組同步、裝置管理、流量路徑、合規限制，以及上線的影響範圍。
3. 只檢索所涉及產品需要的最新文件：Access、Gateway、WARP／裝置用戶端、Tunnel/Mesh、Cloudflare WAN、DLP、CASB、device posture 或身分。
4. 如果能存取帳號，在提出或做出變更之前，先檢查既有資源：Access app/policy/group/IdP、Gateway 規則／清單／分類、裝置 profile／posture 檢查、tunnel／route、DNS／resolver 設定，以及 location／據點。
5. 提出變更清單時，要附上前置條件、驗證和 rollback。有風險的變更，除非使用者明確要求，否則預設停用，或限定在試跑的群組／據點。

## Assessment Prompts

用這些來避免一上來就直接動設定。只問跟使用者任務有關的。

### Architecture and Current State

- 據點與使用者：辦公室、分公司、資料中心、VPC、遠端使用者、外包人員、使用者人數，以及目前的連線模型。
- 應用程式與目的地：SaaS、公開 app、私有 app、API、基礎設施目標、protocol、port、hostname 和 IP 範圍。
- 連線：VPN、MPLS、SD-WAN、直接上網出口、集中式回傳、站對站需求，以及私有 DNS 架構。
- 安全架構：目前的 SWG、NGFW、VPN/ZTNA、DLP、CASB、email 安全、logging 和合規需求。
- 身分：IdP、SCIM／群組同步、群組命名、多 IdP 需求、service account，以及外包／夥伴的存取。
- 上線：試跑的使用者／據點、影響範圍、rollback 路徑、支援負責人和成功標準。

### Access and SaaS Federation

- App 的形式：web app、API、SSH/RDP/VNC、資料庫、SaaS app、公開 hostname、私有 IP 或私有 hostname。選擇之前，先檢索 [Access application type](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/choose-application-type/index.md) 文件。
- Access 模型：無 client 的瀏覽器存取、搭配裝置用戶端的私有網路、點對點連線、用 service token 或 mutual TLS 的服務連線，或 SaaS SSO 聯邦。
- Policy 需求：使用者群組、device posture、session 時長、mTLS、service token 和 app launcher 的可見性。設定 selector 或評估順序之前，先檢索 [Access policy](https://developers.cloudflare.com/cloudflare-one/access-controls/policies/index.md) 文件。
- SaaS 細節：支援 SAML 還是 OIDC、ACS／redirect URL、Entity ID／client ID、必要的屬性，以及租戶控制的需求。

### Tunnel and Private Networking

- 據點與網段：哪些資料中心、VPC、辦公室或網路網段需要連線。
- HA：dev/test 用單一 connector、正式環境用多個 connector，或進階的多 tunnel／據點備援。
- Runtime：cloudflared 或 Cloudflare Mesh 節點（前身是 WARP Connector）要跑在哪裡：VM、容器、Kubernetes、實體機或其他目標。
- Egress：connector 能不能透過所需的對外 port／protocol 連到 Cloudflare。講出確切的 endpoint 之前，先檢索 [Tunnel connectivity prechecks](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/troubleshoot-tunnels/connectivity-prechecks/index.md)。
- Origin 可達性：connector 能不能解析並連到每一個私有 origin。
- Routing：需要的 CIDR／hostname、重疊的 IP 空間、[virtual networks](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/private-net/cloudflared/tunnel-virtual-networks/index.md)、[Split Tunnels](https://developers.cloudflare.com/cloudflare-one/team-and-resources/devices/cloudflare-one-client/configure/route-traffic/split-tunnels/index.md)，以及私有 DNS／[resolver policy](https://developers.cloudflare.com/cloudflare-one/traffic-policies/resolver-policies/index.md) 的需求。
- 管理模型：新部署優先用遠端管理／以 token 為基礎的 tunnel，除非有明確理由要用本地設定。

### Gateway, TLS, and DLP

- 流量控制：DNS 分類、HTTP URL／路徑檢查、L4 port／protocol、egress IP 需求、自訂清單，以及允許／封鎖的例外。要知道目前的 selector 和執行順序，先檢索 [Gateway traffic policy](https://developers.cloudflare.com/cloudflare-one/traffic-policies/index.md) 文件。
- 身分：Gateway policy 需要不需要使用者或群組 selector，以及使用者會不會透過 Cloudflare One Client／IdP 的情境完成驗證。涉及群組時，檢查 [Gateway identity selectors](https://developers.cloudflare.com/cloudflare-one/traffic-policies/identity-selectors/index.md) 和 [SCIM provisioning](https://developers.cloudflare.com/cloudflare-one/team-and-resources/users/scim/index.md)。
- TLS inspection：根 CA 的部署路徑、有憑證綁定的應用程式、合規例外，以及 FIPS 需求。啟用之前，先檢索 [TLS decryption](https://developers.cloudflare.com/cloudflare-one/traffic-policies/http-policies/tls-decryption/index.md) 文件。
- DLP：敏感資料類型、要檢查的管道、TLS inspection 就緒度、DLP profile、payload logging 需求，以及對誤判的容忍度。建立強制執行之前，先檢索 [DLP](https://developers.cloudflare.com/cloudflare-one/data-loss-prevention/index.md) 文件。

撰寫或審查由 HTTP Forward action 呼叫的 Workers 時，用 [gateway-workers skill](../gateway-workers/SKILL.md)。

### CASB, Device Posture, and Risk

- CASB：SaaS 廠商、管理員存取層級、掃描 policy、組織規模、修復的負責人，以及是否也需要 inline 保護。建議修復方式之前，先檢索 [CASB findings](https://developers.cloudflare.com/cloudflare-one/cloud-and-saas-findings/manage-findings/index.md) 文件。
- Device posture：必要的檢查、第三方 EDR/MDM 整合、enrollment 規則、裝置 profile，以及 split tunnel 的一致性。
- 風險評分：相關的行為訊號、誤判的來源（例如 VPN 或 service account），以及風險分數是用來調查還是用來強制執行。在 policy 裡使用風險分數之前，先檢索 [user risk score](https://developers.cloudflare.com/cloudflare-one/team-and-resources/users/risk-score/index.md) 文件。

### Cloudflare WAN / Site Connectivity

- 據點拓樸、on-ramp 類型、route 的擁有者、tunnel 備援、靜態 route 與 BGP 管理的 route、網路防火牆需求，以及設備／profile 的擁有者。提出據點連線的變更之前，先檢索 [Cloudflare WAN](https://developers.cloudflare.com/cloudflare-wan/index.md) 和 [Cloudflare Network Firewall](https://developers.cloudflare.com/cloudflare-network-firewall/index.md) 文件。

## Guardrails

- Access 控制應用程式的授權；Gateway 控制流量的檢查／過濾。需求同時涵蓋「知道身分的 app 存取」和「網路／網頁安全」時，兩個都要用。
- 新的 Access 部署，要透過可重複使用的 policy API（`/access/policies`）建立 policy，再把它們掛到應用程式上。不要在建立／更新應用程式的 request 裡送內嵌的 `policies`，除非目前的 API 文件明確要求 app 範圍的 policy。
- 被回報為 `reusable: false` 的 app 範圍 policy，視為舊版。用文件記載的 `make_reusable` endpoint 遷移既有的 policy，或換成可重複使用的 policy；不要建立新的舊版 policy。要區分舊版 policy 和已棄用的舊版私有網路應用程式類型。
- 公開 hostname 的 Access app 可以不需要 client。私有目的地的 app 需要 Cloudflare One Client 或其他網路 on-ramp，再加上 route 和 DNS 解析。設定私有目的地之前，先檢索 [self-hosted private app](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/non-http/self-hosted-private-app/index.md) 文件。
- Cloudflare Tunnel 是從私有網路到 Cloudflare 的 off-ramp。Cloudflare WAN 和 Mesh 是另外的 off-ramp，同時也可以當 on-ramp。
- 以群組為基礎的 policy 取決於 IdP 的群組 claim 或 SCIM。沒有群組同步的話，不要自己編群組 selector。
- 私有 hostname 需要明確的 DNS routing／解析；只建立 Access app 是不夠的。用 [resolver policies](https://developers.cloudflare.com/cloudflare-one/traffic-policies/resolver-policies/index.md)，並檢視 [Connect a private hostname](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/private-net/cloudflared/connect-private-hostname/index.md)
- 加密網頁流量的 HTTP inspection 和 DLP，需要 TLS inspection，以及事先規劃好的 Do Not Inspect 例外。
- Gateway 的 DNS、Network、HTTP 和 Egress policy，評估語意各不相同。解釋優先順序之前，先檢索 [order of enforcement](https://developers.cloudflare.com/cloudflare-one/traffic-policies/order-of-enforcement/index.md) 文件。
- 範圍廣的封鎖／允許／DLP/TLS policy，一開始要先停用，而且限定在試跑、有明確目標使用者或群組的範圍，除非使用者同意擴大上線。

### Identity and Access

- Access Group 是 Cloudflare 的物件；IdP/SCIM 群組是身分 claim。Gateway 的群組 selector 用的是同步過來的 IdP 群組，不是 Access Group。
- 群組名稱和 SAML/OIDC 屬性大小寫有差。建立以群組為基礎的規則之前，先驗證確切的 claim 名稱和值。
- SCIM 變更和群組成員資格，在同步與重新驗證完成之前可能是過期的。排查時要看使用者最後一次驗證的身分，不是只看 IdP 的狀態。
- Access policy 預設是拒絕。私有 app 即使有 route，沒有 Allow policy 還是會擋掉存取。
- Access policy 的 selector 可以用 IP 清單，不能用 Gateway 的網域或 URL 清單。
- SaaS 聯邦處理的是登入進 SaaS app 的驗證。SaaS 的授權和租戶限制，通常需要 SaaS 端的角色，及／或 Gateway 的租戶控制。
- SSH/VNC/RDP 的 Browser Rendering 是 Access 的功能。Browser Isolation 是遠端渲染一般網頁內容。不要搞混。

### Device Client Deployment

- [Cloudflare One 裝置用戶端](https://developers.cloudflare.com/cloudflare-one/team-and-resources/devices/cloudflare-one-client/index.md)是使用者裝置的 on-ramp。有兩個元件控制它：**enrollment 規則**（誰可以連線）和**裝置 profile**（enrollment 之後用戶端的行為）。
- enrollment 規則是類型為 `warp` 的 Access 應用程式，不是裝置設定。它接受可重複使用的 Access policy。debug enrollment 要到 Access 找，不是 Devices。
- 無頭或自主運作的裝置（服務、kiosk、Linux 主機），用 service token 做 enrollment。非人類裝置會以 `non_identity@[team-domain].cloudflareaccess.com` 的身分驗證，沒有群組成員資格，所以以 IdP 群組為目標的裝置 profile 對它們不會比對到。要明確用 non-identity email、裝置的特定慣例（作業系統資訊等）來指定無頭裝置，或讓它們落到預設 profile。
- 裝置 profile 控制連線模式、[split tunnel](https://developers.cloudflare.com/cloudflare-one/team-and-resources/devices/cloudflare-one-client/configure/route-traffic/split-tunnels/index.md) 設定、使用者權限（停用、switch lock）、自動重連和 captive portal 行為。Profile 依優先順序，用使用者群組或裝置屬性比對，第一個符合的生效，其餘的落到預設 profile。
- Split tunnel 模式是影響最大的單一 client 設定。依部署目標選模式：

  | 目標 | 模式 | 理由 |
  |---|---|---|
  | 只做 VPN 替代（私有 app） | **Include** | 只把指定的私有 CIDR 和 hostname 透過 client 走。其他都直連。影響範圍最小。 |
  | 只做 SWG（網際網路安全） | **Exclude** | 所有流量都透過 client。只排除會壞掉的（本地印表機、有憑證綁定的 app）。 |
  | VPN 替代 + SWG | **Exclude** | 所有流量都透過 client。最常見的企業設定。 |
  | 與另一套 VPN 共存 | **Include** | 避免跟另一套 VPN 的 tunnel 介面和 DNS 控制衝突。 |
  | 只做 DNS 過濾 | DNS-only 模式 | 只有 DNS 查詢送到 Gateway。不代理流量。 |

- Include 或 exclude 是以 profile 為單位，不是以每個項目為單位。同一個 profile 裡不能混用模式。部署到一半切換模式，每個項目都要重新評估。
- Split tunnel 的項目必須跟 tunnel route 雙向對齊。include 清單裡有 CIDR 卻沒有對應的 tunnel route，會造成黑洞。有 tunnel route 卻沒有對應的裝置 profile 項目，流量就永遠不會進入 tunnel。
- MDM 參數（`mdm.xml`／managed preferences）會覆蓋 dashboard 上設定的 profile 設定，只要檔案裡有指定那個設定。如果 dashboard 的變更對受管裝置看起來沒效果，就檢查 MDM 設定。各平台的檔案位置和參數，檢索 [MDM deployment](https://developers.cloudflare.com/cloudflare-one/team-and-resources/devices/cloudflare-one-client/deployment/mdm-deployment/index.md) 文件。
- 如果有另一個 VPN client 或 agent 在裝置上控制 DNS，裝置用戶端的 DNS 攔截會衝突。共存的情境下，用「traffic only」模式來避免 routing table 和 DNS 的衝突。
- Captive portal 偵測到 portal（飯店 WiFi、機場）時，會暫時斷開 client。這是終端使用者常見的困擾來源，要小心管理。

### Private Networking

- Split tunnel 模式會改變每個 route 決策的意義：Exclude 模式下，從排除清單移除，流量才會送到 Cloudflare；Include 模式下，加進 include 清單，流量才會送出。
- Virtual network 主要用在 IP 子網路重疊、而且不用 hostname routing 的情況。它也可以用來控制其他使用者的連線行為，但建議透過安全 policy 來管理。
- tunnel 狀態健康，只證明 cloudflared 連得到 Cloudflare。tunnel 還必須有適當的已發布應用程式 route、網路 route 或 hostname route，連線才會運作。
- Cloudflare Tunnel 和 Cloudflare Mesh 都能用來連到內部網路。Cloudflare WAN 也可以，但需要 Enterprise 訂閱。在 Tunnel 類型之間猶豫時，檢索 [choose an on-ramp](https://developers.cloudflare.com/learning-paths/secure-internet-traffic/connect-devices-networks/choose-on-ramp/index.md)。
- 正式環境的 HA 要跑多個 cloudflared connector，最好放在不同主機。以 token 為基礎、遠端管理的 tunnel 是新部署的預設。

### Gateway, TLS, and DLP

- `dns.domains` 比對網域和子網域；`dns.fqdn` 只做精確比對。
- DNS 解析前和解析後的 selector，行為不像單一的嚴格優先順序清單。調整規則順序之前，先檢索目前的評估文件。
- HTTP 的 Do Not Inspect 規則，會在 HTTP 的 Allow/Block/Isolate 行為之前執行。後面的封鎖規則不會覆蓋前面的檢查略過。
- 有憑證綁定的 app，在廣泛啟用 TLS inspection 之前，需要先有 Do Not Inspect 例外。啟用 inspection 之前，先把 Cloudflare 根 CA 部署到受管裝置。
- DLP profile 只是偵測的定義。在被 DLP policy 或 CASB 整合引用之前，它們不會強制執行任何事。[Passive Detection](https://developers.cloudflare.com/cloudflare-one/data-loss-prevention/passive-detection/index.md) 會在還沒有任何 policy 之前，就從取樣的 Gateway 流量中顯示比對結果；用它來決定要記錄或封鎖什麼。有 body 檢查的規則，可能在單次處理中被評估多次。
- DLP 從適當的地方開啟 payload logging 開始，調校誤判，再封鎖。
- Gateway Network policy 是嚴格的 L4 控制。以身分為基礎的 L4 比對，需要已驗證的裝置情境。

### CASB, Risk, and Operations

- API CASB 是帶外而且定期的。它不提供即時的 inline 強制執行，雖然有些整合支援「修復」；在支援的應用程式上要做 inline CASB 能力，用 Gateway 的細粒度應用程式控制。為特定 SaaS 應用程式的特定動作建立安全 policy 時，檢索 [Granular application controls](https://developers.cloudflare.com/cloudflare-one/traffic-policies/http-policies/granular-controls/index.md)。
- CASB 的 finding 綁定特定的資產和 instance。建議修復方式之前，先往下看受影響的資產。
- CASB 修復用 dashboard 目前的修復指引。大部分的修復發生在 SaaS 的管理後台，不是 Cloudflare。
- CASB 掃描是定期的：第一次掃描可能要好幾個小時，之後大約每 24 到 48 小時掃一次。承諾時間之前，先檢索 [CASB troubleshooting](https://developers.cloudflare.com/cloudflare-one/cloud-and-saas-findings/troubleshoot-casb/index.md)。重新授權可能會重設掃描狀態；重新連線之前，先檢查憑證的健康狀況。
- 使用者風險分數是以行為為基礎、而且非同步的。CASB 的 finding 不會自動代表使用者風險高。

### Infrastructure Access

- [Zero Trust Infrastructure Access](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/non-http/infrastructure-apps/index.md)（ZTIA）是專門為透過裝置用戶端做 SSH 存取打造的方案。它提供 self-hosted app 沒有的能力：按鍵紀錄、控制使用者如何對目標機器驗證、用綁定 Access 身分的臨時憑證取代靜態 SSH key 的[短效憑證](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/use-cases/ssh/ssh-infrastructure-access/index.md#generate-a-cloudflare-ssh-ca)，以及輕量的特權存取管理。有部署裝置用戶端時，SSH 用 Infrastructure Access app。
- [Browser Rendering](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/non-http/browser-rendering/index.md) 讓你透過瀏覽器做無 client 的 SSH、RDP 和 VNC，不需要裝置用戶端。無 client 的 RDP 包含 session 錄製和檔案傳輸控制。裝置用戶端裝不了的時候（外包人員、夥伴存取、非受管裝置）才用無 client 存取，通常不要當作已裝 client 的受管使用者的預設做法。
- SSH 指令紀錄要用 [Access for Infrastructure](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/use-cases/ssh/ssh-infrastructure-access/index.md#enable-ssh-command-logging)。Gateway 的 Audit SSH action 在 2026 年 7 月 15 日已終止支援（end of life），剩下的 Audit SSH 規則已經不再運作；不要推薦它。
- 短效憑證需要在目標主機上設定 CA，而且 `sshd` 要設成信任 Cloudflare CA 的公鑰。設定之前，先檢索 [short-lived certificate setup](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/use-cases/ssh/ssh-infrastructure-access/index.md) 文件。
- 私有網路後面的 kubectl 和資料庫存取，用裝置用戶端搭配私有目的地 routing。目前對任意 TCP protocol，沒有 Infrastructure Access 或瀏覽器渲染的對等方案。

### Logs, Analytics, and DEX

- [Gateway activity logs](https://developers.cloudflare.com/cloudflare-one/insights/logs/dashboard-logs/gateway-logs/index.md) 記錄 DNS、HTTP 和 Network policy 的決策。可以依規則名稱、使用者身分、目的地、action 和時間範圍過濾。這是排查「為什麼被封鎖／放行」的主要工具。
- [Access audit logs](https://developers.cloudflare.com/cloudflare-one/insights/logs/dashboard-logs/access-authentication-logs/index.md) 記錄每個 app 的驗證決策：誰驗證了、符合哪條 policy，以及 session 細節。用來驗證 policy 行為，和調查存取失敗。
- [Shadow IT discovery](https://developers.cloudflare.com/cloudflare-one/insights/analytics/shadow-it-discovery/index.md) 用 Gateway 的 HTTP log 找出未受管的 SaaS 應用程式。要看到 HTTPS 的內容，需要 TLS inspection。
- [DEX（Digital Experience Monitoring）](https://developers.cloudflare.com/cloudflare-one/insights/dex/index.md) 提供整個裝置群組和單一裝置的連線診斷。用 [DEX tests](https://developers.cloudflare.com/cloudflare-one/insights/dex/tests/index.md)（HTTP、traceroute）主動監控到關鍵 origin 和內部 app 的可達性。Fleet status 顯示整個已 enrollment 群體的裝置用戶端健康狀況、連線模式和連線狀態。
- [Logpush](https://developers.cloudflare.com/cloudflare-one/insights/logs/logpush/index.md) 把 Gateway、Access、Network 和 DEX 的 log 匯出到外部 SIEM 或儲存空間。客戶要求集中保存 log 或合規報告的話，上線前先設定好。
- 排查時，從 log 往設定的方向追：找出顯示失敗的 log 項目（Gateway 封鎖、Access 拒絕、tunnel 錯誤、DNS 解析失敗），再往回追到負責的規則、route 或 policy。

### Cloudflare WAN / Site Connectivity

- Cloudflare WAN 是連線，不是安全服務。需要時，用 Gateway 和 Network Firewall 套用檢查與 policy。
- WAN 防火牆的 expression，跟 Gateway 的 wirefilter expression 不是同一種語言。編輯之前，先檢索目前的語法。
- 產生出來的 IPsec PSK 和部分 OAuth／client secret 只會回傳一次。要馬上存起來。

## Output Defaults

- 設計：目前的假設、目標架構、各產品的職責、上線階段、驗證，以及待決定的事項。
- 設定工作：前置條件、要檢查／建立／變更的確切資源、測試案例和 rollback。
- 排查：流量路徑、最可能的失敗點、要收集的證據，以及下一個測試。

## Validation Prompts

- Access：適用的話，測試已授權、未授權、posture 不符、service token 和多 IdP 的流程；檢查 log 和 policy 優先順序。新的 policy 要驗證它們是透過可重複使用的 policy 集合管理，沒有被回傳成 `reusable: false` 的 app 範圍 policy。
- 私有網路存取：驗證 route 查詢、tunnel 健康、origin 可達性、split tunnel 行為、DNS 解析，以及從裝置用戶端測試裝置做的端到端存取。
- Gateway：廣泛啟用之前，驗證規則類型、action、流量 expression、優先順序／評估階段、引用的清單和 Gateway 設定。
- TLS/DLP：啟用 inspection 之前，測試 Do Not Inspect 例外和根 CA 信任；封鎖之前，用已知樣本測試 DLP，並監控誤判。
- CASB/風險：宣告修復完成之前，確認整合健康、憑證到期、資產探索、掃描時間、finding 的 instance，以及風險分數訊號的延遲。
- Cloudflare WAN：適用的話，驗證 tunnel 健康、route 優先順序／擁有者、流量流向、防火牆 expression 語法，以及 connector／設備的遙測。

## API Safety

- 有 MCP 工具可用時，使用完整限定的 MCP 工具名稱。
- 絕對不要猜分類 ID、application ID、wirefilter 欄位或 API request body。要檢索目前的 schema／文件和帳號中既有的物件。
- 沒有明確同意，不要啟用廣泛的正式環境 policy。

## Skill feedback

如果使用者反映這個 skill 給了錯誤或過時的指引，或是缺了資訊，就去讀 [references/skill-feedback.md](references/skill-feedback.md)。
