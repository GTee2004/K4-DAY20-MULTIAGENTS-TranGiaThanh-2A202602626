---
name: reliable-tabular-data
description: Use when transforming tabular records into cleaned outputs and summary JSON.
---
- Count input data rows before deduplicating; include duplicate rows in this count.
- Deduplicate by the task’s specified key and use the resulting distinct records for downstream processing.
- Exclude records with unknown amounts from outputs and summaries that require a known amount.
- Parse monetary values without binary floating-point arithmetic and represent output amounts as integer cents.
- Normalize timestamps to UTC and format them as `YYYY-MM-DDTHH:MM:SSZ`.
- Normalize categorical values to the required canonical spellings.
- Write the cleaned file with the exact required column order and one row per distinct eligible record.
- Include required metadata, distinguishing total input rows from distinct records with known amounts.
- Validate output headers, row counts, formats, and JSON types before finishing.
