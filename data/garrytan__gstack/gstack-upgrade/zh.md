---
name: gstack-upgrade
version: 1.1.0
description: 把 gstack 升級到最新版本。
triggers:
  - upgrade gstack
  - update gstack version
  - get latest gstack
allowed-tools:
  - Bash
  - Read
  - Write
  - AskUserQuestion
---
<!-- 由 SKILL.md.tmpl 自動產生，請勿直接編輯 -->
<!-- 重新產生：bun run gen:skill-docs -->

# /gstack-upgrade

把 gstack 升級到最新版本，並顯示有哪些新東西。

## Inline upgrade flow

所有 skill 的 preamble 在偵測到 `UPGRADE_AVAILABLE` 時，都會參照這一節。

### Step 1：問使用者（或自動升級）

先檢查有沒有開啟自動升級：
```bash
_AUTO=""
[ "${GSTACK_AUTO_UPGRADE:-}" = "1" ] && _AUTO="true"
[ -z "$_AUTO" ] && _AUTO=$(~/.claude/skills/gstack/bin/gstack-config get auto_upgrade 2>/dev/null || true)
echo "AUTO_UPGRADE=$_AUTO"
```

**如果 `AUTO_UPGRADE=true` 或 `AUTO_UPGRADE=1`：** 跳過 AskUserQuestion。記錄「Auto-upgrading gstack v{old} → v{new}...」然後直接進 Step 2。如果 setup 失敗，照 Step 4 各安裝類型的復原方式處理：vendored 安裝還原備份；git 安裝則停下來，記下升級前的 commit，不做破壞性的 reset。除非真的還原成功，否則絕對不准說已經還原。

**否則**，用 AskUserQuestion：
- 問題：「gstack **v{new}** 已經推出（你目前是 v{old}）。現在要升級嗎？」
  四個欄位的情況（`UPGRADE_AVAILABLE <old> <old>+<n> <sha>`，代表 main 又往前走了）：改問「gstack main 已經比 v{old} 多了 **{n} 個 commit**（在 {sha}）。現在要升級嗎？」
- 選項：["Yes, upgrade now", "Always keep me up to date", "Not now", "Never ask again"]

**如果選 "Yes, upgrade now"：** 進 Step 2。

**如果選 "Always keep me up to date"：**
```bash
~/.claude/skills/gstack/bin/gstack-config set auto_upgrade true
```
告訴使用者：「Auto-upgrade enabled. Future updates will install automatically.」然後進 Step 2。

**如果選 "Not now"：** 寫入延後提醒的狀態，間隔逐次拉長（第一次延後 = 24 小時，第二次 = 48 小時，第三次以後 = 1 週），然後繼續目前的 skill。不要再提升級的事。
```bash
GSTACK_STATE_ROOT=$(~/.claude/skills/gstack/bin/gstack-paths --get GSTACK_STATE_ROOT); : "${GSTACK_STATE_ROOT:?gstack-paths failed; reinstall with ./setup or /gstack-upgrade}"
_SNOOZE_FILE="$GSTACK_STATE_ROOT/update-snoozed"
_REMOTE_VER="{new}"
_CUR_LEVEL=0
if [ -f "$_SNOOZE_FILE" ]; then
  _SNOOZED_VER=$(awk '{print $(1)}' "$_SNOOZE_FILE")
  if [ "$_SNOOZED_VER" = "$_REMOTE_VER" ]; then
    _CUR_LEVEL=$(awk '{print $(2)}' "$_SNOOZE_FILE")
    case "$_CUR_LEVEL" in *[!0-9]*) _CUR_LEVEL=0 ;; esac
  fi
fi
_NEW_LEVEL=$((_CUR_LEVEL + 1))
[ "$_NEW_LEVEL" -gt 3 ] && _NEW_LEVEL=3
echo "$_REMOTE_VER $_NEW_LEVEL $(date +%s)" > "$_SNOOZE_FILE"
```
注意：`{new}` 是 `UPGRADE_AVAILABLE` 輸出裡的遠端版本，要從更新檢查的結果代入。如果是四個欄位的那種輸出，就用 SHA（第四個欄位）當 `{new}`，這樣 main 一往前走，延後就會結束。

