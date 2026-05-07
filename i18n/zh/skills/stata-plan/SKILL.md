---
description: 将实证研究设计转成 Stata 执行计划或 do 文件骨架，包含数据合并、变量构造、描述统计、回归和稳健性
argument-hint: "<empirical-design-path-or-topic> [--write-do]"
---

# /stata-plan

> 把 wiki 中的变量、数据和模型信息转成 Stata 层面的执行顺序。默认生成计划；只有用户传 `--write-do` 时才创建 `.do` 骨架。

## Workflow

### Step 1: Read Design and Data Context

读取：

- 指定的 `wiki/outputs/empirical-design-*.md`，或按 topic 匹配最近设计文档
- `wiki/variables/*.md`
- `wiki/datasets/*.md`
- `wiki/models/*.md`
- `wiki/robustness/*.md`
- `wiki/heterogeneity/*.md`
- 项目中的 `.do`、`.dta`、`.xlsx`、变量字典和 README

### Step 2: Produce Stata Execution Plan

输出结构：

```markdown
# Stata 执行计划

## 1. 输入数据
## 2. 主键与合并顺序
## 3. 样本筛选
## 4. 变量构造
## 5. 缩尾与缺失值处理
## 6. 描述性统计
## 7. 相关性分析
## 8. 基准回归
## 9. 机制检验
## 10. 异质性检验
## 11. 稳健性检验
## 12. 表格导出
## 13. 复核清单
```

每一步尽量写成 Stata 伪代码或代码块，但不要假造不存在的变量名。变量名不确定时用占位符并标记“需确认”。

### Step 3: Optional Do File

只有用户传 `--write-do` 时，创建：

```text
wiki/outputs/stata-plan-{slug}-{YYYY-MM-DD}.do
```

默认只写：

```text
wiki/outputs/stata-plan-{slug}-{YYYY-MM-DD}.md
```

### Step 4: Log

```bash
python3 tools/research_wiki.py log wiki "stata-plan | <topic> | output: outputs/<file>"
```

## Constraints

- 不覆盖用户已有 `.do` 文件。
- 不假设 Stata 包已经安装；需要 `reghdfe`、`esttab` 等时在计划里列出安装命令。
- 代码骨架必须保留复核点，如样本量检查、merge 结果检查、变量分布检查。
- 对中文路径和空格路径使用引号。
