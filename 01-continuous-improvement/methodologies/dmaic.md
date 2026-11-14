# DMAIC

**Define, Measure, Analyze, Improve, Control.** DMAIC is the Six Sigma cycle for improving an existing process that falls short of what the customer needs. To design a new process instead, use [DMADV](../../03-design-and-engineering/methodologies/dfss-dmadv.md). For background, see [Six Sigma](six-sigma.md).

Each phase ends at a **tollgate**: a review where the Champion confirms the phase's outputs before the team moves on. Use the [DMAIC tollgate checklist](../templates-and-procedures/dmaic-tollgate-checklist.md).

| Phase | Key question | Main activities | Typical tools | Outputs (tollgate evidence) |
| --- | --- | --- | --- | --- |
| **Define** | What is the problem, and why does it matter? | State the system, the voice of the customer (VOC), the customer's requirements, and the project goals. Scope the project and name the team. | Project charter, SIPOC / COPIS, VOC interviews, CTQ tree, cost-benefit analysis | Signed [project charter](../templates-and-procedures/dmaic-project-charter.md), SIPOC, CTQs with targets |
| **Measure** | How does the process perform now? | Measure the key aspects of the current process, collect data, confirm the measurement system can be trusted, and calculate the as-is capability. | Process map, check sheets, data collection plan, MSA / Gauge R&R, histograms, run charts, process capability, rolled throughput yield | Validated baseline (DPMO, sigma level, Cpk), data collection plan, MSA results |
| **Analyze** | What causes the problem? | Find and verify cause and effect. Make sure every plausible factor has been considered, then confirm the root cause(s). | Fishbone (Ishikawa), 5 Whys, Pareto, stratification, hypothesis tests, regression, FMEA, value stream map | Root causes verified with data, and the size of their effect |
| **Improve** | How do we fix it, and does the fix work? | Develop, test, and optimize solutions. Run pilots to show the new capability. | Design of experiments (DOE), poka-yoke (mistake-proofing), standard work, pick chart, Taguchi methods, pilot runs | Piloted solution, new capability, implementation plan |
| **Control** | How do we keep the gain? | Hold the process on target with statistical process control, production boards, visual workplaces, and ongoing monitoring. Hand the process over to its owner. Repeat until the target quality is reached. | Control charts (SPC), control plan, standard work, 5S, visual management, response plan | Control plan, SPC in place, process owner sign-off, verified financial results |

## Phase notes

### Define
- Write the problem in measurable terms ("Scrap on line 3 is 4.2% against a 1% target, costing $X a year"). Don't name a cause or a solution here.
- Bound the scope: name the first and last process steps, and say what is in scope and what is out.
- Translate the voice of the customer into Critical-To-Quality (CTQ) characteristics, each with a specification.

### Measure
- Validate the measurement system before collecting baseline data. A noisy gauge hides real improvement.
- Record the baseline as DPMO, sigma level, and Cp/Cpk. See [Sigma levels and DPMO](../../02-quality-and-statistics/methodologies/sigma-levels-and-dpmo.md).

### Analyze
- Move from many possible causes (the fishbone) to a few verified ones, using data such as Pareto charts, stratification, and tests.
- Report the size of each effect, not only whether it is statistically significant.

### Improve
- Use designed experiments rather than changing one factor at a time.
- Prefer mistake-proofing and process design over inspection or retraining. See [Quality Systems (HOP)](../../07-quality-systems/) on why "train harder" rarely lasts.

### Control
- The control plan names who watches what, how often, with which chart, and what to do when a signal appears.
- Close the project only after the gain has held for an agreed period.

## Variants

- **RDMAIC** adds a **Recognize** step at the front, to pick the right problem to work on first.
- **DMAICS** (practitioner usage) adds **Standardize** at the end, to roll the fix out to similar processes.
- **PDCA / PDSA** is the shorter Deming cycle that DMAIC grew from. It suits small, fast improvements.

---

**Source.** Based on the Wikipedia article [Six Sigma](https://en.wikipedia.org/wiki/Six_Sigma) and the references it cites, as of 2026-10-29, summarized in our own words and expanded with standard practitioner guidance. Wikipedia content is available under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
