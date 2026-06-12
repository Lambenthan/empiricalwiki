# 本地把 wiki 看成网站（Quartz）

把 `wiki/` 这堆 markdown 渲染成一个**带图谱、能搜索、能点链接**的本地网站。读的是同一份 `wiki/` 文件,只读、不改你的内容。适合分享展示、录课演示,比让别人装 Obsidian 省事。

底层用 [Quartz](https://quartz.jzhao.xyz/)(开源静态站生成器),已固定到稳定版 `v4.5.2`。

## 三步走(零基础)

**第 1 步:装 Node.js(只需一次)**
去 [nodejs.org](https://nodejs.org) 下载 LTS 版,一路下一步装好。验证:终端里输入 `node --version`,有版本号就行。

**第 2 步:在项目根目录跑一条命令**

```bash
tools/view.sh
```

- **首次**会自动克隆 Quartz、装依赖(几分钟,只有第一次慢),然后构建。
- 之后每次跑都很快。

**第 3 步:打开浏览器**
看到 `http://localhost:8080` 后,浏览器打开它。完事。按 `Ctrl-C` 退出预览。

## 你会看到什么

- **首页** = `wiki/index.md`,全 wiki 目录。
- **左侧** 文件树,按类型分(papers / assumptions / propositions / mechanisms …)。
- **右侧** 每页的反向链接(谁引用了它)。
- **图谱视图**:整张知识网,理论↔实证的桥一眼可见。
- **顶部搜索**:全文搜。
- **右栏「Claude」页签**:直接和你本地的 Claude Code 对话(见下节)。

## 网页里直接用 Claude Code(不用碰终端)

右栏顶部把「页面」切到「Claude」,就是一个完整的对话面板——背后是你**本地**的 Claude Code(同一个登录、同一套 skill),核心设计参考 [Claudian](https://github.com/YishenTu/claudian)(Obsidian 里嵌 Claude Code 的开源插件):

- 输入 `/ask 耐心资本有哪几种测法`、`/empirical-ingest raw/papers/xxx.pdf` 等任何 skill,或随便提问。
- 多标签、会话续接、从当前会话分支;底部可切模型、思考模式、权限档位(完全 / 逐步确认 / 只读计划)。
- Claude 需要你拍板时(选项题、计划确认),面板里直接点选,不用切终端。
- **写盘自动同步**:对话里 ingest 完论文,新页面会自动同步进站点并热重建,刷新即见。

前提:本机装好并登录了 Claude Code(`claude` 在 PATH 里)。没装时站点照常运行,只是只读;装好后重跑 `tools/view.sh` 即启用。对话服务只绑定 `127.0.0.1`,不对外。

## 其它用法

```bash
tools/view.sh           # 构建 + 本地预览(默认,自动拉起 Claude 对话桥接)
tools/view.sh --build   # 只构建,产物在 site/.quartz/public/(可上传到任意静态托管)
tools/view.sh --update  # 强制更新 Quartz 版本后再构建预览
tools/view.sh --no-chat # 只要只读站点,不启动对话桥接
tools/chat.sh           # 单独启动对话桥接(不常用,view.sh 已自动带起)
```

想发到公网:把 `site/.quartz/public/` 传到 GitHub Pages / Vercel / Netlify 即可(都免费)。

## 写内容时的一个坑:美元符号 `$`

Quartz 会把 `$...$` 当成数学公式(KaTeX)。所以正文里写**美元金额**要转义:写 `\$1`、`\$(1+r)`,不要写 `$1`。否则 `$` 之间的中文会被当公式渲染成乱码。

- 真正的公式:用 `$$...$$`(独立公式)或行内 `$...$`,正常。
- Stata 宏 `$controls`:放进 ``` 代码块 ``` 里就不受影响。

## 说明

- `site/` 整个目录是本地生成的(Quartz 克隆 + 依赖 + 构建产物),已被 `.gitignore` 忽略,不进仓库。每个人在自己机器上跑 `tools/view.sh` 各自生成。
- `wiki/graph/`、`wiki/outputs/`、`wiki/.obsidian/` 不会被渲染进站点。
- 站点只读;要改内容仍然改 `wiki/` 下的 markdown,或走 `/ingest`、`/theory-ingest` 等 skill,改完重跑 `tools/view.sh` 即可刷新。
