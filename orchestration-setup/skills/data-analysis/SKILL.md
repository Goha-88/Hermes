---
name: data-analysis
description: |
  Analyze numbers and build charts — unit-economics, MRR and revenue forecasts,
  cohort/funnel analysis, financial models, runway, KPI dashboards. Use when
  asked to calculate, model, forecast, compare, or visualize data.
---

# Data analysis & financial modeling

Use code execution (`pandas`, `numpy`, `matplotlib` available). Never eyeball
numbers — compute them.

Workflow:
1. Get the data (pasted, a file, or pulled via a tool). State assumptions explicitly.
2. Write python: compute the metrics, then plot with matplotlib and save the chart as PNG.
3. Run it. Report the **key number first** (the answer), then the chart, then the method.
4. For models (MRR, unit-economics, runway, LTV/CAC) show the formula and assumptions so they are auditable and re-runnable.

Conventions:
- **Outcome first** — lead with the answer/number; detail and caveats after.
- Make assumptions explicit and editable (a short "rerun inputs" block).
- Send charts as image files; offer an Excel version via the `documents` skill.
- If a paid model was used for reasoning, surface the cost.
