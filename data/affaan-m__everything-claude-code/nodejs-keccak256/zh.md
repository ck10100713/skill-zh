---
name: nodejs-keccak256
description: 避免 JavaScript 和 TypeScript 裡的以太坊雜湊 bug。Node 的 sha3-256 是 NIST SHA3，不是以太坊的 Keccak-256，會悄悄弄壞 selector、簽章、storage slot 和位址推導。在 JavaScript 或 TypeScript 裡為以太坊做雜湊，或 selector、簽章、storage slot 或推導出來的位址不對時使用。
metadata:
  version: "1.0.0"
  origin: ECC direct-port adaptation
---

# Node.js Keccak-256

以太坊用的是 Keccak-256，不是 Node 的 `crypto.createHash('sha3-256')` 所提供的、經 NIST 標準化的 SHA3 變體。

## When to Use

- 計算以太坊的函式 selector 或事件 topic
- 在 JS/TS 裡建 EIP-712、簽章、Merkle 或 storage-slot 的 helper
- 審查任何直接用 Node crypto 雜湊以太坊資料的程式碼

## How It Works

兩種演算法對同樣的輸入會產生不同的輸出，而 Node 不會警告你。

```javascript
import crypto from 'crypto';
import { keccak256, toUtf8Bytes } from 'ethers';

const data = 'hello';
const nistSha3 = crypto.createHash('sha3-256').update(data).digest('hex');
const keccak = keccak256(toUtf8Bytes(data)).slice(2);

console.log(nistSha3 === keccak); // false
```

## Examples

### ethers v6

```typescript
import { keccak256, toUtf8Bytes, solidityPackedKeccak256, id } from 'ethers';

const hash = keccak256(new Uint8Array([0x01, 0x02]));
const hash2 = keccak256(toUtf8Bytes('hello'));
const topic = id('Transfer(address,address,uint256)');
const packed = solidityPackedKeccak256(
  ['address', 'uint256'],
  ['0x742d35Cc6634C0532925a3b8D4C9B569890FaC1c', 100n],
);
```

### viem

```typescript
import { keccak256, toBytes } from 'viem';

const hash = keccak256(toBytes('hello'));
```

### web3.js

```javascript
const hash = web3.utils.keccak256('hello');
const packed = web3.utils.soliditySha3(
  { type: 'address', value: '0x742d35Cc6634C0532925a3b8D4C9B569890FaC1c' },
  { type: 'uint256', value: '100' },
);
```

### Common patterns

```typescript
import { id, keccak256, AbiCoder } from 'ethers';

const selector = id('transfer(address,uint256)').slice(0, 10);
const typeHash = keccak256(toUtf8Bytes('Transfer(address from,address to,uint256 value)'));

function getMappingSlot(key: string, mappingSlot: number): string {
  return keccak256(
    AbiCoder.defaultAbiCoder().encode(['address', 'uint256'], [key, mappingSlot]),
  );
}
```

### Address from public key

```typescript
import { keccak256 } from 'ethers';

function pubkeyToAddress(pubkeyBytes: Uint8Array): string {
  const hash = keccak256(pubkeyBytes.slice(1));
  return '0x' + hash.slice(-40);
}
```

### Audit your codebase

```bash
grep -rn "createHash.*sha3" --include="*.ts" --include="*.js" --exclude-dir=node_modules .
grep -rn "keccak256" --include="*.ts" --include="*.js" . | grep -v node_modules
```

## Rule

在以太坊的情境裡，絕對不要用 `crypto.createHash('sha3-256')`。要用 `ethers`、`viem`、`web3` 或其他明確的 Keccak 實作所提供、認得 Keccak 的 helper。
