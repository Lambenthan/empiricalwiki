import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
// @ts-ignore — bundled by esbuild at build time
import script from "./scripts/ewchat.inline"
import style from "./styles/ewchat.scss"

// Lives in the RIGHT sidebar. A segmented toggle switches the rail between the
// page views (Graph / ToC / Backlinks — our siblings) and the Claude chat, which
// fills the sticky full-height sidebar when active. Behaviour in ewchat.inline.ts.
export default (() => {
  const EwChat: QuartzComponent = ({ displayClass }: QuartzComponentProps) => {
    return (
      <div id="ew-chat-root" class={displayClass ?? ""}>
        <div id="ew-view-switch" role="tablist">
          <button class="ew-vsw is-active" data-v="page">页面</button>
          <button class="ew-vsw" data-v="claude">
            <span class="ew-spark-sm" aria-hidden="true"></span>Claude
          </button>
        </div>

        <aside id="ew-chat-panel" aria-label="Claude 对话">
          <header id="ew-chat-header">
            <div class="ew-chat-id">
              <span class="ew-avatar" aria-hidden="true"></span>
              <div class="ew-chat-meta">
                <span class="ew-chat-name">Claude Code</span>
                <span class="ew-chat-sub"><span class="ew-chat-dot"></span><span id="ew-chat-status">本地 · 工作目录为本 wiki</span></span>
              </div>
            </div>
            <div class="ew-chat-actions">
              <button id="ew-chat-fork" title="从当前会话分支" aria-label="分支">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="6" r="2.5"/><circle cx="6" cy="18" r="2.5"/><circle cx="18" cy="8" r="2.5"/><path d="M6 8.5v7M6 15.5C6 11 10 12 14 9.5"/></svg>
              </button>
              <button id="ew-chat-reset" title="新对话" aria-label="新对话">
                <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14M5 12h14"/></svg>
              </button>
            </div>
          </header>

          <div id="ew-chat-tabs"></div>
          <div id="ew-chat-log"></div>

          <div id="ew-chat-inputbar">
            <div id="ew-chat-attach"></div>
            <div id="ew-chat-inputwrap">
              <textarea id="ew-chat-input" rows={1} placeholder="问点什么，或用 /ask、/ingest 等 skill…"></textarea>
              <button id="ew-chat-send" aria-label="发送" title="发送">
                <svg class="ew-ic-send" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5M5 12l7-7 7 7"/></svg>
                <svg class="ew-ic-stop" viewBox="0 0 24 24" width="15" height="15" fill="currentColor"><rect x="6" y="6" width="12" height="12" rx="2"/></svg>
              </button>
            </div>
            <div id="ew-chat-footer">
              <button id="ew-chat-model" class="ew-foot-pill ew-foot-btn">本地默认</button>
              <button id="ew-chat-think" class="ew-foot-pill ew-foot-btn">思考: 关</button>
              <button id="ew-chat-perm" class="ew-foot-pill ew-foot-btn ew-foot-yolo">完全权限</button>
              <button id="ew-chat-mcp" class="ew-foot-pill ew-foot-btn ew-gone">MCP</button>
              <span class="ew-foot-grow"></span>
              <span id="ew-chat-ctx" class="ew-foot-ctx"></span>
            </div>
          </div>
        </aside>
      </div>
    )
  }

  EwChat.afterDOMLoaded = script
  EwChat.css = style
  return EwChat
}) satisfies QuartzComponentConstructor
