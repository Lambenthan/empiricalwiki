#!/usr/bin/env node
// EmpiricalWiki chat bridge (Agent SDK core) — same core design as Claudian.
//
// Drives the LOCAL Claude Code via the official @anthropic-ai/claude-agent-sdk,
// which spawns your local `claude` binary (your subscription login, your model,
// your CLAUDE.md / .claude/skills / .mcp.json). Each browser message is one
// query() call resumed onto the same session, so it is multi-turn.
//
// Interactive tools work because we pass a `canUseTool` callback:
//   - AskUserQuestion / ExitPlanMode are routed to the browser; the panel renders
//     options, the user answers, and we resolve the callback with
//     { behavior:"allow", updatedInput:{...input, answers} } — exactly how
//     Claudian feeds the answer back into the live session.
//   - every other tool is auto-allowed (full permission), no prompts.
//
// Binds to 127.0.0.1 only.
//
// Env: EW_CHAT_PORT (8788), CLAUDE_BIN (resolved claude path)

import { createServer } from "node:http"
import { randomUUID } from "node:crypto"
import { readFileSync, readdirSync, statSync, mkdirSync, copyFileSync, existsSync } from "node:fs"
import { fileURLToPath } from "node:url"
import { dirname, resolve, join, relative } from "node:path"
import { query } from "@anthropic-ai/claude-agent-sdk"

const __dirname = dirname(fileURLToPath(import.meta.url))
const PROJECT_ROOT = resolve(__dirname, "..", "..")
const PORT = Number(process.env.EW_CHAT_PORT || 8788)
const CLAUDE_BIN = process.env.CLAUDE_BIN || "claude"
const WIKI_DIR = resolve(PROJECT_ROOT, "wiki")
const SITE_CONTENT = resolve(PROJECT_ROOT, "site", ".quartz", "content")
const SYNC_EXCLUDE = new Set(["graph", "outputs", ".obsidian", ".trash", ".claude", ".checkpoints"])

// The site is a build-time snapshot of wiki/. When a skill writes pages during
// a chat turn, copy the changed .md files into Quartz's content/ — its --serve
// watcher then hot-rebuilds and reloads the browser. Without this, users ingest
// a paper and wonder why nothing shows up.
function syncWikiChanges(sinceMs) {
  if (!existsSync(SITE_CONTENT) || !existsSync(WIKI_DIR)) return []
  const changed = []
  const walk = (dir) => {
    for (const name of readdirSync(dir)) {
      const p = join(dir, name)
      const rel = relative(WIKI_DIR, p)
      const top = rel.split(/[\\/]/)[0]
      if (SYNC_EXCLUDE.has(top)) continue
      let st
      try { st = statSync(p) } catch { continue }
      if (st.isDirectory()) walk(p)
      else if (name.endsWith(".md") && st.mtimeMs >= sinceMs - 2000) {
        try {
          const dest = join(SITE_CONTENT, rel)
          mkdirSync(dirname(dest), { recursive: true })
          copyFileSync(p, dest)
          changed.push(rel)
        } catch {}
      }
    }
  }
  try { walk(WIKI_DIR) } catch {}
  return changed
}

const sessions = new Map() // tabId -> sdk session_id (for resume)
const aborts = new Map() // tabId -> AbortController (for stop)
const askResolvers = new Map() // askId -> (answers|null) => void  (AskUserQuestion / ExitPlanMode)

