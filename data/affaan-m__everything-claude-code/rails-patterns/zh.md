---
name: rails-patterns
description: 適用於 Rails 7.1+ 和 8.x 應用程式的 Ruby on Rails 框架模式。涵蓋目錄約定、搭配 service object 的瘦 controller、form object、query object、道地的 ActiveRecord、背景 job、ViewComponent、Hotwire，以及 Rails 8 的 Solid 全家桶。建置或 review Rails 應用、controller、model、service、job 或 view 時使用。
origin: community
---

# Rails 模式

現代 Ruby on Rails 應用程式（Rails 7.1+ 和 8.x）的框架模式。Rails 本來就很有主見，這些是社群收斂出來、能讓應用程式在超過 50 個 model 之後仍好維護的模式。這個 skill 講的是「怎麼做」。至於「做什麼」和「何時用」（該選哪個模式的決策），請看 Ruby patterns rules：這個 repo 裡的 `rules/ruby/patterns.md`，安裝後位於 `rules/ecc/ruby/patterns.md`。

## 何時啟用

- 建置 Rails 應用程式（全端、純 API 或混合）
- Review 動到 `app/` 或 `config/` 的 PR
- 產生 model、controller、service 或 job
- controller action 長到超過約 10 行
- model 檔案長到超過約 200 行
- ActiveRecord 查詢開始出現在 controller 或 view 裡

## 核心概念

### 目錄約定

Rails 應用程式遵循可預期的結構。要新增目錄就刻意新增，不要隨便加。

```
app/
  models/         ActiveRecord models. Persistence and domain logic close to the data.
  controllers/    HTTP request handling. Thin orchestration only.
  views/          ERB templates. No business logic.
  components/     ViewComponent classes. View logic that needs tests.
  services/       Service objects. Multi-step business operations.
  forms/          Form objects. Complex form handling across multiple models.
  queries/        Query objects. Reusable, composable ActiveRecord queries.
  jobs/           Background jobs. Async work via Solid Queue, Sidekiq, or GoodJob.
  mailers/        ActionMailer classes.
  helpers/        View helpers. Tiny presentational logic only.
  policies/       Authorization policies (if using Pundit). Optional.
  channels/       ActionCable channels for WebSocket work.
```

避免 `app/lib/`、`app/utils/`、`app/managers/`。如果某樣東西放不進上面的目錄，通常是設計要重想，而不是新增目錄。真正通用的程式碼放在 `lib/`。

### 瘦 controller

Controller 接收請求、委派給對的物件、回傳回應。商業邏輯放在別處。（依 Ruby patterns rules，當 controller 開始承擔多個職責時，就抽成 service object。）

### Service object

預設用在不只動到單一 model 儲存的商業操作。這些慣例能讓它們保持一致：

- 依領域命名空間（`Invoices::Create`），不要用後綴（`InvoiceCreator`）。
- 類別方法 `.call` 委派給實例的 `#call`。
- 回傳 Result 物件，不要回傳 boolean 或單純的 record，這樣呼叫端才能依成功、錯誤和受影響的 record 分支處理。
- 多筆 record 的寫入要包在 transaction 裡。
- 每個 service 只做一件事（`Invoices::Create`、`Invoices::MarkPaid`），絕對不要有 `Invoices::Manager`。

### Form object

當表單跨多個 model，或有欄位對應不到資料表欄位時，用 form object，不要用 nested attributes，也不要在錯的 model 上加虛擬屬性。它對 view 來說表現得像 model（`form_with model: @form`），同時乾淨地組合各個 record。

### Query object

ActiveRecord 查詢如果會跨 controller 或 service 重用，或複雜到不適合寫成 scope，就抽成 query object，並讓它接受 scope 當輸入，這樣才能組合。經驗法則：scope 串了超過三個條件，或開始接參數，就該變成 query object。

### 背景 job

慢的東西都丟出去。（依 Ruby patterns rules，全新的 Rails 8 專案、吞吐量不大就用 Solid Queue；需要成熟的可觀測性、高吞吐量或已有 Redis 時用 Sidekiq。）不管用哪個 adapter：傳 ID 不傳 record、讓 `perform` 具冪等性、明確設定 `retry_on`／`discard_on`。

### 用 ViewComponent 取代 partial

