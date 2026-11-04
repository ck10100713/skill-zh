---
name: frontend-a11y
description: React 和 Next.js 的無障礙（accessibility）模式，包含語意化 HTML、ARIA 屬性、表單標籤、鍵盤導覽、焦點管理和螢幕閱讀器支援。建構或 review 表單、modal、dropdown、tooltip 或 tab、修正 a11y lint 或 code review 發現的問題，或是接線鍵盤導覽與焦點管理時使用。
metadata:
  origin: community
---

# Frontend Accessibility Patterns

React 和 Next.js 實用的無障礙模式。涵蓋 code review 最常被標出來的問題：缺少表單標籤、ARIA 用法不正確、用非語意元素當互動元件，以及壞掉的鍵盤導覽。

## When to Activate

- 建構或 review 表單元件（`<input>`、`<select>`、`<textarea>`）
- 建立互動元素（modal、dropdown、tooltip、tab）
- 在 `<div>` 或 `<span>` 上加 `onClick`
- 在任何元素上加 `aria-*` 屬性
- 實作鍵盤導覽或焦點管理
- 收到 code review 工具（CodeRabbit、ESLint a11y）的無障礙回饋
- 建構必須支援螢幕閱讀器的元件

## Form Accessibility

缺少 `htmlFor` / `id` 配對，以及沒有連結的錯誤訊息，是 code review 最常被標出來的問題。

### Label Connection

```tsx
// BAD：label 跟 input 沒有連結，螢幕閱讀器無法把兩者關聯起來
<label>Email</label>
<input type="email" />

// GOOD：htmlFor 對應 input 的 id
<label htmlFor="email">Email</label>
<input id="email" type="email" />
```

### Required Fields

```tsx
// BAD：只有視覺上的星號，螢幕閱讀器完全收不到訊息
<label htmlFor="email">Email *</label>
<input id="email" type="email" />

// GOOD：required 啟用瀏覽器原生驗證；aria-required 則是告訴螢幕閱讀器
<label htmlFor="email">
  Email <span aria-hidden="true">*</span>
</label>
<input id="email" type="email" required aria-required="true" />
```

### Error Messages

```tsx
// BAD：錯誤文字在視覺上存在，但沒有連到 input
<input id="email" type="email" />
<span className="error">Invalid email address</span>

// GOOD：aria-describedby 把 input 連到它的錯誤訊息
// aria-invalid 向螢幕閱讀器表明目前是無效狀態
<input
  id="email"
  type="email"
  aria-describedby="email-error"
  aria-invalid={!!error}
/>
{error && (
  <span id="email-error" role="alert">
    {error}
  </span>
)}
```

### Complete Accessible Form

```tsx
interface LoginFormProps {
  onSubmit: (email: string, password: string) => void;
}

export function LoginForm({ onSubmit }: LoginFormProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<{ email?: string; password?: string }>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const newErrors: typeof errors = {};
    if (!email) newErrors.email = 'Email is required';
    if (!password) newErrors.password = 'Password is required';
    if (Object.keys(newErrors).length) {
      setErrors(newErrors);
      return;
    }
    onSubmit(email, password);
  };

  return (
    <form onSubmit={handleSubmit} noValidate>
      <div>
        <label htmlFor="email">
          Email <span aria-hidden="true">*</span>
        </label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          aria-required="true"
          aria-describedby={errors.email ? 'email-error' : undefined}
          aria-invalid={!!errors.email}
          autoComplete="email"
        />
        {errors.email && (
          <span id="email-error" role="alert">
            {errors.email}
          </span>
        )}
      </div>

      <div>
        <label htmlFor="password">
          Password <span aria-hidden="true">*</span>
        </label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          aria-required="true"
          aria-describedby={errors.password ? 'password-error' : undefined}
          aria-invalid={!!errors.password}
          autoComplete="current-password"
        />
        {errors.password && (
          <span id="password-error" role="alert">
            {errors.password}
          </span>
        )}
      </div>

      <button type="submit">Log in</button>
    </form>
  );
}
```

## Semantic HTML

用符合意圖的元素。螢幕閱讀器和鍵盤使用者都靠原生語意在運作。

