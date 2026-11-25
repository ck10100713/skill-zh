"""從 data/ 產生整個靜態網站。用法：python3 build.py

data/<來源>/<skill>/
  en.md      英文原文（原文就是中文的 skill 沒有這個檔）
  zh.md      中文翻譯，或中文原文
  meta.json  {skill, author, repo, source, license, category, summary}
             category 可以是字串或陣列（一份掛多個分類）
收錄日期取自 git：meta.json 第一次被 commit 的那天，還沒 commit 的算今天。
"""
import datetime, html, json, os, shutil, subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
TITLE = 'Skill 寫法圖鑑'
DESC = '收集各家 Claude Code skill，中文翻譯和英文原文並排對照'
CATEGORIES = [
    '規劃與釐清', '架構與重構', '測試與驗證', '除錯與調查', 'Code Review', '設計與前端', '寫作與文件',
    '部署與發布', '安全護欄', '瀏覽器自動化', 'Office 與 PDF', 'Cloudflare 平台', '雲端與基礎設施',
    '資料與分析', '行銷與 SEO', '商業與營運', '金融與投資', '遊戲開發', '個人與生活', 'Agent 與工作流', '設定與維護',
]
OUT_DIRS = ['s', 'c', 'r']
e = html.escape


def added_dates():
    # git log 由新到舊，一路覆蓋下去留下的就是最早那次
    out = subprocess.run(['git', 'log', '--diff-filter=A', '--format=%cs', '--name-only', '--', 'data'],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout
    dates, cur = {}, None
    for line in out.splitlines():
        if len(line) == 10 and line[4] == '-':
            cur = line
        elif line.endswith('/meta.json'):
            dates[line] = cur
    return dates


def load():
    skills, dates, today = [], added_dates(), datetime.date.today().isoformat()
    for src in sorted(os.listdir(f'{ROOT}/data')):
        for name in sorted(os.listdir(f'{ROOT}/data/{src}')):
            d = f'{ROOT}/data/{src}/{name}'
            meta = json.load(open(f'{d}/meta.json'))
            cats = meta['category'] if isinstance(meta['category'], list) else [meta['category']]
            assert cats and all(c in CATEGORIES for c in cats), (d, cats)
            meta.update(src=src, name=name, url=f's/{src}/{name}.html', cats=cats,
                        added=dates.get(f'data/{src}/{name}/meta.json', today),
                        zh=open(f'{d}/zh.md').read(),
                        en=open(f'{d}/en.md').read() if os.path.exists(f'{d}/en.md') else None)
            skills.append(meta)
    return skills


def shell(title, body, depth, desc=DESC):
    up = '../' * depth
    return f'''<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="stylesheet" href="{up}assets/style.css">
</head>
<body>
<input type="checkbox" id="nav-toggle" hidden>
<header class="top">
  <a class="brand" href="{up}index.html">{TITLE}</a>
  <label for="nav-toggle" class="burger" aria-label="開關選單">☰</label>
</header>
<div class="shell">
  <nav class="side">{NAV.replace('href="', f'href="{up}')}</nav>
  <main class="content">
{body}
  </main>
</div>
</body>
</html>
'''


def cards(items, depth, filt=False):
    up = '../' * depth
    box = '<input class="search filter" type="search" placeholder="在這頁篩選名稱、用途或分類" autocomplete="off">' if filt else ''
    script = """<script>
const f = document.querySelector('.filter');
f.addEventListener('input', () => {
  const t = f.value.trim().toLowerCase();
  document.querySelectorAll('.cards a').forEach(a => { a.hidden = !!t && !a.dataset.q.includes(t); });
});
</script>""" if filt else ''
    return box + '<div class="cards">' + ''.join(
        f'<a href="{up}{s["url"]}" data-q="{e((s["skill"] + " " + s["summary"] + " " + " ".join(s["cats"])).lower())}">'
        f'<strong>{e(s["skill"])}</strong><small>{e(s["author"])} ｜ {s["added"]}</small>'
        f'<span class="tags">{"".join(f"<i>{e(c)}</i>" for c in s["cats"])}</span><p>{e(s["summary"])}</p></a>'
        for s in by_date(items)) + '</div>' + script


def by_date(items):  # 新收錄的在前，同一天照名稱
    return sorted(sorted(items, key=lambda s: s['skill'].lower()), key=lambda s: s['added'], reverse=True)


def write(path, text):
    os.makedirs(os.path.dirname(f'{ROOT}/{path}'), exist_ok=True)
    open(f'{ROOT}/{path}', 'w').write(text)


skills = load()
by_cat = {c: [s for s in skills if c in s['cats']] for c in CATEGORIES}
sources = {}
for s in skills:
    sources.setdefault(s['src'], []).append(s)
src_label = {k: v[0]['repo'] for k, v in sources.items()}

NAV = '<details open><summary>分類</summary><ul>' + ''.join(
    f'<li><a href="c/{i}.html">{e(c)}<span>{len(by_cat[c])}</span></a></li>'
    for i, c in enumerate(CATEGORIES) if by_cat[c]) + '</ul></details>'
NAV += '<details><summary>來源</summary><ul>' + ''.join(
    f'<li><a href="r/{k}.html">{e(src_label[k])}<span>{len(sources[k])}</span></a></li>'
    for k in sorted(sources, key=lambda k: -len(sources[k]))) + '</ul></details>'

for d in OUT_DIRS:  # 產出物整個重建；ponytail: 不保留舊檔，data/ 才是唯一來源
    shutil.rmtree(f'{ROOT}/{d}', ignore_errors=True)

for s in skills:
    pane = lambda label, text: f'<section><h2>{label}</h2><pre>{e(text.rstrip())}</pre></section>'
    cat_links = '、'.join(f'<a href="../../c/{CATEGORIES.index(c)}.html">{e(c)}</a>' for c in s['cats'])
    body = (f'<h1>{e(s["skill"])}</h1>\n<p class="meta">{e(s["author"])} ｜ {cat_links} ｜ '
            f'<a href="{e(s["source"])}">原文</a> ｜ {e(s["license"])} ｜ {s["added"]} 收錄</p>\n<p class="summary">{e(s["summary"])}</p>\n')
    body += (f'<div class="pair">{pane("中文翻譯", s["zh"])}{pane("英文原文", s["en"])}</div>' if s['en']
             else f'<div class="pair single">{pane("中文原文", s["zh"])}</div>')
    write(s['url'], shell(f'{s["skill"]}｜{TITLE}', body, 2, s['summary']))

for i, c in enumerate(CATEGORIES):
    if by_cat[c]:
        write(f'c/{i}.html', shell(f'{c}｜{TITLE}', f'<h1>{e(c)}</h1>\n<p class="summary">{len(by_cat[c])} 份</p>\n' + cards(by_cat[c], 1, True), 1))
for k, items in sources.items():
    first = items[0]
    head = (f'<h1>{e(src_label[k])}</h1>\n<p class="meta">{e(first["author"])} ｜ '
            f'<a href="https://github.com/{e(first["repo"])}">GitHub</a> ｜ {e(first["license"])} ｜ {len(items)} 份</p>\n')
    write(f'r/{k}.html', shell(f'{src_label[k]}｜{TITLE}', head + cards(items, 1, True), 1))

index = [{'n': s['skill'], 'a': s['author'], 'd': s['summary'], 'c': s['cats'], 'u': s['url']} for s in skills]
write('search.json', json.dumps(index, ensure_ascii=False, separators=(',', ':')))
chips = ''.join(f'<button type="button" class="chip" data-c="{e(c)}">{e(c)}<span>{len(by_cat[c])}</span></button>'
                for c in CATEGORIES if by_cat[c])
home = f'''<h1>{TITLE}</h1>
<p class="summary">{DESC}，目前收錄 {len(skills)} 份。</p>
<input id="q" class="search" type="search" placeholder="搜尋 skill、作者或用途" autocomplete="off">
<div class="chips">{chips}</div>
<div id="results"></div>
<div id="browse"><h2 class="cat">最近收錄</h2>{cards(by_date(skills)[:12], 0)}</div>
<script>
// ponytail: 全部載入後純文字比對，幾千筆內夠快；分類按鈕單選，可和文字搜尋疊加
let data = null, cat = '';
const q = document.getElementById('q'), out = document.getElementById('results'), browse = document.getElementById('browse');
const esc = t => t.replace(/[&<>"]/g, ch => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}})[ch]);
async function run() {{
  data ??= await (await fetch('search.json')).json();
  const t = q.value.trim().toLowerCase();
  browse.hidden = !!(t || cat);
  if (!t && !cat) {{ out.innerHTML = ''; return; }}
  const hits = data.filter(s => (!cat || s.c.includes(cat)) && (s.n + ' ' + s.a + ' ' + s.d).toLowerCase().includes(t));
  out.innerHTML = `<p class="summary">${{hits.length}} 筆</p><div class="cards">` + hits.slice(0, 200).map(s =>
    `<a href="${{s.u}}"><strong>${{esc(s.n)}}</strong><small>${{esc(s.a)}}</small><span class="tags">${{s.c.map(c => `<i>${{esc(c)}}</i>`).join('')}}</span><p>${{esc(s.d)}}</p></a>`).join('') + '</div>';
}}
q.addEventListener('input', run);
document.querySelector('.chips').addEventListener('click', ev => {{
  const b = ev.target.closest('.chip'); if (!b) return;
  cat = cat === b.dataset.c ? '' : b.dataset.c;
  document.querySelectorAll('.chip').forEach(x => x.classList.toggle('on', x.dataset.c === cat));
  run();
}});
</script>'''
write('index.html', shell(TITLE, home, 0))

# README 的來源表跟著 data/ 走
rows = '\n'.join(f'| {v[0]["author"]} | [{v[0]["repo"]}](https://github.com/{v[0]["repo"]}) | {v[0]["license"]} | {len(v)} |'
                 for v in sorted(sources.values(), key=lambda v: -len(v)))
readme = open(f'{ROOT}/README.md').read()
a, b = readme.index('<!-- sources:start -->'), readme.index('<!-- sources:end -->')
write('README.md', readme[:a] + f'<!-- sources:start -->\n| 作者 | 來源 | 授權 | 份數 |\n|---|---|---|---|\n{rows}\n' + readme[b:])
print(f'{len(skills)} skills, {len(sources)} sources')
