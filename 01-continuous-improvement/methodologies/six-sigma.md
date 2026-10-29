# Six Sigma

Six Sigma is a data-driven approach to process improvement. It aims to find and remove the causes of defects and to reduce variation in manufacturing and business processes. Projects are run by trained practitioners (the "belts") through a defined sequence of phases, and each project has a measurable target, usually stated in financial or customer terms.

Related pages in this library:

- [DMAIC](dmaic.md): the Six Sigma cycle for improving an existing process
- [DFSS and DMADV](../../03-design-and-engineering/methodologies/dfss-dmadv.md): the Six Sigma cycle for designing a new product or process
- [Six Sigma roles and belts](six-sigma-roles-and-belts.md)
- [Sigma levels, DPMO, and the 1.5σ shift](../../02-quality-and-statistics/methodologies/sigma-levels-and-dpmo.md)
- [Six Sigma toolkit by phase](../tools/six-sigma-toolkit.md)
- [DMAIC project charter](../templates-and-procedures/dmaic-project-charter.md) and [DMAIC tollgate checklist](../templates-and-procedures/dmaic-tollgate-checklist.md)

## Where the name comes from

The name comes from statistical quality control. Sigma (σ) is the standard deviation of a process. A process runs "at six sigma" when six standard deviations fit between the process mean and the nearest specification limit. By convention, and after allowing for long-term drift, that works out to about **3.4 defects per million opportunities (DPMO)**. See [Sigma levels, DPMO, and the 1.5σ shift](../../02-quality-and-statistics/methodologies/sigma-levels-and-dpmo.md) for the arithmetic and its caveats.

## History

| Year | Event |
| --- | --- |
| 1986 | Engineer Bill Smith introduces Six Sigma at Motorola, which sets a "six sigma" goal for its manufacturing. |
| 1991 | Motorola registers "Six Sigma" as a U.S. service mark (June 11). |
| 1993 | Motorola registers "Six Sigma" as a trademark (December 28). |
| 1995 | Jack Welch makes Six Sigma central to General Electric's strategy. Honeywell (AlliedSignal) is another early adopter. |
| 1998 | GE reports $350 million in savings. The figure later passes $1 billion. |
| Late 1990s | About two-thirds of Fortune 500 companies have begun Six Sigma programs. |
| 2000s | Practitioners combine it with Lean manufacturing to form **Lean Six Sigma**. |
| 2005 | Motorola attributes more than $17 billion in savings to Six Sigma. |
| 2011 | ISO publishes **ISO 13053:2011**, the first international standard for the Six Sigma process. |

## Core principles

Six Sigma rests on three assertions:

1. Stable, predictable process results matter to business success, which in practice means reducing variation.
2. Manufacturing and business processes have characteristics that can be defined, measured, analyzed, improved, and controlled.
3. Lasting quality improvement needs commitment from the whole organization, and most of all from top management.

Three things set it apart from earlier quality programs:

- Every project must show a clear, measurable return, usually financial.
- Management leads and supports it actively, through a defined set of roles.
- Decisions rest on verifiable data and statistical methods, not on assumptions or opinion.

Not every process has to reach 3.4 DPMO. The organization should set a suitable sigma target for each key process, based on cost, risk, and what the customer needs, and then prioritize improvements.

## The two project cycles

Both cycles have five phases and descend from Deming's Plan-Do-Study-Act cycle.

| | DMAIC | DMADV (DFSS) |
| --- | --- | --- |
| Use it for | Improving an **existing** process that falls short | Designing a **new** product or process, or replacing one that can't be fixed |
| Phases | Define, Measure, Analyze, Improve, Control | Define, Measure, Analyze, Design, Verify |
| Ends with | A controlled, sustained process at a new level of performance | A verified design handed over to process owners |
| Details | [dmaic.md](dmaic.md) | [dfss-dmadv.md](../../03-design-and-engineering/methodologies/dfss-dmadv.md) |

## Six Sigma and Lean

| | Lean | Six Sigma |
| --- | --- | --- |
| Main target | Waste and flow | Defects and variation |
| Typical question | "Why does this take so long?" | "Why does this vary?" |
| Data use | Data-driven, often with simple measures | Depends heavily on accurate data and statistics |

The two are complementary. **Lean Six Sigma** uses Lean for flow and waste and Six Sigma for variation and design.

## Roles

