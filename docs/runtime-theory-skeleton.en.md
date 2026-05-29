# Theory-Modeling Universal Skeleton

> The design baseline for the theory layer. Any formal economic model — game theory, general equilibrium, contract theory, mechanism design, macro DSGE, asset pricing, industrial organization — shares one logical skeleton. When ingesting a theory paper, extract against these 6 fixed slots.
>
> The "fixed template" of empirical papers (variables/data/model/identification) is **paradigm-bound**; these 6 theory slots are **logical grammar** and travel further across subfields. The hard part is not structure but **faithful filling**: formal statements must be quoted verbatim, never paraphrased.

---

## The 6 fixed slots → page-type mapping

| # | Slot | What it holds | Where it lands |
|---|------|---------------|----------------|
| ① | **Environment / primitives** | who (players), what they can do (actions/strategies), what they want (preferences/payoffs), what they know (information), when (timing), constraints (technology/feasibility) | `assumptions/` + paper page `## Model Environment` |
| ② | **Solution concept** | Nash / subgame perfect / perfect Bayesian / competitive equilibrium / rational-expectations equilibrium ... | `foundations/` (reusable, terminal node) |
| ③ | **Results** | propositions/theorems/lemmas: existence, characterization, uniqueness, welfare, comparative statics | `propositions/` |
| ④ | **Proofs** | proof technique: fixed point, backward induction, envelope theorem, revealed preference, counterexample ... | `proof_technique` field on `propositions/` |
| ⑤ | **Comparative statics** | how endogenous variables move with parameters (the model's "prediction engine") | `propositions/` field (proposition_type: comparative_statics) or `## Comparative Statics` body |
| ⑥ | **Testable implications** | sign predictions the model yields that can be taken to data | `hypotheses/` ← **the theory↔empirics bridge** |

Slot ① splits model primitives into `assumptions/` pages; the overall environment narrative goes in the paper page's `## Model Environment`. ②③④⑤⑥ each have their mapping.

---

## Extraction order (the fixed theory-ingest flow)

1. **Environment/primitives** → read the model-setup section, split into `assumptions/`, write `## Model Environment` on the paper page
2. **Solution concept** → identify the equilibrium notion, link to or create a `foundations/` page
3. **Results** → one `propositions/` page per proposition/theorem/lemma, `formal_statement` quoted **verbatim**, `conditions` explicit
4. **Proofs** → fill `proof_technique` (write "未报告" if not found; do not guess)
5. **Comparative statics** → into `propositions/` fields or body
6. **Testable implications** → land in `hypotheses/`, write the forward edge `predicts` (proposition → hypothesis)

---

## Bridge edges: theory and empirics on one graph

```
theory-paper --assumes-->              assumptions/X
theory-paper --proves-->               propositions/P
theory-paper --formalizes_mechanism--> mechanisms/M   (shared with empirics)
propositions/P --predicts-->           hypotheses/H   (theory side)
empirical-paper --tests_hypothesis-->  hypotheses/H   (empirical side, existing edge)
empirical-paper --tests_mechanism-->   mechanisms/M   (empirical side, existing edge)
theory-paper --derived_from-->         foundations/F
```

Once connected, a single `mechanisms/` or `hypotheses/` page carries both the **theory side** (who built the model) and the **empirical side** (who tested it). You can ask the graph: "for this mechanism, who proved it theoretically, who tested it empirically, and do they agree?" — a view a pure empirical wiki cannot give.

Edge semantics and confidence rules live in `tools/_schemas.py` (`EDGE_TYPE_SPECS`, workflow `theory_ingest`): `assumes`/`proves` are definite structural facts with no confidence; `formalizes_mechanism`/`predicts` are judgments and require `confidence: high|medium|low`.

---

## Boundary

- This skeleton covers **analytical/formal theory**. Pure computational agent-based / simulation models are experiment-like and belong in `experiments/`, not `propositions/`.
- Pure axiomatic decision theory (representation theorems) also fits: slot ① = preference axioms, ③ = the representation theorem, leave slots like timing empty.
- `propositions/` must not be conflated with `claims/`: a proposition is a proven formal result; a claim is a confidence-weighted empirical assertion.
