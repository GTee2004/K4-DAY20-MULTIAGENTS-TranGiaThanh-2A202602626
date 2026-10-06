---
name: normalized-log-triage
description: Use when generating structured JSON summaries from service logs.
---
- Normalize service names to lowercase and replace hyphens with underscores.
- Sort error records by normalized service name, then by UTC timestamp in ascending order.
- Include the required top-level schema version and generator identifier.
- Validate the JSON structure and confirm the output follows the required schema before finishing.
