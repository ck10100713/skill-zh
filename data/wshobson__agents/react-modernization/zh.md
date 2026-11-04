---
name: react-modernization
description: 把 React 應用升級到最新版本、從 class component 遷移到 hooks，並採用 concurrent 功能。在現代化 React codebase、遷移到 React Hooks 或升級到最新 React 版本時使用。
---

# React Modernization

精通 React 版本升級、class 遷移到 hooks、採用 concurrent 功能，以及用 codemod 自動轉換。

## When to Use This Skill

- 把 React 應用升級到最新版本
- 把 class component 遷移成使用 hooks 的 function component
- 採用 React 的 concurrent 功能（Suspense、transition）
- 用 codemod 自動重構
- 現代化狀態管理的寫法
- 升級到 TypeScript
- 用 React 18+ 的功能提升效能

## Version Upgrade Path

### React 16 → 17 → 18

**各版本的 Breaking Changes：**

**React 17：**

- 事件委派（event delegation）的改動
- 不再有 event pooling
- Effect cleanup 的時機
- JSX transform（不需要再 import React）

**React 18：**

- 自動 batching
- Concurrent rendering
- Strict Mode 的改動（雙重呼叫）
- 新的 root API
- 伺服器端的 Suspense

## Class to Hooks Migration

### State Management

```javascript
// Before: Class component
class Counter extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      count: 0,
      name: "",
    };
  }

  increment = () => {
    this.setState({ count: this.state.count + 1 });
  };

  render() {
    return (
      <div>
        <p>Count: {this.state.count}</p>
        <button onClick={this.increment}>Increment</button>
      </div>
    );
  }
}

// After: Functional component with hooks
function Counter() {
  const [count, setCount] = useState(0);
  const [name, setName] = useState("");

  const increment = () => {
    setCount(count + 1);
  };

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={increment}>Increment</button>
    </div>
  );
}
```

### Lifecycle Methods to Hooks

```javascript
// Before: Lifecycle methods
class DataFetcher extends React.Component {
  state = { data: null, loading: true };

  componentDidMount() {
    this.fetchData();
  }

  componentDidUpdate(prevProps) {
    if (prevProps.id !== this.props.id) {
      this.fetchData();
    }
  }

  componentWillUnmount() {
    this.cancelRequest();
  }

  fetchData = async () => {
    const data = await fetch(`/api/${this.props.id}`);
    this.setState({ data, loading: false });
  };

  cancelRequest = () => {
    // Cleanup
  };

  render() {
    if (this.state.loading) return <div>Loading...</div>;
    return <div>{this.state.data}</div>;
  }
}

// After: useEffect hook
function DataFetcher({ id }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const fetchData = async () => {
      try {
        const response = await fetch(`/api/${id}`);
        const result = await response.json();

        if (!cancelled) {
          setData(result);
          setLoading(false);
        }
      } catch (error) {
        if (!cancelled) {
          console.error(error);
        }
      }
    };

    fetchData();

    // Cleanup function
    return () => {
      cancelled = true;
    };
  }, [id]); // Re-run when id changes

  if (loading) return <div>Loading...</div>;
  return <div>{data}</div>;
}
```

### Context and HOCs to Hooks

```javascript
// Before: Context consumer and HOC
const ThemeContext = React.createContext();

class ThemedButton extends React.Component {
  static contextType = ThemeContext;

  render() {
    return (
      <button style={{ background: this.context.theme }}>
        {this.props.children}
      </button>
    );
  }
}

// After: useContext hook
function ThemedButton({ children }) {
  const { theme } = useContext(ThemeContext);

  return <button style={{ background: theme }}>{children}</button>;
}

// Before: HOC for data fetching
function withUser(Component) {
  return class extends React.Component {
    state = { user: null };

    componentDidMount() {
      fetchUser().then((user) => this.setState({ user }));
    }

    render() {
      return <Component {...this.props} user={this.state.user} />;
    }
  };
}

// After: Custom hook
function useUser() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetchUser().then(setUser);
  }, []);

  return user;
}

function UserProfile() {
  const user = useUser();
  if (!user) return <div>Loading...</div>;
  return <div>{user.name}</div>;
}
```

## React 18 Concurrent Features

### New Root API

```javascript
// Before: React 17
import ReactDOM from "react-dom";

ReactDOM.render(<App />, document.getElementById("root"));

// After: React 18
import { createRoot } from "react-dom/client";

const root = createRoot(document.getElementById("root"));
root.render(<App />);
```

### Automatic Batching

```javascript
// React 18: All updates are batched
function handleClick() {
  setCount((c) => c + 1);
  setFlag((f) => !f);
  // Only one re-render (batched)
}

// Even in async:
setTimeout(() => {
  setCount((c) => c + 1);
  setFlag((f) => !f);
  // Still batched in React 18!
}, 1000);

// Opt out if needed
import { flushSync } from "react-dom";

flushSync(() => {
  setCount((c) => c + 1);
});
// Re-render happens here
setFlag((f) => !f);
// Another re-render
```

### Transitions

```javascript
import { useState, useTransition } from "react";

function SearchResults() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [isPending, startTransition] = useTransition();

  const handleChange = (e) => {
    // Urgent: Update input immediately
    setQuery(e.target.value);

    // Non-urgent: Update results (can be interrupted)
    startTransition(() => {
      setResults(searchResults(e.target.value));
    });
  };

  return (
    <>
      <input value={query} onChange={handleChange} />
      {isPending && <Spinner />}
      <Results data={results} />
    </>
  );
}
```

### Suspense for Data Fetching

```javascript
import { Suspense } from "react";

// Resource-based data fetching (with React 18)
const resource = fetchProfileData();

function ProfilePage() {
  return (
    <Suspense fallback={<Loading />}>
      <ProfileDetails />
      <Suspense fallback={<Loading />}>
        <ProfileTimeline />
      </Suspense>
    </Suspense>
  );
}

function ProfileDetails() {
  // This will suspend if data not ready
  const user = resource.user.read();
  return <h1>{user.name}</h1>;
}

function ProfileTimeline() {
  const posts = resource.posts.read();
  return <Timeline posts={posts} />;
}
```

## Additional patterns and templates

更多詳細的範本和實作範例放在 `references/details.md`。要看完整的 pattern 清單，就讀那個檔案。