告訴使用者延後多久：「Next reminder in 24h」（依等級也可能是 48h 或 1 week）。小提醒：「Set `auto_upgrade: true` in `~/.gstack/config.yaml` for automatic upgrades.」

**如果選 "Never ask again"：**
```bash
~/.claude/skills/gstack/bin/gstack-config set update_check false
```
告訴使用者：「Update checks disabled. Run `~/.claude/skills/gstack/bin/gstack-config set update_check true` to re-enable.」
繼續目前的 skill。

### Step 2：偵測安裝類型

```bash
if [ -d "$HOME/.claude/skills/gstack/.git" ]; then
  INSTALL_TYPE="global-git"
  INSTALL_DIR="$HOME/.claude/skills/gstack"
elif [ -d "$HOME/.gstack/repos/gstack/.git" ]; then
  INSTALL_TYPE="global-git"
  INSTALL_DIR="$HOME/.gstack/repos/gstack"
elif [ -d ".claude/skills/gstack/.git" ]; then
  INSTALL_TYPE="local-git"
  INSTALL_DIR=".claude/skills/gstack"
elif [ -d ".agents/skills/gstack/.git" ]; then
  INSTALL_TYPE="local-git"
  INSTALL_DIR=".agents/skills/gstack"
elif [ -d ".claude/skills/gstack" ]; then
  INSTALL_TYPE="vendored"
  INSTALL_DIR=".claude/skills/gstack"
elif [ -d "$HOME/.claude/skills/gstack" ]; then
  INSTALL_TYPE="vendored-global"
  INSTALL_DIR="$HOME/.claude/skills/gstack"
elif _SRC=$(~/.claude/skills/gstack/bin/gstack-paths --get GSTACK_STATE_ROOT 2>/dev/null) && _SRC=$(awk -F '\t' '$(1) == "claude" && $(6) != "-" { print $(6); exit }' "$_SRC/installs.tsv" 2>/dev/null) && [ -d "$_SRC/.git" ]; then
  # 安裝登錄檔會記錄 setup 為這個 host 啟用的 checkout（例如 ~/gstack 這個 clone）。
  INSTALL_TYPE="global-git"
  INSTALL_DIR="$_SRC"
else
  echo "ERROR: gstack not found"
  exit 1
fi
INSTALL_DIR=$(cd -- "$INSTALL_DIR" && pwd -P) || { echo "ERROR: cannot enter the gstack install directory" >&2; exit 1; }
echo "Install type: $INSTALL_TYPE at $INSTALL_DIR"
```

上面印出來的安裝類型和絕對路徑，後面每一步都會用到。
明確地把 `INSTALL_TYPE`、`INSTALL_DIR`、`OLD_VERSION`，以及之後的 `UPSTREAM_REF` 和 `NEW_VERSION` 往後帶：每次呼叫工具可能是全新的 shell，所以後面每個區塊開頭都要從捕捉到的輸出重新賦值（例如 `INSTALL_DIR=/abs/path/printed/above`）。不要依賴上一次呼叫的工作目錄或 shell 變數。每個會改檔案的區塊，都要先檢查 `INSTALL_DIR`，如果它沒設、是空的、不存在、讀不了，或不是 gstack 自己的 checkout，就在執行任何 git 指令之前停下來。

### Step 3：記下舊版本

用上面 Step 2 輸出的安裝目錄：

```bash
OLD_VERSION=$(cat "${INSTALL_DIR:?INSTALL_DIR is not set: re-run Step 2 and substitute the printed path}/VERSION" 2>/dev/null || echo "unknown")
echo "OLD_VERSION=$OLD_VERSION"
```

### Step 4：升級

用 Step 2 偵測到的安裝類型和目錄：

**git 安裝**（global-git、local-git）：

