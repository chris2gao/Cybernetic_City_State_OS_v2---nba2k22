# New-save template

`save_template.json` contains only stable schema and default-rule metadata. It
does not contain a prior career's roster, finances, snapshots, or process memory
addresses. `src/save_context.py` builds a clean SQLite template from
`database/schema.sql` and creates the versioned file
`league_template_v2.sqlite`. It copies that template into
`database/saves/<save-id>/` when a new save is initialized. Each career receives
its own database, snapshots, audits, backups, and reports. Older versioned
templates are left in place and are never silently reused for a new save.

Use the same `--save-id` for bootstrap and every monthly capture. Use a new ID
for a different in-game save. Existing save databases are never reset by the
bootstrap command.
