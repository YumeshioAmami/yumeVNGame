export interface Choice {
  text: string;
  to: string;
  hint?: string;
}

export interface SceneCast {
  character: string;
  expression: string;
  position?: "left" | "center" | "right" | "cg";
  layer?: number;
}

export interface SceneVisual {
  visual_mode: "background_sprites" | "background_only" | "cg";
  background?: string | null;
  cg?: string | null;
  filter?: string;
  cast?: SceneCast[];
}

export interface Ending {
  id: string;
  title: string;
  type: string;
  description: string;
}

export interface StoryNode {
  id: string;
  title: string;
  type: string;
  speaker: string;
  narration?: string;
  text: string;
  scene: SceneVisual;
  next?: string;
  choices?: Choice[];
  ending?: Ending;
}

export interface Character {
  id: string;
  name: string;
  role: string;
  color: string;
  bio: string;
  sprite: string;
  expressions: string[];
}

export interface StoryPackage {
  title: string;
  logline: string;
  synopsis: string;
  genre: string[];
  tone: string;
  theme: string;
  cover: string;
  characters: Character[];
  start_node: string;
  nodes: StoryNode[];
}

export interface StoryRecord {
  id: string;
  title: string;
  logline: string;
  synopsis: string;
  genre: string[];
  tone: string;
  theme: string;
  cover: string;
  source: string;
  status: string;
  created_at: string;
  updated_at: string;
  node_count: number;
  ending_count: number;
  character_count: number;
  package?: StoryPackage;
}

export interface Session {
  id: string;
  story_id: string;
  player_id: string;
  current_node_id: string;
  visited: string[];
  choices: Array<{ node: string; choice: string; to: string }>;
  history: Array<Record<string, string>>;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface SessionPayload {
  session: Session;
  story: StoryRecord;
  node: StoryNode;
  newly_unlocked?: string[];
}

export interface GalleryEntry {
  id: string;
  story_id: string;
  entry_key: string;
  entry_type: "cg" | "scene" | "sprite_differential" | "ending" | "music";
  title: string;
  image: string;
  node_id?: string | null;
  payload: Record<string, unknown>;
  sort_order: number;
  unlocked: boolean;
}

export interface Settings {
  theme: string;
  model: string;
  base_url: string;
  tts_endpoint: string;
  tts_voice: string;
}

export interface SecretsStatus {
  has_api_key: boolean;
  masked_key: string;
  storage: string;
}

export interface Bootstrap {
  stories: StoryRecord[];
  settings: Settings;
  secrets: SecretsStatus;
  stats: {
    stories: number;
    saves: number;
    gallery_unlocks: number;
    sessions: number;
  };
  dataset: {
    works?: number;
    name?: string;
    version?: string;
    status?: string;
  };
}

