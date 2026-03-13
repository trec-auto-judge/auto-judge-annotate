# Changelog

## 0.3.5

- Add Supabase integration for real-time annotation sync
  - Online/offline sync modes with debounced auto-upload
  - Per-annotation username tracking (consistent across export and sync)
  - `--supabase-url` and `--supabase-anon-key` options on `generate` command
- Add `export-db` command to download annotations from Supabase as JSONL
- Replace `init-db` with SQL instructions for the Supabase SQL Editor
- Remove `psycopg2` dependency (all Supabase access via REST API)
- Fix: rapid navigation no longer drops annotations (dirty-set sync)
- Fix: failed uploads are retried automatically


## 0.3.4 yanked

## 0.3.3

- Citations annotation mode with dual spans (report + document)
- Sentence stepper navigation
- Per-sentence span splitting on text selection