先做 fast-forward，透過 `bin/gstack-ff-update`，跟 session-update 自動升級用的是同一份程式：本地修改只要能乾淨 merge，就會跟著更新一起保留；如果修改有衝突（或有 staged 的變更、或有 unmerged 的檔案），會存到 rescue ref，不會留下衝突標記：
```bash
cd -- "${INSTALL_DIR:?INSTALL_DIR is not set: re-run Step 2 and substitute the printed path}" || exit 1
{ [ -f VERSION ] && [ -f setup ] && [ -f bin/gstack-config ] && _p=$(git rev-parse --show-prefix 2>/dev/null) && [ -z "$_p" ] && [ "$(git rev-parse --is-inside-work-tree 2>/dev/null)" = true ]; } || { echo "ERROR: $INSTALL_DIR is not a gstack checkout; nothing was changed. Re-run Step 2." >&2; exit 1; }
git fetch origin
# Channel ref (docs/releases.md): origin/stable for a team install, else origin/main
_CH=$(bash bin/gstack-update-channel.sh --fetch-ref 2>&1) || _CH=origin/main
echo "$_CH"; UPSTREAM_REF=$(printf '%s\n' "$_CH" | tail -1)
echo "UPSTREAM_REF=${UPSTREAM_REF:=origin/main}"
# Same pre-advance check as the auto-updater: the incoming release's Bun floor,
# judged by bash whatever this tool shell is (zsh does not word-split).
HOLD=$(UPSTREAM_REF="$UPSTREAM_REF" bash -c '. bin/gstack-bun-version.sh && gstack_bun_incoming_hold . "$UPSTREAM_REF"' 2>/dev/null) && { case "$HOLD" in bun-version-unreadable*) echo "BUN_VERSION_UNREADABLE: $HOLD; nothing was changed" >&2 ;; *) echo "BUN_TOO_OLD: $HOLD; nothing was changed" >&2 ;; esac; exit 1; }
PRE_UPGRADE_COMMIT=$(git rev-parse HEAD)
echo "PRE_UPGRADE_COMMIT=$PRE_UPGRADE_COMMIT"
# Past the release (by ancestry, or by VERSION in a depth-1 clone): wait for stable; nothing moves back.
if [ "$UPSTREAM_REF" = origin/stable ] && [ "$(git rev-parse origin/stable)" != "$PRE_UPGRADE_COMMIT" ] && ! git merge-base --is-ancestor HEAD origin/stable 2>/dev/null \
  && { git merge-base --is-ancestor origin/stable HEAD 2>/dev/null || [ "$(printf '%s\n%s\n' "$(git show origin/stable:VERSION)" "$(cat VERSION)" | sort -V | tail -1)" = "$(cat VERSION)" ]; }; then echo "AHEAD_OF_STABLE"; exit 0; fi
FF=$(bash bin/gstack-ff-update . "$UPSTREAM_REF"); FF_RC=$?
echo "$FF"
case "$FF_RC" in
  0) if ./setup --refresh-registered; then echo "FF_OK"; else echo "SETUP_FAILED: git update succeeded; stop and inspect setup output (previous commit: $PRE_UPGRADE_COMMIT)" >&2; exit 1; fi ;;
  4) echo "FF_REFUSED" ;;
  *) echo "FF_STOPPED: $FF" >&2; exit 1 ;;
esac
```

Setup 的 `--refresh-registered` 會重新整理這個 checkout 登錄過的每一個安裝（每個 host、全域的和這個專案的），先印出來源，最後以 `Upgrade summary` 收尾，每個安裝一列。把這幾列照原樣轉述給使用者。`failed` 那列代表該 host 保留了原本的安裝；給它重試的指令，絕對不准說每個 host 都已經更新。`skipped` 那列屬於別的 checkout 或專案；把它的指令轉告使用者就好，不要自己跑。

