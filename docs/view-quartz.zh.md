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

## 其它用法

```bash
tools/view.sh           # 构建 + 本地预览(默认)
tools/view.sh --build   # 只构建,产物在 site/.quartz/public/(可上传到任意静态托管)
tools/view.sh --update  # 强制更新 Quartz 版本后再构建预览
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
