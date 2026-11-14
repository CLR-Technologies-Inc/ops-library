# Operational Excellence Library

*Methods, frameworks, and tools for manufacturing, quality, and operational performance.*

A one-stop, publicly available library of templates and knowledge for operations and industrial engineering. It covers batch, discrete, job shop, and every other production mode. It is published by CLR Technologies Inc. and is a companion to [FoaMES](https://github.com/CLR-Technologies-Inc/foames).

## Library Organization

| Domain | Focus |
| --- | --- |
| [Continuous Improvement](01-continuous-improvement/) | Lean, Kaizen, 5S, VSM, DMAIC |
| [Quality & Statistics](02-quality-and-statistics/) | SPC, MSA, capability, DOE |
| [Design & Engineering](03-design-and-engineering/) | DFSS, DMADV, FMEA, QFD |
| [Production Systems](04-production-systems/) | OEE, TPM, Kanban, SMED |
| [Operations Management](05-operations-management/) | TOC, S&OP, capacity planning |
| [Standards & Playbooks](06-standards-and-playbooks/) | ISO, SOPs, templates, checklists |
| [Quality Systems (QA / QC)](07-quality-systems/) | QA, QC, Human & Organizational Performance (HOP) |

Each domain is split into **Methodologies** (structured approaches such as DMAIC or DFSS), **Tools** (control charts, fishbone diagrams, calculators), and **Templates & Procedures** (FMEA worksheets, control plans, standard work).

```
ops-library/
├── 01-continuous-improvement/
├── 02-quality-and-statistics/
├── 03-design-and-engineering/
├── 04-production-systems/
├── 05-operations-management/
├── 06-standards-and-playbooks/
└── 07-quality-systems/
    ├── methodologies/
    ├── tools/
    └── templates-and-procedures/
```

## Working tools

Working Six Sigma and SPC tools in Excel / LibreOffice, Python, and R are in [Quality & Statistics → Tools](02-quality-and-statistics/tools/). They cover capability, sigma level, control charts, Gauge R&R, DOE, hypothesis tests, Pareto, and FMEA. All three formats are checked against each other in CI. The [Six Sigma toolkit by DMAIC phase](01-continuous-improvement/tools/six-sigma-toolkit.md) shows which tool to use in which phase.

## Other strong naming options

| Name                                          | Acronym | Best application                            |
| --------------------------------------------- | ------- | ------------------------------------------- |
| Operational Excellence Library                | OEL     | Best overall, broad and professional        |
| Manufacturing & Operations Excellence Library | MOEL    | Explicit manufacturing focus                |
| Industrial Engineering Methods Library        | IEML    | Technical and engineering-focused           |
| Process Excellence Library                    | PEL     | Process optimization and improvement        |
| Operational Excellence Framework              | OEF     | Structured methodologies and standards      |
| Manufacturing Systems & Methods               | MSM     | Production engineering and systems          |
| Continuous Improvement Knowledge Base         | CIKB    | Learning, documentation, and best practices |
| Operations Engineering Toolkit                | OET     | Hands-on tools, calculations, and templates |

## Contributing

Each domain folder has a README with planned entries. To add content, place it in the matching `methodologies/`, `tools/`, or `templates-and-procedures/` subfolder and link it from that subfolder's README.

## License

[MIT](LICENSE) © CLR Technologies Inc.

---

Thanks ChatGPT! ;)