```tsx
// BAD：div 沒有 role、不支援鍵盤、也沒有無障礙名稱
<div onClick={handleClick}>Submit</div>

// GOOD：button 能取得焦點、按 Enter/Space 會觸發、並且會被唸成「按鈕」
<button type="button" onClick={handleClick}>Submit</button>
```

```tsx
// BAD：非語意的導覽
<div onClick={() => navigate('/home')}>Home</div>

// GOOD：anchor 支援右鍵、中鍵和鍵盤導覽
<a href="/home">Home</a>
```

```tsx
// BAD：標題層級跳級（h1 直接跳到 h4）
<h1>Dashboard</h1>
<h4>Recent Activity</h4>

// GOOD：標題層級循序
<h1>Dashboard</h1>
<h2>Recent Activity</h2>
```

## ARIA Attributes

原生 HTML 語意不夠用時才用 ARIA。錯誤的 ARIA 比完全沒有 ARIA 更糟。

### aria-label vs aria-labelledby

```tsx
// aria-label：行內字串標籤，沒有可見的標籤文字時使用
<button aria-label="Close modal">
  <XIcon />
</button>

// aria-labelledby：參照另一個元素的文字，已有可見標籤時使用
<section aria-labelledby="section-title">
  <h2 id="section-title">Recent Orders</h2>
  {/* content */}
</section>
```

### aria-describedby

```tsx
// 在標籤之外提供補充說明
<button
  aria-describedby="delete-warning"
  onClick={handleDelete}
> Delete account
</button>
<p id="delete-warning">This action cannot be undone.</p>
```

### aria-live for Dynamic Content

```tsx
// 用 aria-live 播報不用重新載入頁面就會更新的內容
// polite：等使用者做完目前的動作再播報
// assertive：立刻打斷，只用在緊急的錯誤

export function StatusMessage({ message, isError }: { message: string; isError?: boolean }) {
  return (
    <div role="status" aria-live={isError ? 'assertive' : 'polite'} aria-atomic="true">
      {message}
    </div>
  );
}
```

### aria-expanded and aria-controls

```tsx
export function Accordion({ title, children }: { title: string; children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);
  const contentId = useId();

  return (
    <div>
      <button aria-expanded={isOpen} aria-controls={contentId} onClick={() => setIsOpen(prev => !prev)}>
        {title}
      </button>
      <div id={contentId} hidden={!isOpen}>
        {children}
      </div>
    </div>
  );
}
```

## Keyboard Navigation

每個互動元素都必須能只靠鍵盤就到得了、操作得了。

### Custom Dropdown

```tsx
export function Dropdown({ options, onSelect }: { options: string[]; onSelect: (value: string) => void }) {
  const [isOpen, setIsOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(0);
  const listId = useId();

  if (!options.length) return null;

  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setActiveIndex(i => Math.min(i + 1, options.length - 1));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setActiveIndex(i => Math.max(i - 1, 0));
        break;
      case 'Enter':
      case ' ':
        e.preventDefault();
        if (isOpen) onSelect(options[activeIndex]);
        setIsOpen(prev => !prev);
        break;
      case 'Escape':
        setIsOpen(false);
        break;
    }
  };

  return (
    <div
      role="combobox"
      aria-expanded={isOpen}
      aria-haspopup="listbox"
      aria-controls={listId}
      tabIndex={0}
      onKeyDown={handleKeyDown}
      onClick={() => setIsOpen(prev => !prev)}
    >
      <span>{options[activeIndex]}</span>
      {isOpen && (
        <ul id={listId} role="listbox">
          {options.map((option, index) => (
            <li
              key={option}
              role="option"
              aria-selected={index === activeIndex}
              onClick={() => {
                onSelect(option);
                setIsOpen(false);
              }}
            >
              {option}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

## Focus Management

UI 狀態改變時，焦點必須合乎邏輯地移動，modal 和路由切換尤其如此。

### Modal Focus Restoration

> 這個範例只涵蓋初始焦點和焦點還原。如果要完整的 focus trap（Tab/Shift+Tab 在 modal 內循環），請用 [`focus-trap-react`](https://github.com/focus-trap/focus-trap-react) 這類函式庫，它會處理動態內容和巢狀 portal 這些邊界情況。

```tsx
export function Modal({ isOpen, onClose, title, children }: { isOpen: boolean; onClose: () => void; title: string; children: React.ReactNode }) {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (isOpen) {
      // 記住目前有焦點的元素，並把焦點移進 modal
      previousFocusRef.current = document.activeElement as HTMLElement;
      modalRef.current?.focus();
    } else {
      // 把焦點還給當初打開 modal 的那個元素
      previousFocusRef.current?.focus();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div ref={modalRef} role="dialog" aria-modal="true" aria-labelledby="modal-title" tabIndex={-1} onKeyDown={e => e.key === 'Escape' && onClose()}>
      <h2 id="modal-title">{title}</h2>
      {children}
      <button onClick={onClose}>Close</button>
    </div>
  );
}
```

## Images and Icons

```tsx
// BAD：裝飾性圖示會被當成沒有標籤的圖片唸出來
<img src="/icon.svg" />

