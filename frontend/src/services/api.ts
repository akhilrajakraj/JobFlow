import type { Job, JobListResponse } from "../types/job";
import type { Worker } from "../types/worker";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  jobs: (limit = 50, offset = 0) => request<JobListResponse>(`/jobs?limit=${limit}&offset=${offset}`),
  job: (id: string) => request<Job>(`/jobs/${id}`),
  cancelJob: (id: string) => request<Job>(`/jobs/${id}/cancel`, { method: "POST" }),
  workers: () => request<Worker[]>("/workers"),
  health: () => request<{ status: string }>("http://localhost:8000/health".replace("http://localhost:8000", "")),
};
