# Obsidian 配置说明

这个目录存放本项目作者使用的 Obsidian vault 配置子集，可以拷贝到自己的 vault `.obsidian/` 目录里直接套用。

## 配置文件清单

| 文件 | 作用 |
|:---|:---|
| `app.json` | Obsidian 通用偏好（启动选项、链接行为等） |
| `appearance.json` | 主题、字体、CSS 片段启用列表 |
| `core-plugins.json` | 启用的内置核心插件 |
| `community-plugins.json` | 启用的社区插件清单 |
| `hotkeys.json` | 自定义快捷键 |
| `graph.json` | Graph View 显示偏好 |
| `themes/Cupertino/` | 推荐主题（Cupertino），淡雅风格，对中文友好 |
| `snippets/line-space.css` | 加宽中文段落行距 |
| `snippets/sidenote-callout.css` | 把 callout 渲染成右侧边注的样式 |

## 推荐安装的社区插件清单

社区插件本身请通过 Obsidian 内置的"第三方插件市场"（Settings → Community plugins → Browse）按名字搜索安装。下面是作者使用的清单：

| Plugin ID | 用途 |
|:---|:---|
| `dataview` | 把 wiki 内容当数据库查询，写综述时聚合页面 |
| `templater-obsidian` | 模板引擎，用于新建条目时套用 frontmatter |
| `obsidian-excalidraw-plugin` | 在 vault 内画 Excalidraw 图（架构图、流程图） |
| `notebook-navigator` | 类 Bear 的笔记本导航视图，比默认侧栏更好用 |
| `obsidian-icon-folder` | 给目录加图标，区分实体类型 |
| `pdf-plus` | PDF 增强，支持 highlight、annotation 跨笔记 |
| `enhanced-annotations` | 标注高亮的扩展 |
| `highlightr-plugin` | 多色高亮 |
| `obsidian-git` | 在 Obsidian 内做 git commit/push（可选，如果需要版本控制 vault） |
| `obsidian-custom-attachment-location` | 自定义附件存放位置 |
| `advanced-canvas` | Obsidian Canvas 的功能增强 |
| `show-hidden-files` | 在文件浏览器里显示 dotfiles |
| `terminal` | 在 Obsidian 内开终端（可选） |
| `vscode-editor` | 把笔记当代码文件用 VSCode 风格编辑（可选） |
| `better-export-pdf` | 增强 PDF 导出 |
| `docxer` | docx 导入导出 |
| `univer` | 在 Obsidian 内嵌入电子表格 |
| `wordwise` | 写作辅助 |
| `obsidian-weread-plugin` | 微信读书笔记同步（可选） |
| `claudian` | 在 Obsidian 内调用 Claude（需要自行配置 API key） |

## 使用步骤

1. 把自己的 Obsidian vault 关掉
2. 打开 vault 目录下的 `.obsidian/`（隐藏目录，需要先在系统里设置显示隐藏文件）
3. 把本目录里的 6 个 JSON 配置文件、`themes/Cupertino/` 目录、`snippets/` 目录拷过去（如果已存在请先备份）
4. 按上面"推荐插件清单"在 Obsidian 内安装社区插件
5. 重新打开 vault，启用 community plugins 时信任作者
6. 按需在 Settings → Appearance 里启用 Cupertino 主题与 CSS 片段

## 注意事项

- **本目录不包含任何插件代码本身**。所有插件都需要通过 Obsidian 官方市场自行安装，以保证版本最新且符合各插件的版权约定。
- **本目录不包含 `text-generator.json`、各插件 `data.json`、`workspace.json`**。这些文件含有作者的个人配置（API key、远程仓库地址、本地路径等），不适合公开。读者按上面步骤安装插件后，相应的 data.json 由插件自动生成并由读者自行配置。
- **本目录不含 `claudian` 插件的配置**。Claudian 调用 Claude API 需要 key，请到 [Anthropic Console](https://console.anthropic.com/) 申请后在插件设置里填入。
