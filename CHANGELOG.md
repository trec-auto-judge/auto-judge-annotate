# Changelog

## 0.3.6

- Supabase sync: simplified to throttled `syncAll` approach (every edit starts a 5s
  timer; when it fires, all annotations are uploaded). Replaces the previous dirty-key
  tracking which had edge cases around navigation and offline-to-online transitions.
- Sync status indicator: 5 states (grey=idle, yellowish-green=pending, yellow=uploading,
  green=synced, red=error)
- Error dialog on sync failure with option to switch to offline mode (one dialog per
  error streak, resets on recovery or manual action)
- Switching from offline to online immediately syncs all annotations
- Per-annotation username: each annotation stores the username at edit time, consistent
  across JSONL export, server sync, and "Sync to Server" button
- `init-db` now prints SQL instructions for the Supabase SQL Editor (direct PostgreSQL
  connection removed due to network issues with Supabase)
- `export-db` command: download annotations from Supabase via REST API as JSONL
- Remove `psycopg2` dependency (all Supabase access via REST API)
- "Clear all" button renamed to clarify scope (per-user, per-dataset)


## 0.3.5 yanked

## 0.3.4 yanked

## 0.3.3

- Citations annotation mode with dual spans (report + document)
- Sentence stepper navigation
- Per-sentence span splitting on text selection