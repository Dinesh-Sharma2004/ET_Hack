const API_BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000/api";
const responseCache = new Map();

function buildUrl(path, params = {}) {
  const url = new URL(`${API_BASE}${path}`);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, value);
    }
  });
  return url.toString();
}

async function request(path, options = {}, cacheKey = null) {
  if (cacheKey && responseCache.has(cacheKey)) {
    return responseCache.get(cacheKey);
  }
  const response = await fetch(`${API_BASE}${path}`, options);
  if (!response.ok) {
    throw new Error(`Request failed for ${path}`);
  }
  const payload = await response.json();
  if (cacheKey) {
    responseCache.set(cacheKey, payload);
  }
  return payload;
}

async function get(path, params = {}, useCache = true) {
  const url = buildUrl(path, params);
  const cacheKey = useCache ? url : null;
  if (cacheKey && responseCache.has(cacheKey)) return responseCache.get(cacheKey);
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Request failed for ${path}`);
  const payload = await response.json();
  if (cacheKey) responseCache.set(cacheKey, payload);
  return payload;
}

export const api = {
  getDashboard: () => get("/news/dashboard"),
  getNews: (params) => get("/news", params, false),
  getRecommendations: (params) => get("/recommendations", params, false),
  getBriefing: (topic) => get(`/briefing/${encodeURIComponent(topic)}`),
  askBriefing: (topic, payload) =>
    request(
      `/briefing/${encodeURIComponent(topic)}/chat`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      },
      null
    ),
  getStory: (storyId) => get(`/story/${encodeURIComponent(storyId)}`),
  getVideos: () => get("/video"),
  getVideo: (videoId) => get(`/video/${encodeURIComponent(videoId)}`),
  translate: (payload) =>
    request(
      "/translate",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      },
      null
    ),
  getProfile: () => get("/profile", {}, false),
  updateProfile: (payload) =>
    request(
      "/profile",
      {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      },
      null
    ),
  uploadPortfolio: async (file) => {
    const form = new FormData();
    form.append("file", file);
    const response = await fetch(`${API_BASE}/profile/portfolio`, {
      method: "POST",
      body: form
    });
    if (!response.ok) throw new Error("Portfolio upload failed");
    return response.json();
  }
};
