// Client for the EmpiricalWiki chat widget — docked side panel driven by the
// Agent-SDK bridge (tools/chat-bridge/server.mjs). Design follows Claudian.
// Features: streamed prose, tool cards (+ Edit/Write diff), thinking marker,
// interactive AskUserQuestion / ExitPlanMode / permission prompts, model /
// thinking / permission / MCP selectors, slash-command autocomplete, multi-tab
// conversations (new / switch / close / fork), image paste, copy, context+cost.
// Runs on every Quartz `nav`; state in sessionStorage.

const API = "http://127.0.0.1:8788"
const STATE_KEY = "ew-chat:v2"

type Tool = { id: string; name: string; input: any; result?: string; isError?: boolean; done?: boolean }
type Ask = { askId: string; kind: string; questions?: any[]; plan?: string; tool?: string; summary?: string; answered?: boolean; result?: string }
type Meta = { durationMs?: number; cost?: number }
type Msg = { role: "user" | "assistant" | "tool" | "error" | "ask" | "think"; text?: string; tool?: Tool; ask?: Ask; meta?: Meta; imgs?: number }
type Conv = { id: string; title: string; sessionId: string | null; forkFrom?: string | null; msgs: Msg[] }
type State = {
  view: "page" | "claude"
  model: string | null
  perm: string
  think: boolean
  disabledMcp: string[]
  active: string
  convs: Conv[]
}

const SLASH_COMMANDS = [
  "ask", "ingest", "empirical-ingest", "theory-ingest", "empirical-design", "variable-map",
  "stata-plan", "discover", "edit", "check", "novelty", "review", "ideate", "survey",
  "research", "paper-plan", "paper-draft", "paper-compile", "rebuttal", "refine", "prefill",
  "exp-design", "exp-run", "exp-status", "exp-eval", "daily-arxiv", "init", "setup", "reset",
]

function uid(): string {
  return "c-" + Math.random().toString(36).slice(2) + "-" + String(performance.now()).replace(".", "")
}
function newConv(): Conv {
  return { id: uid(), title: "新对话", sessionId: null, msgs: [] }
}
function loadState(): State {
  try {
    const raw = sessionStorage.getItem(STATE_KEY)
    if (raw) {
      const s = JSON.parse(raw)
      if (Array.isArray(s.convs) && s.convs.length) return { view: "page", perm: "full", think: false, model: null, disabledMcp: [], ...s }
    }
  } catch {}
  const c = newConv()
  return { view: "page", model: null, perm: "full", think: false, disabledMcp: [], active: c.id, convs: [c] }
}
function saveState(s: State) {
  try {
    sessionStorage.setItem(STATE_KEY, JSON.stringify(s))
  } catch {}
}
function modelLabel(id: string | null): string {
  if (!id) return "本地默认"
  const m = id.match(/(opus|sonnet|haiku)-(\d+)-(\d+)/i)
  if (m) return `${m[1][0].toUpperCase()}${m[1].slice(1)} ${m[2]}.${m[3]}`
  return id
}