如果輸出以 `FF_OK` 結尾，升級就完成了，直接跳過下面的 fallback。如果它前一行是
`rescued <old> <new> refs/gstack/rescue/<oid> unmerged=<0|1>`，要告訴使用者他們有衝突的本地修改已經存到那裡，並轉述腳本印出的 `Inspect`、`Export` 和 `Delete` 指令（匯出到暫時的 scratch checkout，用 `git apply -3`，絕對不要在安裝目錄裡 `stash apply`；`unmerged=1` 代表這份 rescue 需要手動解衝突）。
遇到 `FF_STOPPED`，停下來並轉述原因：什麼都沒改。
遇到 `AHEAD_OF_STABLE`，停下來：這個 checkout 已經超過最新的 stable release，在下一次發版之前不會有變動（`gstack-config set update_channel main` 會跟著每次 merge 走）。如果上面有 `fetching origin/stable failed` 這行，停下來並轉述；什麼都沒改。
`ff-busy` 代表另一個 gstack 更新正在跑（一分鐘後再試）；
`autostash-unrecoverable` 會指出擋路的東西（release 要新增的某個 untracked 檔案，或另一個 git 指令）；`index-unreadable` 代表這個 checkout 的 index 壞了。
遇到 `BUN_TOO_OLD`，停下來：叫使用者執行 `bun upgrade`，然後再跑一次 /gstack-upgrade。
遇到 `BUN_VERSION_UNREADABLE`，停下來：`bun --version` 沒有印出 gstack 讀得懂的版本，所以 `bun upgrade` 可能也跑不動；叫使用者從 https://bun.sh 重新安裝 Bun（在 Git Bash 或 macOS/Linux 終端機裡用 `curl -fsSL https://bun.sh/install | bash`），確認 `bun --version` 會印出像 1.4.2 這樣的版本，再跑一次 /gstack-upgrade（docs/troubleshooting.md#bun-version-unreadable）。
遇到 `SETUP_FAILED`，停下來；保留使用者的修改，並回報復原用的 commit。git 這條路徑沒有 `.bak`。不要只因為 setup 失敗就進分歧 fallback。只有在 `FF_REFUSED`（有本地 commit 或歷史分岔）時才進去；網路/驗證失敗要停下來修，不是去 reset。

**Fallback（ff-only 被拒絕，有本地 commit 或歷史分岔）。** `git reset
--hard` 會毀掉東西：就算工作目錄是乾淨的，只要有還沒 push 的本地 commit，那些 commit 一樣會不見。要設關卡：

1. 在 `$INSTALL_DIR` 裡跑 `git status --porcelain` 和 `git rev-list "${UPSTREAM_REF:?}"..HEAD --oneline`。
2. 如果兩個**都是空的**，reset 可以證明是安全的，直接跑下面的 fallback 區塊，不用問。
3. 否則用 AskUserQuestion 問（單向門，不可逆），明確列出會被丟掉的東西：每個有改動的檔案、每個還沒 push 的 commit（hash + 標題）。選項：**A)** 丟掉它們並升級（reset），一定要明確回答這個字母；**B)** 中止升級，讓使用者先把自己的工作救出來（有本地 commit 時建議選這個）。回答含糊就絕對不准繼續。

```bash
cd -- "${INSTALL_DIR:?INSTALL_DIR is not set: re-run Step 2 and substitute the printed path}" || exit 1
{ [ -f VERSION ] && [ -f setup ] && [ -f bin/gstack-config ] && _p=$(git rev-parse --show-prefix 2>/dev/null) && [ -z "$_p" ] && [ "$(git rev-parse --is-inside-work-tree 2>/dev/null)" = true ]; } || { echo "ERROR: $INSTALL_DIR is not a gstack checkout; nothing was changed. Re-run Step 2." >&2; exit 1; }
# Regenerable render-footprint dirt (setup re-renders it) never goes into the stash.
git checkout -- 'SKILL.md' '*/SKILL.md' '*/sections/*.md' 2>/dev/null || true
STASH_OUTPUT=$(git stash 2>&1)
git reset --hard "${UPSTREAM_REF:?UPSTREAM_REF is not set: substitute the value Step 4 printed}"
./setup --refresh-registered
```
如果 `$STASH_OUTPUT` 含有 "Saved working directory"，要警告使用者：「Note: local changes were stashed (any modified generated SKILL.md/sections files were discarded first — they regenerate on setup). Run `git stash pop` in the skill directory to restore your own changes.」

