export interface Worker {
  id: string;
  worker_name: string;
  hostname: string;
  status: string;
  concurrency: number;
  active_tasks: number;
  metadata: Record<string, unknown>;
  registered_at: string;
  last_heartbeat_at: string;
}
