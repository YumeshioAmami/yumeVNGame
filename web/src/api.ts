const BASE = "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    ...init,
  });
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const data = await response.json();
      detail = data.detail || JSON.stringify(data);
    } catch {
      detail = await response.text();
    }
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

export const api = {
  bootstrap: () => request<import("./types").Bootstrap>("/bootstrap"),
  story: (id: string) => request<import("./types").StoryRecord>(`/stories/${id}`),
  stories: () => request<import("./types").StoryRecord[]>("/stories"),
  generate: (payload: {
    premise: string;
    genre: string;
    tone: string;
    length: string;
    extra: string;
  }) =>
    request<import("./types").StoryRecord>("/stories/generate", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  createSession: (story_id: string) =>
    request<import("./types").SessionPayload>("/sessions", {
      method: "POST",
      body: JSON.stringify({ story_id }),
    }),
  session: (id: string) => request<import("./types").SessionPayload>(`/sessions/${id}`),
  next: (id: string) =>
    request<import("./types").SessionPayload>(`/sessions/${id}/next`, { method: "POST" }),
  choose: (id: string, choice_index: number) =>
    request<import("./types").SessionPayload>(`/sessions/${id}/choose`, {
      method: "POST",
      body: JSON.stringify({ choice_index }),
    }),
  save: (id: string, save_name: string) =>
    request<Record<string, unknown>>(`/sessions/${id}/save`, {
      method: "POST",
      body: JSON.stringify({ save_name }),
    }),
  saves: (storyId: string) =>
    request<Array<Record<string, unknown>>>(`/stories/${storyId}/saves`),
  load: (saveId: string) =>
    request<import("./types").SessionPayload>(`/saves/${saveId}/load`, { method: "POST" }),
  gallery: (storyId: string) =>
    request<import("./types").GalleryEntry[]>(`/stories/${storyId}/gallery`),
  settings: () =>
    request<{ settings: import("./types").Settings; secrets: import("./types").SecretsStatus }>(
      "/settings",
    ),
  updateSettings: (payload: Partial<import("./types").Settings>) =>
    request<{ settings: import("./types").Settings; secrets: import("./types").SecretsStatus }>(
      "/settings",
      { method: "PUT", body: JSON.stringify(payload) },
    ),
  setSecret: (api_key: string, model?: string, base_url?: string) =>
    request<{ settings: import("./types").Settings; secrets: import("./types").SecretsStatus }>(
      "/settings/secret",
      { method: "POST", body: JSON.stringify({ api_key, model, base_url }) },
    ),
  clearSecret: () =>
    request<{ settings: import("./types").Settings; secrets: import("./types").SecretsStatus }>(
      "/settings/secret",
      { method: "DELETE" },
    ),
  dataset: () =>
    request<{ summary: Record<string, unknown>; preview: Array<Record<string, unknown>> }>(
      "/dataset",
    ),
  tts: (text: string) =>
    request<{
      mode: string;
      audio_base64?: string;
      mime?: string;
      response?: Record<string, unknown>;
      detail?: string;
      message?: string;
    }>("/tts", { method: "POST", body: JSON.stringify({ text }) }),
};

export function backgroundUrl(key?: string | null): string {
  return `/assets/backgrounds/${key || "rain_classroom"}.svg`;
}

export function cgUrl(key?: string | null): string {
  return `/assets/cg/${key || "cg_letter"}.svg`;
}

export function spriteUrl(sprite: string, expression: string): string {
  return `/assets/sprites/${sprite}_${expression}.svg`;
}