**vendored 安裝**（vendored、vendored-global）：
```bash
(cd -- "${INSTALL_DIR:?INSTALL_DIR is not set: re-run Step 2 and substitute the printed path}" && [ -f VERSION ] && [ -f setup ] && [ -f bin/gstack-config ]) || { echo "ERROR: INSTALL_DIR=${INSTALL_DIR:-} is not a gstack install; nothing was changed. Re-run Step 2." >&2; exit 1; }
# 上一次當掉的升級留下的過期 .bak，會讓下面的 mv 把現行安裝「巢狀」塞進它裡面，
# 失敗還原那條路也會「還原」成過期的備份。
# 它也可能是那次當掉之後唯一完好的副本，
# 所以要中止，讓人來檢查，絕對不准默默刪掉。
[ -e "$INSTALL_DIR.bak" ] && { echo "ERROR: stale backup exists at $INSTALL_DIR.bak (from a previous failed upgrade?) — inspect it, salvage/remove it, then re-run." >&2; exit 1; }
TMP_DIR=$(mktemp -d "${TMPDIR:-/tmp}/gstack-upgrade.XXXXXX") || { echo "ERROR: mktemp failed — aborting upgrade (install untouched)." >&2; exit 1; }
git clone --depth 1 https://github.com/garrytan/gstack.git "$TMP_DIR/gstack" || { echo "ERROR: clone failed — aborting upgrade (install untouched)." >&2; rm -rf "$TMP_DIR"; exit 1; }
mv "$INSTALL_DIR" "$INSTALL_DIR.bak" || { rm -rf "$TMP_DIR"; exit 1; }
if mv "$TMP_DIR/gstack" "$INSTALL_DIR"; then
  if (cd "$INSTALL_DIR" && ./setup --refresh-registered); then
    rm -rf "$INSTALL_DIR.bak" "$TMP_DIR"
  else
    rm -rf "$INSTALL_DIR"
    mv "$INSTALL_DIR.bak" "$INSTALL_DIR" || { echo "ERROR: restore failed; backup retained." >&2; exit 1; }
    rm -rf "$TMP_DIR"
    echo "ERROR: setup failed; previous install restored." >&2
    exit 1
  fi
else
  mv "$INSTALL_DIR.bak" "$INSTALL_DIR"
  echo "ERROR: swap failed — previous install restored; upgrade aborted." >&2
  rm -rf "$TMP_DIR"
  exit 1
fi
```

### Step 4.5：處理本地的 vendored 副本

用 Step 2 的安裝目錄。檢查是不是也有一份本地的 vendored 副本，以及有沒有開 team mode：

```bash
_RESOLVED_PRIMARY=$(cd -- "${INSTALL_DIR:?INSTALL_DIR is not set: re-run Step 2 and substitute the printed path}" && pwd -P) || exit 1
_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
LOCAL_GSTACK=""
if [ -n "$_ROOT" ] && [ -d "$_ROOT/.claude/skills/gstack" ]; then
  _RESOLVED_LOCAL=$(cd "$_ROOT/.claude/skills/gstack" && pwd -P)
  if [ "$_RESOLVED_LOCAL" != "$_RESOLVED_PRIMARY" ]; then
    LOCAL_GSTACK="$_ROOT/.claude/skills/gstack"
  fi
fi
_TEAM_MODE=$(~/.claude/skills/gstack/bin/gstack-config get team_mode 2>/dev/null || echo "false")
echo "LOCAL_GSTACK=$LOCAL_GSTACK"
echo "TEAM_MODE=$_TEAM_MODE"
```

**如果 `LOCAL_GSTACK` 不是空的，而且 `TEAM_MODE` 是 `true`：** 移除 vendored 副本。Team mode 以全域安裝作為唯一的 source of truth。

