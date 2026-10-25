// on vercel the api lives on the same site, so production builds default to relative /api calls
const API_URL = (import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? "http://localhost:8000" : "")).replace(/\/$/, "");
const TOKEN_KEY = "lotline.token";

export class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

export const tokenStore = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (token) => localStorage.setItem(TOKEN_KEY, token),
  clear: () => localStorage.removeItem(TOKEN_KEY),
};

let onUnauthorized = () => {};
export function setUnauthorizedHandler(handler) {
  onUnauthorized = handler;
}

// fastapi sends validation errors as a list, so flatten them into one readable line
function readError(body, status) {
  const detail = body?.detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => `${item.loc?.at(-1) ?? "field"}: ${item.msg}`).join(", ");
  }
  return detail || `Request failed (${status})`;
}

async function request(path, { method = "GET", body } = {}) {
  const headers = { "Content-Type": "application/json" };
  const token = tokenStore.get();
  if (token) headers.Authorization = `Bearer ${token}`;

  let response;
  try {
    response = await fetch(`${API_URL}${path}`, { method, headers, body: body ? JSON.stringify(body) : undefined });
  } catch {
    throw new ApiError(0, "Can't reach the server. Check that the API is running.");
  }

  if (response.status === 204) return null;
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    if (response.status === 401 && token) onUnauthorized();
    throw new ApiError(response.status, readError(data, response.status));
  }
  return data;
}

export const api = {
  register: (data) => request("/api/auth/register", { method: "POST", body: data }),
  login: (data) => request("/api/auth/login", { method: "POST", body: data }),
  me: () => request("/api/auth/me"),

  searchVehicles: (query) => request(`/api/vehicles/search${query ? `?${query}` : ""}`),
  listVehicles: () => request("/api/vehicles"),
  categories: () => request("/api/vehicles/categories"),
  addVehicle: (data) => request("/api/vehicles", { method: "POST", body: data }),
  updateVehicle: (id, data) => request(`/api/vehicles/${id}`, { method: "PUT", body: data }),
  deleteVehicle: (id) => request(`/api/vehicles/${id}`, { method: "DELETE" }),
  purchase: (id, quantity) => request(`/api/vehicles/${id}/purchase`, { method: "POST", body: { quantity } }),
  restock: (id, quantity) => request(`/api/vehicles/${id}/restock`, { method: "POST", body: { quantity } }),

  myPurchases: () => request("/api/purchases/me"),
  allSales: () => request("/api/purchases"),
  stats: () => request("/api/stats/summary"),
};