view 邏輯如果有條件式渲染、參數超過兩個，或在超過三個地方重用，就優先用 ViewComponent。Component 可以單獨測試，而且介面一目了然；條件邏輯很深的 partial 會變成技術債。

### Hotwire：Turbo 與 Stimulus

Rails 預設的前端技術組合。（依 Ruby patterns rules，伺服器渲染的應用優先用 Hotwire；互動複雜度大到值得開出 client 這一塊時，才去用 React/Vue。）Turbo Frames 做局部頁面更新，Turbo Streams 做伺服器驅動的更新，Stimulus 負責貼著 markup 的小型 client 端行為。

### Rails 8 的 Solid 全家桶

Rails 8 內建以資料庫為底的預設值，這些以前都需要 Redis：Solid Queue（job）、Solid Cache（快取）、Solid Cable（ActionCable）。代價是資料庫負載變多，換來少一個基礎設施元件；吞吐量不大時很適合，規模大了還是 Redis 比較強。Kamal 是預設的 Docker 部署工具。

## 程式碼範例

### 搭配 service object 的瘦 controller

```ruby
# Bad: 商業邏輯塞在 controller
class InvoicesController < ApplicationController
  def create
    @invoice = Invoice.new(invoice_params)
    @invoice.user = current_user
    @invoice.line_items.build(invoice_params[:line_items])
    @invoice.tax_total = TaxCalculator.new(@invoice).calculate
    @invoice.total = @invoice.line_items.sum(&:amount) + @invoice.tax_total

    if @invoice.save
      InvoiceMailer.created(@invoice).deliver_later
      AccountingExportJob.perform_later(@invoice.id)
      redirect_to @invoice, notice: "Invoice created"
    else
      render :new
    end
  end
end

# Good: controller 負責調度，service 負責做事
class InvoicesController < ApplicationController
  def create
    result = Invoices::Create.call(params: invoice_params, user: current_user)

    if result.success?
      redirect_to result.invoice, notice: "Invoice created"
    else
      @invoice = result.invoice
      render :new, status: :unprocessable_entity
    end
  end
end
```

### Service object

```ruby
# app/services/invoices/create.rb
module Invoices
  class Create
    # 用 Struct 讓這段在 Rails 7.1 支援的每個 Ruby 版本上都能跑。
    # Ruby 3.2+ 的話，`Data.define(:success?, :invoice, :errors)` 是更
    # 簡潔的不可變替代方案。
    Result = Struct.new(:success, :invoice, :errors, keyword_init: true) do
      def success?
        success
      end
    end

    def self.call(params:, user:)
      new(params: params, user: user).call
    end

    def initialize(params:, user:)
      @params = params
      @user = user
    end

    def call
      invoice = build_invoice
      ApplicationRecord.transaction do
        invoice.save!
      end
      begin
        send_notifications(invoice)
      rescue StandardError => e
        Rails.logger.error("Notification dispatch failed for invoice #{invoice.id}: #{e.message}")
      end
      Result.new(success: true, invoice: invoice, errors: nil)
    rescue ActiveRecord::RecordInvalid => e
      Result.new(success: false, invoice: e.record, errors: e.record.errors)
    end

    private

    attr_reader :params, :user

    def build_invoice
      invoice = user.invoices.new(params.except(:line_items))
      invoice.line_items.build(params[:line_items])
      invoice.tax_total = TaxCalculator.call(invoice)
      invoice.total = invoice.line_items.sum(&:amount) + invoice.tax_total
      invoice
    end

    def send_notifications(invoice)
      InvoiceMailer.created(invoice).deliver_later
      AccountingExportJob.perform_later(invoice.id)
    end
  end
end
```

### Form object

```ruby
# app/forms/signup_form.rb
class SignupForm
  include ActiveModel::Model
  include ActiveModel::Attributes

  attribute :email, :string
  attribute :password, :string
  attribute :company_name, :string
  attribute :terms_accepted, :boolean

  validates :email, presence: true, format: URI::MailTo::EMAIL_REGEXP
  validates :password, presence: true, length: { minimum: 12 }
  validates :company_name, presence: true
  validates :terms_accepted, acceptance: true

  attr_reader :user, :company

  def save
    return false unless valid?

    ApplicationRecord.transaction do
      @company = Company.create!(name: company_name)
      @user = @company.users.create!(email: email, password: password, role: :owner)
    end
    true
  rescue ActiveRecord::RecordInvalid => e
    errors.merge!(e.record.errors)
    false
  end
end
```