```bash
(cd -- "${LOCAL_GSTACK:?LOCAL_GSTACK is not set: re-run the detection block above and substitute the printed path}" && [ -f VERSION ] && [ -f setup ] && [ -f bin/gstack-config ]) || { echo "ERROR: LOCAL_GSTACK=${LOCAL_GSTACK:-} is not a gstack copy; nothing was changed." >&2; exit 1; }
_ROOT=${LOCAL_GSTACK%/.claude/skills/gstack}
{ [ "$_ROOT" != "$LOCAL_GSTACK" ] && cd -- "${_ROOT:?}" && _p=$(git rev-parse --show-prefix 2>/dev/null) && [ -z "$_p" ] && [ "$(git rev-parse --is-inside-work-tree 2>/dev/null)" = true ]; } || { echo "ERROR: $LOCAL_GSTACK is not the vendored copy at the root of a git repository; nothing was changed." >&2; exit 1; }
git rm -r --cached .claude/skills/gstack/ 2>/dev/null || true
if ! grep -qF '.claude/skills/gstack/' .gitignore 2>/dev/null; then
  echo '.claude/skills/gstack/' >> .gitignore
fi
rm -rf "$LOCAL_GSTACK"
```
告訴使用者：「Removed vendored copy at `$LOCAL_GSTACK` (team mode active — global install is the source of truth). Commit the `.gitignore` change when ready.」

**如果 `LOCAL_GSTACK` 不是空的，而且 `TEAM_MODE` 不是 `true`：** 從剛升級好的主要安裝複製過去更新它（做法跟 README 的 vendored 安裝一樣）：
```bash
(cd -- "${INSTALL_DIR:?INSTALL_DIR is not set: re-run Step 2 and substitute the printed path}" && [ -f VERSION ] && [ -f setup ] && [ -f bin/gstack-config ]) || { echo "ERROR: INSTALL_DIR=${INSTALL_DIR:-} is not a gstack install; nothing was changed." >&2; exit 1; }
(cd -- "${LOCAL_GSTACK:?LOCAL_GSTACK is not set: re-run the detection block above and substitute the printed path}" && [ -f VERSION ] && [ -f setup ] && [ -f bin/gstack-config ]) || { echo "ERROR: LOCAL_GSTACK=${LOCAL_GSTACK:-} is not a gstack copy; nothing was changed." >&2; exit 1; }
[ -e "$LOCAL_GSTACK.bak" ] && { echo "ERROR: stale vendored backup; inspect it before retrying." >&2; exit 1; }
mv "$LOCAL_GSTACK" "$LOCAL_GSTACK.bak" || exit 1
if cp -Rf "$INSTALL_DIR" "$LOCAL_GSTACK" && rm -rf "$LOCAL_GSTACK/.git" && (cd "$LOCAL_GSTACK" && ./setup --refresh-registered); then
  rm -rf "$LOCAL_GSTACK.bak"
  echo "LOCAL_SYNC_OK"
else
  rm -rf "$LOCAL_GSTACK"
  mv "$LOCAL_GSTACK.bak" "$LOCAL_GSTACK" || { echo "ERROR: restore failed; backup retained." >&2; exit 1; }
  echo "ERROR: sync failed; previous vendored copy restored." >&2
  exit 1
fi
```
只有看到 `LOCAL_SYNC_OK` 才告訴使用者：「Also updated vendored copy at `$LOCAL_GSTACK` — commit `.claude/skills/gstack/` when you're ready.」否則就停下來，回報復原的結果；不要繼續跑 migration，也不要宣布成功。

### Step 4.75：執行版本 migration

`./setup` 跑完之後，執行 `gstack-upgrade/migrations/` 裡比舊版本新的 migration（冪等的 `v{VERSION}.sh` 腳本；怎麼新增一個，看 CONTRIBUTING.md）：它們負責修 `./setup` 單靠自己修不了的狀態（過期的 config、孤兒檔案）。

