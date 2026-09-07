import type { JobStatus } from "../types/job";

export function StatusBadge({ status }: { status: JobStatus | string }) {
  return <span className={`badge badge-${status.toLowerCase()}`}>{status}</span>;
}
