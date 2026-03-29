const API_BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8100/api";
const AUTH_BASE = API_BASE.replace(/\/api\/?$/, "");
const TOKEN_STORAGE_KEY = "myet.gateway.token";
const responseCache = new Map();
const inFlightRequests = new Map();

const CACHE_TTL_MS = {
  dashboard: 30_000,
  news: 20_000,
  recommendations: 20_000,
  briefing: 60_000,
  story: 60_000,
  videos: 60_000,
  video: 60_000,
  profile: 60_000,
  translate: 5 * 60_000
};

let inMemoryToken = null;
let authBootstrapPromise = null;

function readStoredToken() {
  if (typeof window === "undefined") {
    return inMemoryToken;
  }
  return window.localStorage.getItem(TOKEN_STORAGE_KEY) ?? inMemoryToken;
}

function persistToken(token) {
  inMemoryToken = token;
  if (typeof window !== "undefined") {
    if (token) {
      window.localStorage.setItem(TOKEN_STORAGE_KEY, token);
    } else {
      window.localStorage.removeItem(TOKEN_STORAGE_KEY);
    }
  }
}

async function bootstrapDemoSession(forceRefresh = false) {
  if (!forceRefresh && readStoredToken()) {
    return readStoredToken();
  }
  if (!forceRefresh && authBootstrapPromise) {
    return authBootstrapPromise;
  }

  authBootstrapPromise = fetch(`${AUTH_BASE}/auth/demo-login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username: "demo-user", role: "investor" })
  })
    .then(async (response) => {
      if (!response.ok) {
        throw new Error("Unable to create demo session");
      }
      const payload = await response.json();
      persistToken(payload.access_token);
      return payload.access_token;
    })
    .finally(() => {
      authBootstrapPromise = null;
    });

  return authBootstrapPromise;
}

function buildUrl(path, params = {}) {
  const url = new URL(`${API_BASE}${path}`);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, value);
    }
  });
  return url.toString();
}

function readCached(cacheKey) {
  if (!cacheKey) {
    return null;
  }
  const entry = responseCache.get(cacheKey);
  if (!entry) {
    return null;
  }
  if (Date.now() > entry.expiresAt) {
    responseCache.delete(cacheKey);
    return null;
  }
  return entry.payload;
}

function writeCached(cacheKey, payload, ttlMs) {
  if (!cacheKey || !ttlMs) {
    return payload;
  }
  responseCache.set(cacheKey, {
    payload,
    expiresAt: Date.now() + ttlMs
  });
  return payload;
}

function invalidateCache(matcher) {
  Array.from(responseCache.keys()).forEach((cacheKey) => {
    if (matcher(cacheKey)) {
      responseCache.delete(cacheKey);
    }
  });
}

async function authorizedFetch(url, options = {}, allowRetry = true) {
  const token = await bootstrapDemoSession();
  const headers = new Headers(options.headers ?? {});
  headers.set("Authorization", `Bearer ${token}`);

  const response = await fetch(url, { ...options, headers });
  if (response.status === 401 && allowRetry) {
    persistToken(null);
    const refreshedToken = await bootstrapDemoSession(true);
    headers.set("Authorization", `Bearer ${refreshedToken}`);
    return fetch(url, { ...options, headers });
  }
  return response;
}

async function request(path, options = {}, cache = null) {
  const cacheKey = cache?.key ?? null;
  const ttlMs = cache?.ttlMs ?? 0;
  const cached = readCached(cacheKey);
  if (cached) {
    return cached;
  }
  if (cacheKey && inFlightRequests.has(cacheKey)) {
    return inFlightRequests.get(cacheKey);
  }

  const requestPromise = authorizedFetch(`${API_BASE}${path}`, options)
    .then(async (response) => {
      if (!response.ok) {
        throw new Error(`Request failed for ${path}`);
      }
      const payload = await response.json();
      return writeCached(cacheKey, payload, ttlMs);
    })
    .finally(() => {
      if (cacheKey) {
        inFlightRequests.delete(cacheKey);
      }
    });

  if (cacheKey) {
    inFlightRequests.set(cacheKey, requestPromise);
  }
  return requestPromise;
}

async function get(path, params = {}, ttlMs = 0) {
  const url = buildUrl(path, params);
  return request(path + (url.includes("?") ? url.slice(url.indexOf("?")) : ""), {}, ttlMs ? { key: url, ttlMs } : null);
}

export const api = {
  bootstrapSession: () => bootstrapDemoSession(),
  getDashboard: () => get("/news/dashboard", {}, CACHE_TTL_MS.dashboard),
  getNews: (params) => get("/news", params, CACHE_TTL_MS.news),
  getRecommendations: (params) => get("/recommendations", params, CACHE_TTL_MS.recommendations),
  getBriefing: (topic) => get(`/briefing/${encodeURIComponent(topic)}`, {}, CACHE_TTL_MS.briefing),
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
  getStory: (storyId) => get(`/story/${encodeURIComponent(storyId)}`, {}, CACHE_TTL_MS.story),
  getVideos: () => get("/video", {}, CACHE_TTL_MS.videos),
  getVideo: (videoId) => get(`/video/${encodeURIComponent(videoId)}`, {}, CACHE_TTL_MS.video),
  translate: (payload) =>
    request(
      "/translate",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      },
      {
        key: `translate:${JSON.stringify(payload)}`,
        ttlMs: CACHE_TTL_MS.translate
      }
    ),
  getProfile: () => get("/profile", {}, CACHE_TTL_MS.profile),
  updateProfile: (payload) =>
    request(
      "/profile",
      {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      },
      null
    ).then((result) => {
      invalidateCache((cacheKey) =>
        cacheKey.includes("/profile") ||
        cacheKey.includes("/recommendations") ||
        cacheKey.includes("/news/dashboard")
      );
      return result;
    }),
  uploadPortfolio: async (file) => {
    const form = new FormData();
    form.append("file", file);
    const response = await authorizedFetch(`${API_BASE}/profile/portfolio`, {
      method: "POST",
      body: form
    });
    if (!response.ok) {
      throw new Error("Portfolio upload failed");
    }
    const payload = await response.json();
    invalidateCache((cacheKey) =>
      cacheKey.includes("/profile") ||
      cacheKey.includes("/recommendations") ||
      cacheKey.includes("/news") ||
      cacheKey.includes("/news/dashboard")
    );
    return payload;
  }
};