### Query object

```ruby
# app/queries/invoices/overdue.rb
module Invoices
  class Overdue
    def self.call(scope: Invoice.all, as_of: Time.current)
      new(scope: scope, as_of: as_of).call
    end

    def initialize(scope:, as_of:)
      @scope = scope
      @as_of = as_of
    end

    def call
      scope
        .where(status: :sent)
        .where(due_date: ..as_of)
        .where.not(id: paid_invoice_ids)
        .includes(:customer, :line_items)
    end

    private

    attr_reader :scope, :as_of

    def paid_invoice_ids
      Payment.where(created_at: ..as_of).pluck(:invoice_id)
    end
  end
end
```

Query object 接受 scope，所以可以組合：`Invoices::Overdue.call(scope: current_user.invoices)`。

### 預防 N+1

```ruby
# Bad: view 裡呼叫 post.author.name 造成 N+1
@posts = Post.published

# Good: eager load
@posts = Post.published.includes(:author)
```

`includes` 讓 Rails 自己選 preload 或 eager_load。要拆成獨立查詢就強制用 `preload`，要在 association 上過濾、用 JOIN 就用 `eager_load`。從 Rails 6.1 起，`strict_loading` 會在意外的 lazy load 時丟出錯誤。

### Counter cache

```ruby
class Comment < ApplicationRecord
  belongs_to :post, counter_cache: true
end
```

```ruby
add_column :posts, :comments_count, :integer, default: 0, null: false
```

`post.comments_count` 變成讀欄位，而不是 `COUNT(*)`。這個範例
假設是新資料表；對已經有資料的資料表加 counter cache，需要
回填資料，這裡不談。

### 背景 job 的形狀

傳 record 的 ID，不要傳 record。重試讓投遞變成至少一次，所以任何會呼叫
外部服務的 job 都必須具冪等性，否則遠端呼叫成功之後如果發生暫時性失敗，
下一次嘗試就會重複產生效果。

```ruby
class AccountingExportJob < ApplicationJob
  queue_as :exports

  retry_on AccountingApi::TransientError, wait: :polynomially_longer, attempts: 5
  discard_on AccountingApi::PermanentError

  def perform(invoice_id)
    invoice = Invoice.find(invoice_id)
    export = AccountingExport.create_or_find_by!(
      invoice: invoice,
      idempotency_key: "invoice-export-#{invoice.id}-#{invoice.updated_at.to_i}"
    )
    return if export.completed_at?

    receipt = AccountingApi.export(invoice, idempotency_key: export.idempotency_key)
    export.update!(completed_at: Time.current, external_id: receipt.id)
  end
end
```

```ruby
add_index :accounting_exports, :idempotency_key, unique: true
```

unique index 才是讓這件事安全的關鍵：兩次嘗試競爭時，資料庫會拒絕
第二次 insert，Active Record 在呼叫內部解決衝突，回傳
已存在的那一列。這不需要任何 job 層級的重試，上面的 `retry_on` 只涵蓋
`AccountingApi::TransientError`。這個 guard
涵蓋遠端呼叫之前的時間窗；把 `idempotency_key` 一路傳給 API，
則涵蓋之後的時間窗，所以就算在 API 呼叫和 `update!` 之間當掉，
最終也只會產生一次匯出。

### ViewComponent

```ruby
# app/components/invoice_status_badge_component.rb
class InvoiceStatusBadgeComponent < ViewComponent::Base
  STATUS_CLASSES = {
    draft: "bg-gray-100 text-gray-800",
    sent: "bg-blue-100 text-blue-800",
    paid: "bg-green-100 text-green-800",
    overdue: "bg-red-100 text-red-800"
  }.freeze

  def initialize(invoice:)
    @invoice = invoice
  end

  def call
    tag.span(@invoice.status.humanize, class: "rounded-full px-2 py-1 text-sm #{status_class}")
  end

  private

  def status_class
    STATUS_CLASSES.fetch(@invoice.status.to_sym, "bg-gray-100")
  end
end
```

```erb
<%= render InvoiceStatusBadgeComponent.new(invoice: @invoice) %>
```

### Hotwire