// ---- markdown ----------------------------------------------------------------
function esc(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
}
function inlineMd(s: string): string {
  s = s.replace(/`([^`]+)`/g, (_m, c) => `<code>${c}</code>`)
  s = s.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (_m, t, u) => `<a href="${u}" target="_blank" rel="noopener">${t}</a>`)
  s = s.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
  s = s.replace(/__([^_]+)__/g, "<strong>$1</strong>")
  s = s.replace(/(^|[^*])\*([^*\n]+)\*/g, "$1<em>$2</em>")
  return s
}
function mdToHtml(src: string): string {
  const cb: string[] = []
  src = src.replace(/```([a-zA-Z0-9_-]*)\n?([\s\S]*?)```/g, (_m, _l, code) => {
    cb.push(`<pre><code>${esc(code.replace(/\n$/, ""))}</code></pre>`)
    return ` CB${cb.length - 1} `
  })
  const lines = src.split("\n")
  const out: string[] = []
  let i = 0
  let para: string[] = []
  const flush = () => {
    if (para.length) {
      out.push(`<p>${inlineMd(esc(para.join(" ")))}</p>`)
      para = []
    }
  }
  while (i < lines.length) {
    const line = lines[i]
    const c = line.match(/^ CB(\d+) $/)
    if (c) { flush(); out.push(cb[Number(c[1])]); i++; continue }
    if (/^\s*$/.test(line)) { flush(); i++; continue }
    const h = line.match(/^(#{1,4})\s+(.*)$/)
    if (h) { flush(); const lv = Math.min(h[1].length + 2, 6); out.push(`<h${lv}>${inlineMd(esc(h[2]))}</h${lv}>`); i++; continue }
    if (/^\s*([-*+])\s+/.test(line)) {
      flush(); const it: string[] = []
      while (i < lines.length && /^\s*([-*+])\s+/.test(lines[i])) { it.push(`<li>${inlineMd(esc(lines[i].replace(/^\s*([-*+])\s+/, "")))}</li>`); i++ }
      out.push(`<ul>${it.join("")}</ul>`); continue
    }
    if (/^\s*\d+\.\s+/.test(line)) {
      flush(); const it: string[] = []
      while (i < lines.length && /^\s*\d+\.\s+/.test(lines[i])) { it.push(`<li>${inlineMd(esc(lines[i].replace(/^\s*\d+\.\s+/, "")))}</li>`); i++ }
      out.push(`<ol>${it.join("")}</ol>`); continue
    }
    if (/^\s*>\s?/.test(line)) { flush(); out.push(`<blockquote>${inlineMd(esc(line.replace(/^\s*>\s?/, "")))}</blockquote>`); i++; continue }
    para.push(line); i++
  }
  flush()
  return out.join("")
}

// ---------- tool registry ----------
// Every tool the Agent SDK can emit gets a glyph (text, no emoji), a Chinese
// label, and a purpose-built one-line summary. Unknown tools and MCP tools
// degrade gracefully instead of showing raw internals.
const shortPath = (p: any) => String(p || "").split("/").filter(Boolean).slice(-2).join("/")
const shortUrl = (u: any) => { try { const x = new URL(String(u)); return x.host + (x.pathname.length > 1 ? x.pathname.slice(0, 40) : "") } catch { return String(u || "").slice(0, 60) } }
type ToolMeta = { glyph: string; label: string; arg: (input: any) => string }
const TOOL_META: Record<string, ToolMeta> = {
  Read:        { glyph: "▤", label: "读取",     arg: (i) => shortPath(i?.file_path) + (i?.offset ? ` :${i.offset}` : "") },
  Write:       { glyph: "✎", label: "写入",     arg: (i) => shortPath(i?.file_path) },
  Edit:        { glyph: "✎", label: "编辑",     arg: (i) => shortPath(i?.file_path) },
  MultiEdit:   { glyph: "✎", label: "批量编辑", arg: (i) => shortPath(i?.file_path) + (Array.isArray(i?.edits) ? `（${i.edits.length} 处）` : "") },
  NotebookEdit:{ glyph: "✎", label: "编辑笔记本", arg: (i) => shortPath(i?.notebook_path) },
  Bash:        { glyph: "❯", label: "终端",     arg: (i) => String(i?.description || i?.command || "").slice(0, 120) },
  BashOutput:  { glyph: "❯", label: "终端输出", arg: () => "查看后台任务输出" },
  KillShell:   { glyph: "❯", label: "终止任务", arg: () => "" },
  Glob:        { glyph: "⌕", label: "找文件",   arg: (i) => String(i?.pattern || "") },
  Grep:        { glyph: "⌕", label: "搜代码",   arg: (i) => String(i?.pattern || "") + (i?.path ? `  ${shortPath(i.path)}` : "") },
  WebSearch:   { glyph: "◎", label: "联网搜索", arg: (i) => String(i?.query || "").slice(0, 80) },
  WebFetch:    { glyph: "◎", label: "抓取网页", arg: (i) => shortUrl(i?.url) },
  Task:        { glyph: "✦", label: "子代理",   arg: (i) => String(i?.description || "").slice(0, 80) },
  Agent:       { glyph: "✦", label: "子代理",   arg: (i) => String(i?.description || "").slice(0, 80) },
  Skill:       { glyph: "✦", label: "技能",     arg: (i) => "/" + String(i?.skill || "") + (i?.args ? " " + String(i.args).slice(0, 60) : "") },
  SlashCommand:{ glyph: "✦", label: "命令",     arg: (i) => String(i?.command || "").slice(0, 80) },
  TodoWrite:   { glyph: "▣", label: "任务清单", arg: (i) => { const ts = Array.isArray(i?.todos) ? i.todos : []; const doing = ts.find((t: any) => t.status === "in_progress"); return `${ts.filter((t: any) => t.status === "completed").length}/${ts.length}${doing ? " · " + String(doing.content).slice(0, 40) : ""}` } },
  AskUserQuestion: { glyph: "?", label: "提问", arg: () => "" },
  ExitPlanMode:    { glyph: "▷", label: "提交计划", arg: () => "" },
  ToolSearch:  { glyph: "⌕", label: "找工具",   arg: (i) => String(i?.query || "").slice(0, 60) },
  WebView:     { glyph: "◎", label: "查看页面", arg: (i) => shortUrl(i?.url) },
}
function toolMeta(name: string): ToolMeta {
  if (TOOL_META[name]) return TOOL_META[name]
  // MCP tools arrive as mcp__<server>__<tool>
  const m = /^mcp__([^_]+(?:_[^_]+)*?)__(.+)$/.exec(name)
  if (m) return { glyph: "◇", label: "MCP·" + m[1], arg: (i) => m[2] + (i && (i.query || i.q) ? `  ${String(i.query || i.q).slice(0, 50)}` : "") }
  return { glyph: "›", label: name, arg: (i) => {
    if (!i) return ""
    for (const k of ["file_path", "path", "pattern", "query", "url", "description"]) if (i[k]) return String(i[k]).slice(0, 80)
    return ""
  } }
}

function setup() {
  const root = document.getElementById("ew-chat-root")
  if (!root) return
  const panel = document.getElementById("ew-chat-panel") as HTMLElement | null
  const resetBtn = document.getElementById("ew-chat-reset") as HTMLButtonElement | null
  const forkBtn = document.getElementById("ew-chat-fork") as HTMLButtonElement | null
  const log = document.getElementById("ew-chat-log") as HTMLElement | null
  const input = document.getElementById("ew-chat-input") as HTMLTextAreaElement | null
  const sendBtn = document.getElementById("ew-chat-send") as HTMLButtonElement | null
  const tabsEl = document.getElementById("ew-chat-tabs")
  const attachEl = document.getElementById("ew-chat-attach")
  const modelEl = document.getElementById("ew-chat-model") as HTMLButtonElement | null
  const thinkEl = document.getElementById("ew-chat-think") as HTMLButtonElement | null
  const permEl = document.getElementById("ew-chat-perm") as HTMLButtonElement | null
  const mcpEl = document.getElementById("ew-chat-mcp") as HTMLButtonElement | null
  const ctxEl = document.getElementById("ew-chat-ctx")
  const vswEls = Array.from(root.querySelectorAll<HTMLButtonElement>("#ew-view-switch .ew-vsw"))
  if (!panel || !log || !input || !sendBtn || !vswEls.length) return

  let state = loadState()
  try { if (new URLSearchParams(location.search).get("ew") === "claude") state.view = "claude" } catch {}
  let busy = false
  let assistantIdx = -1
  let thinkIdx = -1
  let controller: AbortController | null = null
  let streamConv: Conv | null = null
  let pendingImages: { mime: string; data: string; url: string }[] = []
  let mcpServers: string[] = []
  const pageTitle = (document.querySelector("h1")?.textContent || document.title || "这一页").trim()

  const cur = (): Conv => state.convs.find((c) => c.id === state.active) || state.convs[0]

  // ---------- footer selectors ----------
  const MODELS = [
    { id: null as string | null, label: "本地默认" },
    { id: "claude-opus-4-8", label: "Opus 4.8" },
    { id: "claude-sonnet-4-6", label: "Sonnet 4.6" },
    { id: "claude-haiku-4-5", label: "Haiku 4.5" },
  ]
  const PERMS = [
    { v: "full", label: "完全权限", desc: "全部自动放行" },
    { v: "ask", label: "逐步确认", desc: "每个工具问你" },
    { v: "plan", label: "只读", desc: "只读不改动" },
  ]
  const THINKS = [
    { v: false, label: "思考: 关", desc: "直接回答" },
    { v: true, label: "思考: 深度", desc: "先深入思考" },
  ]
  function refreshFooter() {
    if (modelEl) modelEl.textContent = (MODELS.find((m) => m.id === state.model) || MODELS[0]).label
    if (thinkEl) thinkEl.textContent = state.think ? "思考: 深度" : "思考: 关"
    if (permEl) {
      const p = PERMS.find((x) => x.v === state.perm) || PERMS[0]
      permEl.textContent = p.label
      permEl.classList.toggle("ew-foot-yolo", state.perm === "full")
    }
    if (mcpEl) {
      const off = state.disabledMcp.length
      mcpEl.textContent = off ? `MCP ${mcpServers.length - off}/${mcpServers.length}` : "MCP"
    }
  }
  let openMenuEl: HTMLElement | null = null
  function closeMenu() {
    openMenuEl?.remove()
    openMenuEl = null
    document.removeEventListener("click", onDocClick, true)
  }
  function onDocClick(e: MouseEvent) {
    if (openMenuEl && !openMenuEl.contains(e.target as Node)) closeMenu()
  }
  function openMenu(anchor: HTMLElement, items: { label: string; desc?: string; active: boolean; pick: () => void }[], cls = "") {
    closeMenu()
    const menu = document.createElement("div")
    menu.className = "ew-menu " + cls
    items.forEach((it) => {
      const b = document.createElement("button")
      b.className = "ew-menu-item" + (it.active ? " is-active" : "")
      b.innerHTML = `<span class="ew-menu-label"></span>` + (it.desc ? `<span class="ew-menu-desc"></span>` : "")
      ;(b.querySelector(".ew-menu-label") as HTMLElement).textContent = it.label
      if (it.desc) (b.querySelector(".ew-menu-desc") as HTMLElement).textContent = it.desc
      b.addEventListener("click", (e) => {
        e.stopPropagation()
        it.pick()
        refreshFooter()
        saveState(state)
        if (!cls.includes("ew-keep")) closeMenu()
      })
      menu.appendChild(b)
    })
    const r = anchor.getBoundingClientRect()
    menu.style.left = r.left + "px"
    menu.style.bottom = window.innerHeight - r.top + 6 + "px"
    document.body.appendChild(menu)
    openMenuEl = menu
    setTimeout(() => document.addEventListener("click", onDocClick, true), 0)
  }
  const onModelMenu = () => openMenu(modelEl!, MODELS.map((m) => ({ label: m.label, active: state.model === m.id, pick: () => (state.model = m.id) })))
  const onThinkMenu = () => openMenu(thinkEl!, THINKS.map((t) => ({ label: t.label, desc: t.desc, active: state.think === t.v, pick: () => (state.think = t.v) })))
  const onPermMenu = () => openMenu(permEl!, PERMS.map((p) => ({ label: p.label, desc: p.desc, active: state.perm === p.v, pick: () => (state.perm = p.v) })))
  const onMcpMenu = () =>
    openMenu(
      mcpEl!,
      mcpServers.map((s) => ({
        label: s,
        desc: state.disabledMcp.includes(s) ? "已禁用" : "已启用",
        active: !state.disabledMcp.includes(s),
        pick: () => {
          state.disabledMcp = state.disabledMcp.includes(s) ? state.disabledMcp.filter((x) => x !== s) : [...state.disabledMcp, s]
        },
      })),
      "ew-keep",
    )
  refreshFooter()

  // ---------- slash autocomplete ----------
  function showSlash(qstr: string) {
    const matches = SLASH_COMMANDS.filter((c) => c.startsWith(qstr)).slice(0, 8)
    if (!matches.length) {
      if (openMenuEl?.classList.contains("ew-slash")) closeMenu()
      return
    }
    closeMenu()
    const menu = document.createElement("div")
    menu.className = "ew-menu ew-slash"
    matches.forEach((c) => {
      const b = document.createElement("button")
      b.className = "ew-menu-item"
      b.innerHTML = `<span class="ew-menu-label"></span>`
      ;(b.querySelector(".ew-menu-label") as HTMLElement).textContent = "/" + c
      b.addEventListener("click", (e) => {
        e.stopPropagation()
        input!.value = "/" + c + " "
        input!.focus()
        closeMenu()
      })
      menu.appendChild(b)
    })
    const wrap = document.getElementById("ew-chat-inputwrap")!
    const r = wrap.getBoundingClientRect()
    menu.style.left = r.left + "px"
    menu.style.bottom = window.innerHeight - r.top + 6 + "px"
    menu.style.minWidth = r.width + "px"
    menu.style.maxHeight = "240px"
    menu.style.overflowY = "auto"
    document.body.appendChild(menu)
    openMenuEl = menu
    setTimeout(() => document.addEventListener("click", onDocClick, true), 0)
  }

  function setActualModel(id: string | null) {
    if (modelEl && id) modelEl.title = "实际运行: " + modelLabel(id)
  }
  function updateCtx(used?: number, window?: number) {
    if (!ctxEl) return
    if (used && window) {
      const pct = Math.min(100, Math.round((used / window) * 100))
      ctxEl.textContent = `上下文 ${pct < 1 ? "<1" : pct}%`
      ctxEl.title = `${used.toLocaleString()} / ${window.toLocaleString()} tokens`
    }
  }

  // health + mcp list
  fetch(`${API}/api/health`).then((r) => r.json()).then(() => {
    const st = document.getElementById("ew-chat-status")
    if (st) st.textContent = "本地 · 已连接"
  }).catch(() => {
    const st = document.getElementById("ew-chat-status")
    if (st) st.textContent = "后端未启动 · 跑 tools/chat.sh"
  })
  fetch(`${API}/api/mcp`).then((r) => r.json()).then((j) => {
    mcpServers = Array.isArray(j.servers) ? j.servers : []
    if (mcpEl) mcpEl.classList.toggle("ew-gone", mcpServers.length === 0)
    refreshFooter()
  }).catch(() => {})

  function suggestions() {
    return [
      { label: "总结这一页", prompt: `用三五句话总结当前 wiki 页面《${pageTitle}》的核心内容。` },
      { label: "相关页面", prompt: `《${pageTitle}》和本 wiki 里哪些页面相关？给出 wikilink。` },
      { label: "出研究计划", prompt: `基于本 wiki 现有图谱里的空白，帮我立一个新的实证选题并给出研究设计。` },
    ]
  }
  function findTool(conv: Conv, id: string): Msg | undefined {
    for (let i = conv.msgs.length - 1; i >= 0; i--) if (conv.msgs[i].role === "tool" && conv.msgs[i].tool?.id === id) return conv.msgs[i]
    return undefined
  }
  async function postAnswer(askId: string, payload: any) {
    try {
      await fetch(`${API}/api/answer`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ askId, ...payload }) })
    } catch {}
  }

  // ---------- conversation tabs ----------
  function renderTabs() {
    if (!tabsEl) return
    tabsEl.innerHTML = ""
    if (state.convs.length <= 1) {
      tabsEl.style.display = "none"
      return
    }
    tabsEl.style.display = "flex"
    state.convs.forEach((c) => {
      const t = document.createElement("div")
      t.className = "ew-conv-tab" + (c.id === state.active ? " is-active" : "")
      const lab = document.createElement("span")
      lab.className = "ew-conv-title"
      lab.textContent = c.title || "新对话"
      lab.addEventListener("click", () => switchConv(c.id))
      t.appendChild(lab)
      const x = document.createElement("button")
      x.className = "ew-conv-close"
      x.textContent = "×"
      x.addEventListener("click", (e) => {
        e.stopPropagation()
        closeConv(c.id)
      })
      t.appendChild(x)
      tabsEl.appendChild(t)
    })
  }
  function switchConv(id: string) {
    if (busy) controller?.abort()
    state.active = id
    assistantIdx = -1
    thinkIdx = -1
    saveState(state)
    renderTabs()
    render()
  }
  function closeConv(id: string) {
    const i = state.convs.findIndex((c) => c.id === id)
    if (i < 0) return
    state.convs.splice(i, 1)
    if (state.convs.length === 0) state.convs.push(newConv())
    if (state.active === id) state.active = state.convs[Math.max(0, i - 1)].id
    saveState(state)
    renderTabs()
    render()
  }
  function startConv(forkFrom?: string | null, title?: string) {
    if (busy) controller?.abort()
    const c = newConv()
    if (forkFrom) {
      c.forkFrom = forkFrom
      c.title = title || "分支"
    }
    state.convs.push(c)
    state.active = c.id
    assistantIdx = -1
    thinkIdx = -1
    saveState(state)
    switchView("claude")
  }

  // ---------- image attachments ----------
  function renderAttach() {
    if (!attachEl) return
    attachEl.innerHTML = ""
    attachEl.style.display = pendingImages.length ? "flex" : "none"
    pendingImages.forEach((im, i) => {
      const chip = document.createElement("div")
      chip.className = "ew-attach-chip"
      const img = document.createElement("img")
      img.src = im.url
      const x = document.createElement("button")
      x.textContent = "×"
      x.addEventListener("click", () => {
        pendingImages.splice(i, 1)
        renderAttach()
      })
      chip.append(img, x)
      attachEl.appendChild(chip)
    })
  }
  const onPaste = (e: ClipboardEvent) => {
    const items = e.clipboardData?.items
    if (!items) return
    for (const it of items as any) {
      if (it.type && it.type.startsWith("image/")) {
        const file = it.getAsFile()
        if (!file) continue
        const reader = new FileReader()
        reader.onload = () => {
          const url = String(reader.result)
          const data = url.split(",")[1] || ""
          pendingImages.push({ mime: file.type || "image/png", data, url })
          renderAttach()
        }
        reader.readAsDataURL(file)
      }
    }
  }

  // ---------- tool / ask renderers ----------
  function buildDiff(t: Tool): HTMLElement | null {
    const edits: { oldS: string; newS: string }[] = []
    if (t.name === "Edit" && t.input?.old_string != null) edits.push({ oldS: String(t.input.old_string), newS: String(t.input.new_string ?? "") })
    else if (t.name === "MultiEdit" && Array.isArray(t.input?.edits)) for (const e of t.input.edits) edits.push({ oldS: String(e.old_string ?? ""), newS: String(e.new_string ?? "") })
    else if (t.name === "Write" && t.input?.content != null) edits.push({ oldS: "", newS: String(t.input.content) })
    else return null
    const wrap = document.createElement("div")
    wrap.className = "ew-diff"
    for (const e of edits) {
      if (e.oldS) e.oldS.split("\n").forEach((l) => { const d = document.createElement("div"); d.className = "ew-diff-del"; d.textContent = "- " + l; wrap.appendChild(d) })
      e.newS.split("\n").forEach((l) => { const a = document.createElement("div"); a.className = "ew-diff-add"; a.textContent = "+ " + l; wrap.appendChild(a) })
    }
    return wrap
  }
  function buildTodoList(t: Tool): HTMLElement | null {
    if (t.name !== "TodoWrite" || !Array.isArray(t.input?.todos)) return null
    const wrap = document.createElement("div"); wrap.className = "ew-todo"
    for (const td of t.input.todos) {
      const li = document.createElement("div"); li.className = "ew-todo-item ew-todo-" + (td.status || "pending")
      const mk = td.status === "completed" ? "✓" : td.status === "in_progress" ? "▸" : "·"
      li.textContent = `${mk} ${String(td.content || "").slice(0, 90)}`
      wrap.appendChild(li)
    }
    return wrap
  }
  function renderTool(msg: Msg, row: HTMLElement) {
    const t = msg.tool!
    const meta = toolMeta(t.name)
    const head = document.createElement("button")
    head.className = "ew-tool-head"
    head.title = t.name // 原始工具名悬浮可见
    const ic = document.createElement("span"); ic.className = "ew-tool-icon"; ic.textContent = meta.glyph
    const nm = document.createElement("span"); nm.className = "ew-tool-name"; nm.textContent = meta.label
    const sm = document.createElement("span"); sm.className = "ew-tool-summary"; sm.textContent = meta.arg(t.input)
    const st = document.createElement("span"); st.className = "ew-tool-status " + (t.isError ? "st-error" : t.done ? "st-done" : "st-run"); st.textContent = t.isError ? "✕" : t.done ? "✓" : "◍"
    head.append(ic, nm, sm, st)
    row.appendChild(head)
    const rich = buildDiff(t) || buildTodoList(t)
    if (rich || t.result) {
      const body = document.createElement("div"); body.className = "ew-tool-content"
      if (rich) body.appendChild(rich)
      if (t.result && !rich) { const pre = document.createElement("div"); pre.className = "ew-tool-lines"; pre.textContent = t.result.length > 1800 ? t.result.slice(0, 1800) + "\n… 已截断" : t.result; body.appendChild(pre) }
      body.style.display = rich ? "block" : "none"
      head.classList.add("ew-clickable")
      head.addEventListener("click", () => { body.style.display = body.style.display === "none" ? "block" : "none" })
      row.appendChild(body)
    }
  }
  function renderAsk(msg: Msg, container: HTMLElement) {
    const ask = msg.ask!
    const card = document.createElement("div")
    card.className = "ew-ask"
    if (ask.kind === "permission") {
      const t = document.createElement("div"); t.className = "ew-ask-title"; t.textContent = "请求执行工具"
      const toolRow = document.createElement("div"); toolRow.className = "ew-ask-permtool"
      toolRow.innerHTML = `<span class="ew-ask-permname"></span><span class="ew-ask-permsum"></span>`
      ;(toolRow.querySelector(".ew-ask-permname") as HTMLElement).textContent = ask.tool || "tool"
      ;(toolRow.querySelector(".ew-ask-permsum") as HTMLElement).textContent = ask.summary || ""
      card.append(t, toolRow)
      if (ask.answered) { const s = document.createElement("div"); s.className = "ew-ask-done"; s.textContent = ask.result || "已处理"; card.appendChild(s) }
      else {
        const acts = document.createElement("div"); acts.className = "ew-ask-actions"
        const ok = document.createElement("button"); ok.className = "ew-ask-go"; ok.textContent = "允许"
        ok.addEventListener("click", () => { ask.answered = true; ask.result = "✓ 已允许"; saveState(state); render(); postAnswer(ask.askId, { decision: { type: "allow" } }) })
        const always = document.createElement("button"); always.className = "ew-ask-alt"; always.textContent = "始终允许"
        always.addEventListener("click", () => { ask.answered = true; ask.result = "✓ 本会话始终允许 " + (ask.tool || ""); saveState(state); render(); postAnswer(ask.askId, { decision: { type: "allow", always: true } }) })
        const no = document.createElement("button"); no.className = "ew-ask-alt"; no.textContent = "拒绝"
        no.addEventListener("click", () => { ask.answered = true; ask.result = "✕ 已拒绝"; saveState(state); render(); postAnswer(ask.askId, { decision: { type: "deny" } }) })
        acts.append(ok, always, no); card.appendChild(acts)
      }
      container.appendChild(card); return
    }
    if (ask.kind === "plan") {
      const t = document.createElement("div"); t.className = "ew-ask-title"; t.textContent = "计划待批准"
      const body = document.createElement("div"); body.className = "ew-ask-plan ew-assistant"; body.innerHTML = mdToHtml(ask.plan || "(空计划)")
      card.append(t, body)
      if (ask.answered) { const s = document.createElement("div"); s.className = "ew-ask-done"; s.textContent = ask.result || "已处理"; card.appendChild(s) }
      else {
        const acts = document.createElement("div"); acts.className = "ew-ask-actions"
        const ok = document.createElement("button"); ok.className = "ew-ask-go"; ok.textContent = "✓ 批准并执行"
        ok.addEventListener("click", () => { ask.answered = true; ask.result = "✓ 已批准计划"; saveState(state); render(); postAnswer(ask.askId, { decision: { type: "approve" } }) })
        const fb = document.createElement("button"); fb.className = "ew-ask-alt"; fb.textContent = "提意见"
        fb.addEventListener("click", () => { const txt = window.prompt("对计划的意见（会让它继续完善）："); if (txt == null) return; ask.answered = true; ask.result = "↩ 已反馈：" + txt; saveState(state); render(); postAnswer(ask.askId, { decision: { type: "feedback", text: txt } }) })
        acts.append(ok, fb); card.appendChild(acts)
      }
      container.appendChild(card); return
    }
    // AskUserQuestion
    const qs = ask.questions || []
    if (ask.answered) { const s = document.createElement("div"); s.className = "ew-ask-done"; s.textContent = ask.result || "已回答"; card.appendChild(s); container.appendChild(card); return }
    const sels: Set<string>[] = qs.map(() => new Set<string>())
    const others: string[] = qs.map(() => "")
    qs.forEach((q: any, qi: number) => {
      const multi = !!q.multiSelect
      const qt = document.createElement("div"); qt.className = "ew-ask-q-text"; qt.textContent = q.question || q.header || "请选择"; card.appendChild(qt)
      const list = document.createElement("div"); list.className = "ew-ask-list"
      const opts = Array.isArray(q.options) ? q.options : []
      opts.forEach((o: any, oi: number) => {
        const val = String(o.value ?? o.label ?? o)
        const item = document.createElement("div"); item.className = "ew-ask-item"
        const mark = document.createElement("span"); mark.className = "ew-ask-mark"; mark.textContent = multi ? "[ ]" : oi + 1 + "."
        const content = document.createElement("span"); content.className = "ew-ask-item-content"
        const lab = document.createElement("span"); lab.className = "ew-ask-item-label"; lab.textContent = String(o.label ?? val); content.appendChild(lab)
        if (o.description) { const d = document.createElement("span"); d.className = "ew-ask-item-desc"; d.textContent = String(o.description); content.appendChild(d) }
        item.append(mark, content)
        item.addEventListener("click", () => {
          if (multi) {
            if (sels[qi].has(val)) { sels[qi].delete(val); item.classList.remove("is-selected"); mark.textContent = "[ ]" }
            else { sels[qi].add(val); item.classList.add("is-selected"); mark.textContent = "[✓]" }
          } else {
            list.querySelectorAll(".ew-ask-item").forEach((e, idx) => { e.classList.remove("is-selected"); const m = e.querySelector(".ew-ask-mark") as HTMLElement; if (m && !m.classList.contains("ew-ask-mark-other")) m.textContent = idx + 1 + "." })
            sels[qi].clear(); sels[qi].add(val); item.classList.add("is-selected"); mark.textContent = "✓"
            if (qs.length === 1 && !q.isOther) submit()
          }
        })
        list.appendChild(item)
      })
      if (q.isOther) {
        const item = document.createElement("div"); item.className = "ew-ask-item ew-ask-other"
        const mark = document.createElement("span"); mark.className = "ew-ask-mark ew-ask-mark-other"; mark.textContent = multi ? "[+]" : "›"
        const inp = document.createElement("input"); inp.className = "ew-ask-custom"; inp.placeholder = "其他（自定义回答）…"
        inp.addEventListener("input", () => (others[qi] = inp.value))
        item.append(mark, inp); list.appendChild(item)
      }
      card.appendChild(list)
    })
    const submitRow = document.createElement("button"); submitRow.className = "ew-ask-submit"; submitRow.textContent = "✓ 提交"
    submitRow.addEventListener("click", () => submit()); card.appendChild(submitRow)
    const hints = document.createElement("div"); hints.className = "ew-ask-hints"; hints.textContent = "点击选择" + (qs.some((q: any) => q.multiSelect) ? "（方括号可多选）" : "") + " · 选完点提交"; card.appendChild(hints)
    container.appendChild(card)
    function submit() {
      const answers: Record<string, string | string[]> = {}
      const summary: string[] = []
      for (let qi = 0; qi < qs.length; qi++) {
        const q = qs[qi]; const other = others[qi].trim(); let v: string | string[]
        if (q.multiSelect) { const arr = [...sels[qi]]; if (other) arr.push(other); if (arr.length === 0) { submitRow.textContent = "✗ 请至少选一项"; return } v = arr }
        else { v = other || [...sels[qi]][0] || ""; if (!v) { submitRow.textContent = "✗ 请先选择"; return } }
        answers[q.id ?? q.question ?? String(qi)] = v
        summary.push(`${q.header || q.question || ""}: ${Array.isArray(v) ? v.join("、") : v}`)
      }
      ask.answered = true; ask.result = "✓ " + summary.join(" / "); saveState(state); render(); postAnswer(ask.askId, { answers })
    }
  }

  // ---------- main render ----------
  function render() {
    if (!log) return
    const conv = cur()
    const msgs = conv.msgs
    log.innerHTML = ""
    if (msgs.length === 0) {
      const empty = document.createElement("div"); empty.className = "ew-welcome"
      empty.innerHTML = '<div class="ew-welcome-greeting">今天想做点什么？</div><div class="ew-welcome-sub">接的是本地 Claude Code，工作目录就是这个 wiki 项目。能读写页面、跑 skill，遇到要拍板时会直接在这里弹选项。</div>'
      const chips = document.createElement("div"); chips.className = "ew-chips"
      for (const s of suggestions()) { const b = document.createElement("button"); b.className = "ew-chip"; b.textContent = s.label; b.addEventListener("click", () => { input!.value = s.prompt; send() }); chips.appendChild(b) }
      empty.appendChild(chips); log.appendChild(empty); return
    }
    const isStreamConv = streamConv && conv.id === streamConv.id
    msgs.forEach((m, idx) => {
      const row = document.createElement("div"); row.className = "ew-row ew-row-" + m.role
      if (m.role === "user") {
        const b = document.createElement("div"); b.className = "ew-user"
        b.textContent = (m.imgs ? "🖼×" + m.imgs + " " : "") + (m.text || "")
        row.appendChild(b)
      } else if (m.role === "tool") { renderTool(m, row) }
      else if (m.role === "ask") { renderAsk(m, row) }
      else if (m.role === "error") { row.textContent = m.text || "" }
      else if (m.role === "think") {
        const head = document.createElement("div"); head.className = "ew-think-head"
        if (m.text) {
          head.textContent = busy && isStreamConv && idx === thinkIdx ? "思考中…" : "已思考（点击展开）"
          const body = document.createElement("div"); body.className = "ew-think-body"; body.textContent = m.text
          body.style.display = busy && isStreamConv && idx === thinkIdx ? "block" : "none"
          head.addEventListener("click", () => { body.style.display = body.style.display === "none" ? "block" : "none" })
          row.append(head, body)
          if (isStreamConv && idx === typeTarget && typeKind === "txt") liveBody = body
        } else { head.textContent = busy && isStreamConv && idx === thinkIdx ? "深度思考中…" : "已深度思考"; head.classList.add("ew-think-empty"); row.append(head) }
      } else {
        const body = document.createElement("div"); body.className = "ew-assistant"; body.innerHTML = mdToHtml(m.text || "")
        const isTyping = isStreamConv && idx === typeTarget && typeKind === "md"
        if (isTyping || (busy && isStreamConv && idx === assistantIdx)) { const caret = document.createElement("span"); caret.className = "ew-caret"; body.appendChild(caret) }
        if (isTyping) liveBody = body
        if (m.text) {
          const cp = document.createElement("button"); cp.className = "ew-copy"; cp.textContent = "复制"
          cp.addEventListener("click", () => { navigator.clipboard?.writeText(m.text || ""); cp.textContent = "已复制"; setTimeout(() => (cp.textContent = "复制"), 1200) })
          row.appendChild(cp)
        }
        row.appendChild(body)
        if (m.meta && (m.meta.durationMs || m.meta.cost)) {
          const f = document.createElement("div"); f.className = "ew-resp-meta"; const parts: string[] = []
          if (m.meta.durationMs) parts.push((m.meta.durationMs / 1000).toFixed(1) + "s")
          if (m.meta.cost) parts.push("$" + m.meta.cost.toFixed(4))
          f.textContent = parts.join(" · "); row.appendChild(f)
        }
      }
      log!.appendChild(row)
    })
    if (busy && isStreamConv && assistantIdx === -1 && msgs[msgs.length - 1]?.role !== "ask") {
      const row = document.createElement("div"); row.className = "ew-row ew-row-assistant"
      row.innerHTML = '<div class="ew-thinking">思考中<span>.</span><span>.</span><span>.</span></div>'
      log.appendChild(row)
    }
    log.scrollTop = log.scrollHeight
  }

  function setBusy(b: boolean) { busy = b; sendBtn!.classList.toggle("ew-busy", b) }
  function switchView(v: "page" | "claude") {
    state.view = v
    root!.classList.toggle("ew-claude-mode", v === "claude")
    document.documentElement.classList.toggle("ew-wide", v === "claude") // widen the right column
    vswEls.forEach((b) => b.classList.toggle("is-active", b.dataset.v === v))
    // hide/show the sibling right-rail components (Graph / ToC / Backlinks)
    const parent = root!.parentElement
    if (parent) for (const sib of Array.from(parent.children)) if (sib !== root) (sib as HTMLElement).style.display = v === "claude" ? "none" : ""
    saveState(state)
    if (v === "claude") { renderTabs(); render(); setTimeout(() => input!.focus(), 30) }
  }
  const ensureAssistant = (): number => {
    const c = streamConv!
    if (assistantIdx >= 0 && c.msgs[assistantIdx]?.role === "assistant") return assistantIdx
    c.msgs.push({ role: "assistant", text: "" }); assistantIdx = c.msgs.length - 1; return assistantIdx
  }
  const ensureThink = (): number => {
    const c = streamConv!
    if (thinkIdx >= 0 && c.msgs[thinkIdx]?.role === "think") return thinkIdx
    c.msgs.push({ role: "think", text: "" }); thinkIdx = c.msgs.length - 1; return thinkIdx
  }

  // ---------- typewriter pacer ----------
  // SSE deltas arrive in sentence-sized bursts; dumping them straight into the
  // DOM reads as text "jumping". Instead, deltas land in a queue and an rAF
  // loop releases characters at a steady pace — char-by-char when the backlog
  // is small, speeding up smoothly as it grows so we never fall behind.
  // While typing, only the live message's element repaints (not the whole log).
  let typeQ = ""
  let typeTarget = -1
  let typeKind: "md" | "txt" = "md"
  let typeRAF = 0
  let liveBody: HTMLElement | null = null // captured by render() for the streaming msg
  function typeStep(): number {
    // 节奏标定：60fps 下 1字/帧=60字/秒（经典打字机），3字/帧=180字/秒。
    // 积压越多越快（不让显示落后生成太远），但上限收着，保持"在打字"的观感。
    const n = typeQ.length
    if (n > 2400) return 32
    if (n > 800) return 8
    if (n > 240) return 3
    return n > 0 ? 1 : 0
  }
  function paintLive() {
    const c = streamConv
    if (!c || typeTarget < 0) return
    if (!liveBody || !liveBody.isConnected) { render(); return } // render() recaptures liveBody
    const text = c.msgs[typeTarget]?.text || ""
    if (typeKind === "txt") liveBody.textContent = text
    else {
      liveBody.innerHTML = mdToHtml(text)
      const caret = document.createElement("span"); caret.className = "ew-caret"; liveBody.appendChild(caret)
    }
    if (log) log.scrollTop = log.scrollHeight
  }
  function typeTick() {
    typeRAF = 0
    if (typeTarget < 0 || !streamConv) { typeQ = ""; return }
    const n = typeStep()
    if (n > 0) {
      streamConv.msgs[typeTarget].text = (streamConv.msgs[typeTarget].text || "") + typeQ.slice(0, n)
      typeQ = typeQ.slice(n)
      paintLive()
    }
    if (typeQ.length) typeRAF = requestAnimationFrame(typeTick)
    else {
      // 自然流完：落盘；若整轮已结束，撤掉光标。
      saveState(state)
      if (!busy) { typeTarget = -1; liveBody = null; render() }
    }
  }
  function enqueueType(k: number, kind: "md" | "txt", s: string) {
    if (typeTarget !== k || typeKind !== kind) flushType(false)
    typeTarget = k; typeKind = kind
    // 页签在后台时 rAF 会被浏览器节流甚至停摆——此时没有动画可言，直接落字，
    // 用户切回来看到的就是完整进度而不是积压的队列。
    if (document.hidden) {
      streamConv!.msgs[k].text = (streamConv!.msgs[k].text || "") + typeQ + s
      typeQ = ""
      paintLive()
      return
    }
    typeQ += s
    if (!typeRAF) typeRAF = requestAnimationFrame(typeTick)
  }
  // Drain instantly (tool call / turn end / error): the remaining queue lands
  // at once so later messages never appear before earlier text finishes.
  function flushType(repaint = true) {
    if (typeRAF) { cancelAnimationFrame(typeRAF); typeRAF = 0 }
    if (typeTarget >= 0 && typeQ && streamConv) streamConv.msgs[typeTarget].text = (streamConv.msgs[typeTarget].text || "") + typeQ
    typeQ = ""; typeTarget = -1; liveBody = null
    if (repaint) render()
  }

  async function send() {
    const text = input!.value.trim()
    if (busy) { controller?.abort(); return }
    if (!text && !pendingImages.length) return
    const conv = cur()
    streamConv = conv
    const imgs = pendingImages.slice()
    pendingImages = []
    renderAttach()
    input!.value = ""
    input!.style.height = "auto"
    conv.msgs.push({ role: "user", text, imgs: imgs.length || undefined })
    if (conv.title === "新对话" && text) conv.title = text.slice(0, 16)
    assistantIdx = -1
    thinkIdx = -1
    setBusy(true)
    renderTabs()
    render()
    saveState(state)
    controller = new AbortController()
    try {
      const resp = await fetch(`${API}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tabId: conv.id,
          prompt: text || "（见图）",
          model: state.model || undefined,
          permission: state.perm,
          thinking: state.think,
          forkFrom: !conv.sessionId && conv.forkFrom ? conv.forkFrom : undefined,
          images: imgs.length ? imgs.map((im) => ({ mime: im.mime, data: im.data })) : undefined,
          disabledMcp: state.disabledMcp.length ? state.disabledMcp : undefined,
        }),
        signal: controller.signal,
      })
      if (!resp.ok || !resp.body) throw new Error("bridge HTTP " + resp.status)
      const reader = resp.body.getReader()
      const dec = new TextDecoder()
      let buf = ""
      while (true) {
        const { value, done } = await reader.read()
        if (done) break
        buf += dec.decode(value, { stream: true })
        let sep
        while ((sep = buf.indexOf("\n\n")) !== -1) {
          const frame = buf.slice(0, sep); buf = buf.slice(sep + 2)
          const line = frame.split("\n").find((l) => l.startsWith("data:")); if (!line) continue
          let ev: any; try { ev = JSON.parse(line.slice(5).trim()) } catch { continue }
          if (ev.type === "session") { conv.sessionId = ev.sessionId; conv.forkFrom = null }
          else if (ev.type === "model") setActualModel(ev.model)
          else if (ev.type === "think_start") { ensureThink(); render() }
          else if (ev.type === "think_delta") { const k = ensureThink(); enqueueType(k, "txt", ev.content) }
          else if (ev.type === "delta") { const k = ensureAssistant(); enqueueType(k, "md", ev.content) }
          else if (ev.type === "result") {
            // 不 flush：让结尾段照常逐字流完，否则最后一大块会瞬间砸出来。
            updateCtx(ev.usedTokens, ev.contextWindow)
            for (let i = streamConv!.msgs.length - 1; i >= 0; i--) if (streamConv!.msgs[i].role === "assistant") { streamConv!.msgs[i].meta = { durationMs: ev.durationMs, cost: ev.cost }; break }
            render(); saveState(state)
          } else if (ev.type === "tool") { flushType(false); streamConv!.msgs.push({ role: "tool", tool: { id: ev.id, name: ev.name, input: ev.input } }); assistantIdx = -1; render(); saveState(state) }
          else if (ev.type === "tool_result") { const tm = findTool(streamConv!, ev.id); if (tm?.tool) { tm.tool.result = ev.content; tm.tool.isError = ev.isError; tm.tool.done = true; render(); saveState(state) } }
          else if (ev.type === "ask") { flushType(false); streamConv!.msgs.push({ role: "ask", ask: { askId: ev.askId, kind: ev.kind, questions: ev.questions, plan: ev.plan, tool: ev.tool, summary: ev.summary } }); assistantIdx = -1; render(); saveState(state) }
          else if (ev.type === "turn_end") { assistantIdx = -1; thinkIdx = -1 }
          else if (ev.type === "wiki_synced") {
            // 本回合改写了 wiki 页面：已同步进站点，Quartz 热重建后浏览器会自动刷新。
            flushType(false)
            const names = (ev.files || []).map((f: string) => f.replace(/\.md$/, "")).join("、")
            streamConv!.msgs.push({ role: "tool", tool: { id: "sync-" + Date.now(), name: "站点已同步", input: {}, result: `更新了 ${ev.count} 个页面${names ? "：" + names : ""}${ev.count > 8 ? " …" : ""}。站点正在热重建，稍候自动刷新即可看到。`, done: true } })
            render(); saveState(state)
          }
          else if (ev.type === "error") { flushType(false); streamConv!.msgs.push({ role: "error", text: ev.message }); render(); saveState(state) }
        }
      }
    } catch (e: any) {
      if (e?.name === "AbortError") streamConv?.msgs.push({ role: "tool", tool: { id: "x", name: "已停止", input: {}, done: true } })
      else streamConv?.msgs.push({ role: "error", text: (e?.message ? e.message + " — " : "") + "连不上本地对话服务。重跑 tools/view.sh（它会自动拉起桥接），或单独跑 tools/chat.sh。" })
    } finally {
      controller = null
      setBusy(false)
      render()
      saveState(state)
    }
  }

  const onNew = () => startConv()
  const onFork = () => {
    const c = cur()
    if (!c.sessionId) { startConv(); return } // nothing to fork yet
    startConv(c.sessionId, (c.title || "对话") + " ·分支")
  }
  const onKey = (e: KeyboardEvent) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send() } }
  const onInput = () => {
    input!.style.height = "auto"; input!.style.height = Math.min(input!.scrollHeight, 160) + "px"
    const m = input!.value.match(/^\/([\w-]*)$/)
    if (m) showSlash(m[1])
    else if (openMenuEl?.classList.contains("ew-slash")) closeMenu()
  }

  const vswHandlers = vswEls.map((b) => {
    const h = () => switchView((b.dataset.v as "page" | "claude") || "page")
    b.addEventListener("click", h)
    return [b, h] as const
  })
  resetBtn?.addEventListener("click", onNew)
  forkBtn?.addEventListener("click", onFork)
  sendBtn.addEventListener("click", send)
  input.addEventListener("keydown", onKey)
  input.addEventListener("input", onInput)
  input.addEventListener("paste", onPaste as any)
  modelEl?.addEventListener("click", onModelMenu)
  thinkEl?.addEventListener("click", onThinkMenu)
  permEl?.addEventListener("click", onPermMenu)
  mcpEl?.addEventListener("click", onMcpMenu)
  window.addCleanup?.(() => {
    vswHandlers.forEach(([b, h]) => b.removeEventListener("click", h))
    resetBtn?.removeEventListener("click", onNew)
    forkBtn?.removeEventListener("click", onFork)
    sendBtn.removeEventListener("click", send)
    input.removeEventListener("keydown", onKey)
    input.removeEventListener("input", onInput)
    input.removeEventListener("paste", onPaste as any)
    modelEl?.removeEventListener("click", onModelMenu)
    thinkEl?.removeEventListener("click", onThinkMenu)
    permEl?.removeEventListener("click", onPermMenu)
    mcpEl?.removeEventListener("click", onMcpMenu)
    closeMenu()
  })

  renderAttach()
  renderTabs()
  render()
  switchView(state.view)
}

document.addEventListener("nav", setup)