```bash
MIGRATIONS_DIR="${INSTALL_DIR:?INSTALL_DIR is not set: re-run Step 2 and substitute the printed path}/gstack-upgrade/migrations"
: "${OLD_VERSION:?OLD_VERSION is not set: substitute the value Step 3 printed}"
if [ -d "$MIGRATIONS_DIR" ]; then
  for migration in $(find "$MIGRATIONS_DIR" -maxdepth 1 -name 'v*.sh' -type f 2>/dev/null | sort -V); do
    m_ver="$(basename "$migration" .sh | sed 's/^v//')"
    if [ "$OLD_VERSION" != "unknown" ] && [ "$(printf '%s\n%s' "$OLD_VERSION" "$m_ver" | sort -V | head -1)" = "$OLD_VERSION" ] && [ "$OLD_VERSION" != "$m_ver" ]; then
      echo "Running migration $m_ver..."
      # Without GSTACK_INSTALL_DIR a migration that cleans the install assumes ~/.claude/skills/gstack.
      GSTACK_INSTALL_DIR="$INSTALL_DIR" bash "$migration" || echo "  Warning: migration $m_ver had errors (non-fatal)"
    fi
  done
fi
```

### Step 4.8：停掉過期的 daemon（無條件執行）

升級前啟動的 browse daemon 會繼續跑舊的 binary（reset 和 `./setup` 都不會停它），所以這一步一定要跑，用 Step 2 的安裝目錄。

```bash
INSTALL_DIR_PLACEHOLDER="<install dir from Step 2>"
NEW_HASH=$(cat "$INSTALL_DIR_PLACEHOLDER/browse/dist/.version" 2>/dev/null || echo "")
_STATE_FILE="${BROWSE_STATE_FILE:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)/.gstack/browse.json}"
if [ -z "$NEW_HASH" ] || [ ! -f "$_STATE_FILE" ]; then
  echo "DAEMON_CHECK=none (no state file or no fresh build hash)"
else
  DAEMON_PID=$(sed -n 's/.*"pid"[[:space:]]*:[[:space:]]*\([0-9][0-9]*\).*/\1/p' "$_STATE_FILE" | head -1)
  DAEMON_PORT=$(sed -n 's/.*"port"[[:space:]]*:[[:space:]]*\([0-9][0-9]*\).*/\1/p' "$_STATE_FILE" | head -1)
  OLD_HASH=$(sed -n 's/.*"binaryVersion"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$_STATE_FILE" | head -1)
  if [ -z "$DAEMON_PID" ] || ! kill -0 "$DAEMON_PID" 2>/dev/null; then
    echo "DAEMON_CHECK=dead (no live daemon to stop)"
  elif [ "$OLD_HASH" = "$NEW_HASH" ]; then
    echo "DAEMON_CHECK=current (daemon already runs the new binary)"
  elif curl -fsS --max-time 2 "http://127.0.0.1:$DAEMON_PORT/health" 2>/dev/null | grep -q '"status":"healthy"'; then
    echo "DAEMON_CHECK=stale-responsive pid=$DAEMON_PID hash=${OLD_HASH:-unknown} -> $NEW_HASH"
    "$INSTALL_DIR_PLACEHOLDER/browse/dist/browse" stop && echo "DAEMON_STOPPED=yes"
  else
    echo "DAEMON_CHECK=stale-busy pid=$DAEMON_PID hash=${OLD_HASH:-unknown} -> $NEW_HASH"
  fi
fi
```

代入 Step 2 的安裝目錄，然後依 `DAEMON_CHECK` 的結果處理：

1. **`stale-responsive` + `DAEMON_STOPPED=yes`：** 告訴使用者「Stopped the
   old browse daemon (binary {OLD_HASH} → {NEW_HASH}). The next browse command
   starts a fresh daemon on the new binary.」
2. **`stale-busy`：** daemon 跑的是舊 binary，但正在忙，要讓它自己做完，升級期間絕對不准殺掉忙碌中的 daemon。告訴使用者：「A browse daemon
   is still running the pre-upgrade binary ({OLD_HASH} → {NEW_HASH}) but is
   busy right now. When it finishes, stop it with `browse stop` — or force it
   immediately with `browse --force-restart stop` (loses that session's
   tabs/cookies/logins).」
3. **`none` / `dead` / `current`：** 什麼都不用說。

### Step 5：寫入 marker + 清掉 cache

