---
description: Convert an empirical design into a Stata execution plan or optional do-file skeleton covering merge, variable construction, regressions, robustness, and exports
argument-hint: "<empirical-design-path-or-topic> [--write-do]"
---

# /stata-plan

Read the selected empirical design, `wiki/variables/*.md`, `wiki/datasets/*.md`, `wiki/models/*.md`, robustness and heterogeneity pages, plus local `.do`, `.dta`, `.xlsx`, dictionaries, and READMEs.

By default, create `wiki/outputs/stata-plan-{slug}-{YYYY-MM-DD}.md` with:

1. Input data
2. Merge keys and merge order
3. Sample filters
4. Variable construction
5. Winsorization and missing-value handling
6. Descriptive statistics
7. Correlations
8. Baseline regressions
9. Mechanism tests
10. Heterogeneity tests
11. Robustness checks
12. Table exports
13. Verification checklist

Only when the user passes `--write-do`, also create `wiki/outputs/stata-plan-{slug}-{YYYY-MM-DD}.do`.

Constraints:

- Never overwrite existing user `.do` files.
- Do not invent final variable names; use placeholders and mark `needs confirmation` when names are uncertain.
- Include checks for sample size, merge results, missingness, and variable distributions.
