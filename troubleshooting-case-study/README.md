# Power BI Dashboard Troubleshooting: Target Hours Model

I took over a Power BI dashboard (target hours vs actual hours, by team) that another developer had built and left half-finished. Users reported six problems. This repo is the diagnosis and fix plan I used, written so it can be reused for any inherited Power BI model.

---

## The setup

- Source files (dimension and fact tables) are dropped into a **SharePoint** folder.
- Power BI loads them, through a **Dataflow**, into a semantic model.
- A dashboard shows target hours, actual hours and cost by team and month.

## The six reported problems and my diagnosis

| # | Reported problem | Real cause | Fix |
|---|---|---|---|
| 1 | "Tables have not updated since the 21st" | A SharePoint file date is not the same as a Power BI refresh. Usually the scheduled refresh is failing silently (expired credentials or a changed source file). | Check **Refresh history** on the semantic model first, then fix credentials or the broken step |
| 2 | "If Power Automate drops the files daily, will the tables update?" | Not by itself. Power Automate can deliver the files, but Power BI still needs its own **scheduled refresh**, and the query must combine **all files in the folder** instead of one fixed file name | Folder + combine-files query, and a scheduled refresh after the files arrive |
| 3 | "I can't open Power Query editor on this data" | The tables are a **Dataflow** that lives in the workspace, not inside the .pbix file. Editing needs **Contributor** access to that workspace | Request workspace Contributor access, then edit the Dataflow |
| 4 | "Holidays show 0 target hours" | Not a bug. A calendar table sets holidays to 0 on purpose | Agree the business rule first (zero, reduced, or excluded), then change the calendar table |
| 5 | "No total cost in dollars, only quantity" | The dollar column was never brought in from the ERP extract | Add the cost amount column to the source extract and map it in the model |
| 6 | "Hours don't match the ERP invoice report and there is no pattern" | Usually timing (data pulled at different times) or reversal/adjustment lines counted in one report but not the other | Compare 2-3 real transactions line by line instead of comparing totals |

## Diagnosis order I recommend for any inherited model

1. **Is it refreshing at all?** Look at refresh history, not file dates.
2. **If yes, is it mapped correctly?** When new columns are added to a source file, the query or Dataflow must be updated **once** by hand. After that, automatic refresh picks them up.
3. **Is the "bug" actually a business rule?** Ask before changing it.
4. **Mismatches with the source system:** trace individual transactions, not totals.

## What I learned

- Most "Power BI is broken" problems are refresh, access, or mapping problems, not DAX problems.
- A model left half-finished often has new source columns that were never mapped into the old tables.
- Writing each answer as "question → cause → next step" made the meeting with the business users short and clear.

## Tools

Power BI Service · Power Query / Dataflows · SharePoint · Power Automate · Oracle Fusion (source data)

> Team names, people and project numbers have been removed.
