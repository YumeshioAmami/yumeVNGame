PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_meta (
  version INTEGER PRIMARY KEY,
  applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS player_profiles (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS stories (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  logline TEXT,
  synopsis TEXT,
  genre_json TEXT NOT NULL DEFAULT '[]',
  tone TEXT,
  theme TEXT,
  cover TEXT,
  package_json TEXT NOT NULL,
  source TEXT NOT NULL DEFAULT 'demo',
  status TEXT NOT NULL DEFAULT 'ready',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
  id TEXT PRIMARY KEY,
  story_id TEXT NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
  player_id TEXT NOT NULL,
  current_node_id TEXT NOT NULL,
  visited_json TEXT NOT NULL DEFAULT '[]',
  choices_json TEXT NOT NULL DEFAULT '[]',
  history_json TEXT NOT NULL DEFAULT '[]',
  status TEXT NOT NULL DEFAULT 'active',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS saves (
  id TEXT PRIMARY KEY,
  session_id TEXT,
  story_id TEXT NOT NULL,
  player_id TEXT NOT NULL,
  save_name TEXT NOT NULL,
  current_node_id TEXT NOT NULL,
  visited_json TEXT NOT NULL DEFAULT '[]',
  choices_json TEXT NOT NULL DEFAULT '[]',
  history_json TEXT NOT NULL DEFAULT '[]',
  state_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS gallery_entries (
  id TEXT PRIMARY KEY,
  story_id TEXT NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
  entry_key TEXT NOT NULL,
  entry_type TEXT NOT NULL,
  title TEXT NOT NULL,
  image TEXT,
  node_id TEXT,
  payload_json TEXT NOT NULL DEFAULT '{}',
  sort_order INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  UNIQUE(story_id, entry_key)
);

CREATE TABLE IF NOT EXISTS gallery_unlocks (
  id TEXT PRIMARY KEY,
  player_id TEXT NOT NULL,
  entry_id TEXT NOT NULL REFERENCES gallery_entries(id) ON DELETE CASCADE,
  unlocked_at TEXT NOT NULL,
  UNIQUE(player_id, entry_id)
);

CREATE TABLE IF NOT EXISTS generation_jobs (
  id TEXT PRIMARY KEY,
  status TEXT NOT NULL,
  prompt_json TEXT NOT NULL DEFAULT '{}',
  story_id TEXT,
  error TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS assets (
  id TEXT PRIMARY KEY,
  asset_type TEXT NOT NULL,
  url TEXT NOT NULL,
  label TEXT,
  metadata_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS agent_configs (
  id TEXT PRIMARY KEY,
  category TEXT NOT NULL,
  label TEXT NOT NULL,
  sort_order INTEGER NOT NULL DEFAULT 0,
  mode TEXT NOT NULL DEFAULT 'api',
  model TEXT NOT NULL DEFAULT '',
  base_url TEXT NOT NULL DEFAULT '',
  local_path TEXT NOT NULL DEFAULT '',
  local_endpoint TEXT NOT NULL DEFAULT '',
  provider TEXT NOT NULL DEFAULT '',
  updated_at TEXT NOT NULL
);

