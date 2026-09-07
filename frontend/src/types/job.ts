export type JobStatus = "QUEUED" | "RUNNING" | "SUCCESS" | "FAILED" | "RETRYING" | "CANCELLED";

export interface Job {
  id: string;
  task_type: string;
  payload: Record<string, unknown>;
  status: JobStatus;
  priority: number;
  max_retries: number;
  retry_count: number;
  timeout_seconds: number;
  idempotency_key: string | null;
  result: Record<string, unknown> | null;
  error: string | null;
  celery_task_id: string | null;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface JobListResponse { items: Job[]; total: number; }
