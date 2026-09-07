import type { Job, JobListResponse } from "../types/job";
import type { Worker } from "../types/worker";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";
export function getToken() { return localStorage.getItem("jobflow_token"); }
export function setToken(token: string) { localStorage.setItem("jobflow_token", token); }
export function clearToken() { localStorage.removeItem("jobflow_token"); }
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getToken(); const response = await fetch(`${API_BASE}${path}`, { headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}), ...(init?.headers ?? {}) }, ...init });
  if (!response.ok) throw new Error((await response.text()) || `Request failed (${response.status})`);
  return response.json() as Promise<T>;
}
export const api = {
  login: (username: string, password: string) => request<{ access_token: string; token_type: string; expires_in: number }>("/auth/login", { method: "POST", body: JSON.stringify({ username, password }) }),
  jobs: (limit = 50, offset = 0) => request<JobListResponse>(`/jobs?limit=${limit}&offset=${offset}`),
  job: (id: string) => request<Job>(`/jobs/${id}`),
  cancelJob: (id: string) => request<Job>(`/jobs/${id}/cancel`, { method: "POST" }),
  workers: () => request<Worker[]>("/workers"),
};
