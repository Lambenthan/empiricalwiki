import { query } from "@anthropic-ai/claude-agent-sdk"

const CLAUDE = "/Applications/cmux.app/Contents/Resources/bin/claude"
console.log("ANTHROPIC_API_KEY set?", !!process.env.ANTHROPIC_API_KEY)

let askFired = false
const q = query({
  prompt: "请调用 AskUserQuestion 工具问我：喜欢苹果还是香蕉。只问这一个问题，不要做别的。",
  options: {
    cwd: "/tmp",
    pathToClaudeCodeExecutable: CLAUDE,
    permissionMode: "default",
    settingSources: [],
    canUseTool: async (name, input) => {
      console.log(">>> canUseTool:", name, "input keys:", Object.keys(input || {}))
      if (name === "AskUserQuestion") {
        askFired = true
        console.log(">>> AskUserQuestion input:", JSON.stringify(input).slice(0, 400))
        // simulate the user's answer the Claudian way
        return { behavior: "allow", updatedInput: { ...input, answers: { "0": "苹果" } } }
      }
      return { behavior: "allow", updatedInput: input }
    },
  },
})

try {
  for await (const m of q) {
    if (m.type === "system" && m.subtype === "init") console.log("INIT model=", m.model, "session=", m.session_id?.slice(0,8))
    else if (m.type === "assistant") {
      for (const b of m.message?.content || []) {
        if (b.type === "text") console.log("TEXT:", b.text.slice(0, 120))
        else if (b.type === "tool_use") console.log("TOOL_USE:", b.name)
      }
    } else if (m.type === "result") console.log("RESULT:", m.subtype, "askFired=", askFired)
  }
} catch (e) {
  console.log("ERROR:", e.message)
}