Six Sigma uses a hierarchy of roles named after martial-arts belts: Executive Leadership, Champions, Master Black Belts, Black Belts, Green Belts, and in some organizations Yellow and White Belts. See [Six Sigma roles and belts](six-sigma-roles-and-belts.md).

## Where it has been applied

| Sector | Reported examples |
| --- | --- |
| Manufacturing | Motorola, GE, Honeywell, Johnson & Johnson (about $600M saved), Texas Instruments (over $500M saved), Sony, Boeing |
| Engineering and construction | Bechtel (about $30M invested, over $200M saved through less rework). A construction case study reported 26.2% shorter build time and 67% less waste. |
| Finance | Bank of America (2004: customer satisfaction up 10.4%, customer issues down 24%), American Express, GE Capital, JPMorgan Chase. Typical targets are cash allocation accuracy, bank charges, payment automation, and collector variation. |
| Telecom | Telefónica (€30M saved in the first 10 months) |
| Supply chain | Redesigning supply chains for on-time, defect-free delivery |
| Healthcare | Fits well because tolerance for error is near zero. MD Anderson Cancer Center ran 45% more exams on the same machines and cut patient preparation time from 45 to 5 minutes. Lean Six Sigma reached Red Cross hospitals in 2002 and Stanford hospitals in 2003. |

**Organization size.** Some consultants say companies with fewer than about 500 employees need a scaled-down approach. Most of the tools work at any size. What has to scale is the infrastructure: dedicated Black Belts, Champions, and certification.

## Criticism and failure modes

Use this section as a checklist of what to guard against.

| Criticism | Summary | How to guard against it |
| --- | --- | --- |
| High failure rate | A 2010 *Wall Street Journal* report put project failure at over 60%. | Use the failure factors below as a risk register for each program. |
| Not original | Joseph Juran called it "a basic version of quality improvement." | Treat it as a packaging of proven tools, and adopt only what helps. |
| Doesn't go far enough | Philip Crosby argued that 3.4 DPMO is too lax for products with millions of parts, such as microchips. | Set sigma targets from risk, not from the name. |
| Consultant industry | The belt and certification model created a training industry, and some trainers have only a shallow grasp of the method. | Judge practitioners by completed projects, not certificates. |
| Financial results | An analysis cited by *Fortune*, from a competing consultancy, found that 91% of 58 large Six Sigma adopters trailed the S&P 500 afterward. | Use it to fix existing processes, not as a growth strategy. |
| Stifles creativity | Critics (*Design News*, *BusinessWeek* on 3M, Wharton faculty) say it favors incremental gains over breakthrough research. | Keep DMAIC away from early-stage R&D. |
| Rigid and statistically fragile | Heavy reliance on significance tests and regression invites p-value misuse and treating exploratory models as confirmed. | Pre-register hypotheses and confirm with designed experiments. |
| The 1.5σ shift | Donald Wheeler and others call the fixed 1.5σ shift arbitrary. | Report short-term and long-term capability separately. See [sigma levels](../../02-quality-and-statistics/methodologies/sigma-levels-and-dpmo.md). |
| Single-loop thinking | A 2006 *Army Logistician* article argued that it can blind users to double-loop learning, adaptability, and culture. | Pair it with operational learning. See [Quality Systems (HOP)](../../07-quality-systems/). |
| Weak evidence base | Cranfield researchers found that much of the literature lacks rigor and relies on consultant case studies. | Measure your own before-and-after results honestly. |

A review of 56 papers (1995 to 2013) on Lean, Six Sigma, and Lean Six Sigma found 34 failure factors. They fall into five groups:

1. Weak top-management commitment and leadership
2. Too little training, education, and resourcing
3. Poor project selection, with a weak link to strategic goals
4. Cultural resistance, poor communication, and neglect of human factors
5. Little awareness of the benefits, and weak technical understanding

## Related topics

Lean manufacturing, Kaizen, Total Quality Management (TQM), Total Productive Maintenance (TPM), W. Edwards Deming, the seven basic quality tools, and BADIR (a data-analytics cycle).

---

**Source.** Facts and figures on this page come from the Wikipedia article [Six Sigma](https://en.wikipedia.org/wiki/Six_Sigma) and the references it cites, as of 2026-10-29. The text is a summary in our own words. Wikipedia content is available under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). "Six Sigma" is a registered mark of Motorola, Inc.