```erb
<%# Turbo Frame: clicking Edit replaces only this frame %>
<%= turbo_frame_tag "invoice_#{@invoice.id}" do %>
  <div class="invoice">
    <%= link_to "Edit", edit_invoice_path(@invoice) %>
  </div>
<% end %>
```

```erb
<%# Turbo Stream: app/views/comments/create.turbo_stream.erb %>
<%= turbo_stream.append "comments", @comment %>
<%= turbo_stream.update "comment_form", partial: "form", locals: { comment: Comment.new } %>
```

```javascript
// app/javascript/controllers/copy_to_clipboard_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["source"]

  copy() {
    navigator.clipboard.writeText(this.sourceTarget.value)
  }
}
```

### 可接受 vs 不可接受的 callback

```ruby
# Acceptable: 單純的資料正規化
class User < ApplicationRecord
  before_validation :normalize_email

  private

  def normalize_email
    self.email = email.to_s.downcase.strip
  end
end

# 改放到 service：callback 裡藏了副作用
# class User < ApplicationRecord
#   after_create :send_welcome_email  # 很難選擇不執行，也很難測試
# end
```

### 好的 concern vs 壞的 concern

```ruby
# Good: 真正橫切、可跨不相關的 model 重用
# app/models/concerns/soft_deletable.rb
module SoftDeletable
  extend ActiveSupport::Concern

  included do
    scope :active, -> { where(deleted_at: nil) }
    scope :deleted, -> { where.not(deleted_at: nil) }
  end

  def soft_delete! = update!(deleted_at: Time.current)
  def restore! = update!(deleted_at: nil)
end

# Bad: 「concern」只給一個 model 用，裝的是屬於它自己的邏輯
# app/models/concerns/invoice_calculations.rb
module InvoiceCalculations
  extend ActiveSupport::Concern

  def calculate_total
    line_items.sum(&:amount) + tax_total
  end
end
# 只有 Invoice 會 include 這個。它不是橫切的；這是 Invoice 自己的邏輯，
# 藏在 module 裡，只為了讓 model 看起來「很瘦」。把它放回 Invoice。
```

只有一個類別用的 concern 只是在搬程式碼，它屬於那個類別。concern 應該至少能在兩個不相關的 model 之間重用。

## 反模式

### 上帝 controller

任何超過約 80 行的 controller 都做太多事了。把 action 拆到不同 controller，或抽成 service。

### 有 30 個以上方法的肥 model

Model 應該只認得自己的資料。去調度其他 model、發通知或協調工作流程的方法，屬於 service。

### Callback 串

`after_save :update_cache, :send_notifications, :enqueue_export` 就是除錯惡夢的開端。把它們搬進 service，讓 service 明確地依序執行。

### 複雜表單用 nested attributes

`accepts_nested_attributes_for` 用在簡單情況沒問題。需要條件式驗證或跨 model 邏輯時，用 form object。

### 重要 model 上的 default scope

`default_scope { where(deleted: false) }` 會默默把 record 從應用程式裡的每個查詢排除，包括客服和除錯時需要的那些。優先用明確命名的 scope。

### 用資料庫概念命名的 model

`UserRole`、`OrderStatus`、`InvoiceState` 通常是 enum 的候選，不是 model。

### 還沒想到 Hotwire 就先用 JS 框架

如果頁面是伺服器渲染、只有偶爾的互動，Hotwire 出貨更快。React/Vue 留給真正 SPA 形狀的應用。

## 最佳實踐

- controller 保持精簡，把商業邏輯推進 service。
- Service 回傳 Result 物件，讓呼叫端依結果分支，不要依例外分支。
- 多筆 record 寫入要包在 transaction 裡；通知／副作用失敗時只記 log，不要弄壞主要的寫入。
- 傳 ID 給 job，讓 `perform` 具冪等性，明確設定 retry／discard。
- 預設就 eager load；意外的 N+1 當成 bug，不要當成小困擾。
- concern 只用在至少兩個不相關 model 共享的行為。
- 伺服器渲染的應用，先考慮 Hotwire，再考慮 client 端框架。

## 相關 skill

- `backend-patterns`：service 邊界與 adapter 模式（Ruby patterns rules 有引用）
- Ruby patterns rules（`rules/ruby/patterns.md`，安裝後位於 `rules/ecc/ruby/patterns.md`）：這個 skill 所實作的決策與何時使用的指引