// GOOD：裝飾性圖片對螢幕閱讀器隱藏
<img src="/decoration.png" alt="" aria-hidden="true" />

// GOOD：有意義的圖片搭配具描述性的 alt 文字
<img src="/chart.png" alt="Monthly revenue increased 23% from January to March" />

// GOOD：圖示按鈕搭配無障礙標籤
<button aria-label="Delete item">
  <TrashIcon aria-hidden="true" />
</button>
```

## Reduced Motion

尊重在作業系統設定裡要求減少動態效果的使用者。

```tsx
export function useReducedMotion(): boolean {
  const [prefersReduced, setPrefersReduced] = useState(false);

  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReduced(mq.matches);
    const handler = (e: MediaQueryListEvent) => setPrefersReduced(e.matches);
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, []);

  return prefersReduced;
}

// 用法
export function AnimatedCard({ children }: { children: React.ReactNode }) {
  const reduceMotion = useReducedMotion();

  return (
    <div
      style={{
        transition: reduceMotion ? 'none' : 'transform 300ms ease'
      }}
    >
      {children}
    </div>
  );
}
```

## Anti-Patterns

```tsx
// BAD：非互動元素上的 onClick，沒有鍵盤支援
<div onClick={handleClick}>Click me</div>

// BAD：在沒有 role 的 div 上加 aria-label
<div aria-label="Navigation">...</div>

// BAD：拿 placeholder 當 label 用
<input placeholder="Enter your email" />

// BAD：正數的 tabIndex 會讓 Tab 順序無法預測
<button tabIndex={3}>Submit</button>

// BAD：在可取得焦點的元素上加 aria-hidden，鍵盤使用者會被困住
<button aria-hidden="true">Open</button>

// BAD：div 上加 role="button" 卻沒有鍵盤處理
<div role="button" onClick={handleClick}>Submit</div>
// 缺少：tabIndex={0}，以及處理 Enter/Space 的 onKeyDown
```

## Checklist

提交任何互動元件去 review 之前：

- [ ] 每個 `<input>`、`<select>` 和 `<textarea>` 都透過 `htmlFor`/`id` 連到一個 `<label>`
- [ ] 錯誤訊息用 `aria-describedby` 連結，並標上 `role="alert"`
- [ ] 沒有在 `<div>` 或 `<span>` 上放 `onClick` 卻缺少 `role`、`tabIndex` 和 `onKeyDown`
- [ ] 只有圖示的按鈕有 `aria-label`
- [ ] 裝飾性圖片用 `alt=""` 和 `aria-hidden="true"`
- [ ] modal 關閉時會還原焦點（要完整的 focus trap 和 Tab/Shift+Tab 循環，請用 `focus-trap-react` 這類函式庫）
- [ ] 動態內容更新有用 `aria-live`
- [ ] 動畫有尊重 `prefers-reduced-motion`

## Related Skills

- `frontend-patterns`：一般的 React 元件與狀態模式
- `design-system`：design token 與元件一致性
- `motion-foundations` 和 `motion-patterns`：考量無障礙的動畫模式