```bash
GSTACK_STATE_ROOT=$(~/.claude/skills/gstack/bin/gstack-paths --get GSTACK_STATE_ROOT); : "${GSTACK_STATE_ROOT:?gstack-paths failed; reinstall with ./setup or /gstack-upgrade}"
mkdir -p "$GSTACK_STATE_ROOT"
echo "$OLD_VERSION" > "$GSTACK_STATE_ROOT"/just-upgraded-from
rm -f "$GSTACK_STATE_ROOT"/last-update-check
rm -f "$GSTACK_STATE_ROOT"/update-snoozed
```

### Step 6：顯示有什麼新東西

讀 `$INSTALL_DIR/CHANGELOG.md`。找出舊版本到新版本之間所有的版本條目。整理成 5 到 7 個重點，依主題分組，使用者看得到的變更放前面。

四個欄位的情況：把 `git -C "$INSTALL_DIR" log --oneline <PRE_UPGRADE_COMMIT>..HEAD` 整理成（最多 7 點）「gstack v{old}, main at {sha}」。

格式：
```
gstack v{new} — upgraded from v{old}!

What's new:
- [bullet 1]
- [bullet 2]
- ...

Happy shipping!
```

### Step 7：繼續

繼續執行使用者原本呼叫的 skill；升級已經完成。

---

## Standalone usage

直接以 `/gstack-upgrade` 呼叫時（不是從 preamble 進來）：

1. 強制重新檢查更新（跳過 cache）：
```bash
~/.claude/skills/gstack/bin/gstack-update-check --force 2>/dev/null || \
.claude/skills/gstack/bin/gstack-update-check --force 2>/dev/null || true
```

2. 如果是 `UPGRADE_AVAILABLE`（三個或四個欄位）：照上面 Step 2 到 6 做。

   如果是 `CHECK_FAILED ...`：讀不到遠端版本，所以更新狀態不明。把那一行秀出來（它會指出失敗的 URL），並告訴使用者檢查失敗了；絕對不准說「已經是最新版本」。停止。

3. 如果沒有輸出（主要安裝已是最新）：檢查有沒有過期的本地 vendored 副本。

跑上面 Step 2 的 bash 區塊，偵測主要安裝的類型和目錄（`INSTALL_TYPE` 和 `INSTALL_DIR`）。然後跑上面 Step 4.5 的偵測 bash 區塊，檢查有沒有本地 vendored 副本（`LOCAL_GSTACK`）和 team mode 的狀態（`TEAM_MODE`）。

**如果 `LOCAL_GSTACK` 是空的**（沒有本地 vendored 副本）：告訴使用者「You're already on the latest version (v{version}).」

**如果 `LOCAL_GSTACK` 不是空的，而且 `TEAM_MODE` 是 `true`：** 用上面 Step 4.5 的 team mode 移除 bash 區塊來移除 vendored 副本。告訴使用者：「Global v{version} is up to date. Removed stale vendored copy (team mode active). Commit the `.gitignore` change when ready.」

**如果 `LOCAL_GSTACK` 不是空的，而且 `TEAM_MODE` 不是 `true`**，比較版本：
```bash
PRIMARY_VER=$(cat "${INSTALL_DIR:?INSTALL_DIR is not set: re-run Step 2 and substitute the printed path}/VERSION" 2>/dev/null || echo "unknown")
LOCAL_VER=$(cat "${LOCAL_GSTACK:?LOCAL_GSTACK is not set: re-run the Step 4.5 detection block}/VERSION" 2>/dev/null || echo "unknown")
echo "PRIMARY=$PRIMARY_VER LOCAL=$LOCAL_VER"
```

**如果版本不同：** 照上面 Step 4.5 的同步 bash 區塊，從主要安裝更新本地副本。告訴使用者：「Global v{PRIMARY_VER} is up to date. Updated local vendored copy from v{LOCAL_VER} → v{PRIMARY_VER}. Commit `.claude/skills/gstack/` when you're ready.」

**如果版本一樣：** 告訴使用者「You're on the latest version (v{PRIMARY_VER}). Global and local vendored copy are both up to date.」