function send(res, obj) {
  res.write(`data: ${JSON.stringify(obj)}\n\n`)
}
function cors(res, req) {
  res.setHeader("Access-Control-Allow-Origin", req.headers.origin || "*")
  res.setHeader("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
  res.setHeader("Access-Control-Allow-Headers", "Content-Type")
}
function readBody(req) {
  return new Promise((res2) => {
    let raw = ""
    req.on("data", (c) => {
      raw += c
      if (raw.length > 4_000_000) req.destroy()
    })
    req.on("end", () => {
      try {
        res2(JSON.parse(raw || "{}"))
      } catch {
        res2(null)
      }
    })
  })
}
function toolSummary(name, input) {
  if (!input) return name
  if (input.command) return String(input.command).slice(0, 200)
  if (input.file_path) return String(input.file_path)
  if (input.path) return String(input.path)
  if (input.pattern) return String(input.pattern)
  if (input.url) return String(input.url)
  return name
}
function toolResultText(content) {
  if (typeof content === "string") return content
  if (Array.isArray(content))
    return content
      .map((b) => (typeof b === "string" ? b : b?.text || ""))
      .join("")
      .trim()
  return ""
}

async function handleChat(req, res, body) {
  const { tabId, prompt, model, permission, thinking, forkFrom, images, disabledMcp } = body || {}
  if (!tabId || !prompt) {
    res.writeHead(400, { "Content-Type": "application/json" })
    res.end(JSON.stringify({ error: "tabId and prompt required" }))
    return
  }
  res.writeHead(200, {
    "Content-Type": "text/event-stream",
    "Cache-Control": "no-cache",
    Connection: "keep-alive",
  })

  const prev = aborts.get(tabId)
  if (prev) {
    try {
      prev.abort()
    } catch {}
  }
  const abortController = new AbortController()
  aborts.set(tabId, abortController)

  // AskUserQuestion / ExitPlanMode → ask the browser, await the answer.
  const ask = (kind, payload, signal) => {
    const askId = randomUUID()
    send(res, { type: "ask", kind, askId, ...payload })
    return new Promise((resolveAsk) => {
      askResolvers.set(askId, resolveAsk)
      signal?.addEventListener("abort", () => {
        if (askResolvers.has(askId)) {
          askResolvers.delete(askId)
          resolveAsk(null)
        }
      })
    })
  }

  const canUseTool = async (name, input, opts) => {
    if (name === "AskUserQuestion") {
      const questions = Array.isArray(input?.questions) ? input.questions : []
      for (const q of questions) if (q && typeof q === "object" && !("isOther" in q)) q.isOther = true
      const answers = await ask("question", { questions }, opts?.signal)
      if (answers === null) return { behavior: "deny", message: "用户取消了回答。", interrupt: true }
      return { behavior: "allow", updatedInput: { ...input, answers } }
    }
    if (name === "ExitPlanMode") {
      const decision = await ask("plan", { plan: input?.plan || "" }, opts?.signal)
      if (decision === null) return { behavior: "deny", message: "用户取消。", interrupt: true }
      if (decision && decision.type === "feedback")
        return { behavior: "deny", message: String(decision.text || "继续完善计划"), interrupt: false }
      return { behavior: "allow", updatedInput: input }
    }
    // "逐步确认" mode: ask the browser to allow/deny each tool.
    if (permission === "ask") {
      const decision = await ask("permission", { tool: name, summary: toolSummary(name, input) }, opts?.signal)
      if (decision && decision.type === "allow") {
        if (decision.always)
          return {
            behavior: "allow",
            updatedInput: input,
            updatedPermissions: [{ type: "addRules", behavior: "allow", rules: [{ toolName: name }], destination: "session" }],
          }
        return { behavior: "allow", updatedInput: input }
      }
      return { behavior: "deny", message: "用户拒绝了该操作。", interrupt: false }
    }
    return { behavior: "allow", updatedInput: input } // 完全权限 / 只读(plan 已限制)
  }

  const resume = sessions.get(tabId)
  const effectiveResume = resume || forkFrom || undefined
  const doFork = !resume && !!forkFrom
  const turn = { deltaChars: 0 }
  const turnStartMs = Date.now()
  const permMode = permission === "plan" ? "plan" : "default"
  const disallowed = Array.isArray(disabledMcp) ? disabledMcp.map((n) => `mcp__${n}`) : []

  // images → structured user message via a one-shot async-iterable prompt
  let promptArg = prompt
  if (Array.isArray(images) && images.length) {
    promptArg = (async function* () {
      yield {
        type: "user",
        message: {
          role: "user",
          content: [
            ...images.map((im) => ({
              type: "image",
              source: { type: "base64", media_type: im.mime || "image/png", data: im.data },
            })),
            { type: "text", text: prompt },
          ],
        },
        parent_tool_use_id: null,
        session_id: "",
        uuid: "u-" + randomUUID(),
      }
    })()
  }

  const onClose = () => {
    try {
      abortController.abort()
    } catch {}
  }
  res.on("close", onClose)

  try {
    const q = query({
      prompt: promptArg,
      options: {
        cwd: PROJECT_ROOT,
        pathToClaudeCodeExecutable: CLAUDE_BIN,
        settingSources: ["user", "project"], // load CLAUDE.md + .claude/skills + .mcp.json
        includePartialMessages: true,
        permissionMode: permMode, // canUseTool decides allow/deny per the chosen mode
        canUseTool,
        abortController,
        resume: effectiveResume,
        ...(doFork ? { forkSession: true } : {}),
        ...(model ? { model } : {}),
        ...(thinking ? { thinking: { type: "adaptive" } } : {}),
        ...(disallowed.length ? { disallowedTools: disallowed } : {}),
      },
    })

    for await (const m of q) {
      if (m.type === "system" && m.subtype === "init") {
        if (m.session_id) sessions.set(tabId, m.session_id)
        send(res, { type: "session", sessionId: m.session_id })
        if (m.model) send(res, { type: "model", model: m.model })
      } else if (m.type === "stream_event" && m.event) {
        const ev = m.event
        if (ev.type === "content_block_delta" && ev.delta?.type === "text_delta" && ev.delta.text) {
          turn.deltaChars += ev.delta.text.length
          send(res, { type: "delta", content: ev.delta.text })
        } else if (ev.type === "content_block_delta" && ev.delta?.type === "thinking_delta" && ev.delta.thinking) {
          send(res, { type: "think_delta", content: ev.delta.thinking })
        } else if (ev.type === "content_block_start" && ev.content_block?.type === "thinking") {
          send(res, { type: "think_start" }) // thinking happened (content may be encrypted/not exposed)
        }
      } else if (m.type === "assistant" && m.message?.content) {
        for (const b of m.message.content) {
          if (b.type === "text" && b.text) {
            if (turn.deltaChars === 0) send(res, { type: "delta", content: b.text })
          } else if (b.type === "tool_use") {
            send(res, { type: "tool", id: b.id, name: b.name, input: b.input })
          }
        }
        turn.deltaChars = 0
        send(res, { type: "turn_end" })
      } else if (m.type === "user" && m.message?.content) {
        const blocks = Array.isArray(m.message.content) ? m.message.content : []
        for (const b of blocks) {
          if (b.type === "tool_result") {
            send(res, {
              type: "tool_result",
              id: b.tool_use_id,
              isError: !!b.is_error,
              content: toolResultText(b.content).slice(0, 4000),
            })
          }
        }
      } else if (m.type === "result") {
        if (m.session_id) sessions.set(tabId, m.session_id)
        const u = m.usage || {}
        const used =
          (u.input_tokens || 0) +
          (u.output_tokens || 0) +
          (u.cache_read_input_tokens || 0) +
          (u.cache_creation_input_tokens || 0)
        let ctxWindow = 0
        for (const k in m.modelUsage || {}) ctxWindow = Math.max(ctxWindow, m.modelUsage[k]?.contextWindow || 0)
        send(res, {
          type: "result",
          subtype: m.subtype,
          cost: m.total_cost_usd,
          durationMs: m.duration_ms,
          usedTokens: used,
          contextWindow: ctxWindow,
        })
      }
    }
  } catch (e) {
    if (e?.name !== "AbortError") send(res, { type: "error", message: String(e?.message || e) })
  } finally {
    try {
      const changed = syncWikiChanges(turnStartMs)
      if (changed.length)
        send(res, { type: "wiki_synced", count: changed.length, files: changed.slice(0, 8) })
    } catch {}
    res.off("close", onClose)
    if (aborts.get(tabId) === abortController) aborts.delete(tabId)
    send(res, { type: "done" })
    res.end()
  }
}

const server = createServer(async (req, res) => {
  cors(res, req)
  if (req.method === "OPTIONS") {
    res.writeHead(204)
    res.end()
    return
  }
  const url = new URL(req.url, `http://${req.headers.host}`)

  if (req.method === "GET" && url.pathname === "/api/mcp") {
    let servers = []
    try {
      const j = JSON.parse(readFileSync(resolve(PROJECT_ROOT, ".mcp.json"), "utf8"))
      servers = Object.keys(j.mcpServers || {})
    } catch {}
    res.writeHead(200, { "Content-Type": "application/json" })
    res.end(JSON.stringify({ servers }))
    return
  }
  if (req.method === "GET" && url.pathname === "/api/health") {
    res.writeHead(200, { "Content-Type": "application/json" })
    res.end(JSON.stringify({ ok: true, project: PROJECT_ROOT, permission: "full", core: "agent-sdk" }))
    return
  }
  if (req.method === "POST" && url.pathname === "/api/chat") {
    const body = await readBody(req)
    if (!body) {
      res.writeHead(400)
      res.end()
      return
    }
    return handleChat(req, res, body)
  }
  if (req.method === "POST" && url.pathname === "/api/answer") {
    const body = await readBody(req)
    const r = body && askResolvers.get(body.askId)
    if (r) {
      askResolvers.delete(body.askId)
      r(body.answers ?? body.decision ?? null)
    }
    res.writeHead(200, { "Content-Type": "application/json" })
    res.end(JSON.stringify({ ok: !!r }))
    return
  }
  if (req.method === "POST" && url.pathname === "/api/reset") {
    const body = await readBody(req)
    if (body?.tabId) {
      sessions.delete(body.tabId)
      const a = aborts.get(body.tabId)
      if (a) {
        try {
          a.abort()
        } catch {}
      }
    }
    res.writeHead(200, { "Content-Type": "application/json" })
    res.end(JSON.stringify({ ok: true }))
    return
  }
  res.writeHead(404)
  res.end()
})

server.listen(PORT, "127.0.0.1", () => {
  console.log(`▶ EmpiricalWiki chat bridge (agent-sdk)  http://127.0.0.1:${PORT}`)
  console.log(`  project: ${PROJECT_ROOT}`)
  console.log(`  claude : ${CLAUDE_BIN}`)
  console.log(`  绑定 127.0.0.1，仅本地。Ctrl-C 退出。`)
})
