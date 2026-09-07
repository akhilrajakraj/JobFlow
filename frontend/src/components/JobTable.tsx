import type { Job } from "../types/job";
import { StatusBadge } from "./StatusBadge";

export function JobTable({ jobs, onSelect }: { jobs: Job[]; onSelect: (job: Job) => void }) {
  if (!jobs.length) return <div className="empty">No jobs found.</div>;
  return <div className="table-wrap"><table><thead><tr><th>Task</th><th>Status</th><th>Priority</th><th>Retries</th><th>Created</th></tr></thead><tbody>
    {jobs.map(job => <tr key={job.id} onClick={() => onSelect(job)} className="clickable">
      <td><strong>{job.task_type}</strong><small>{job.id}</small></td><td><StatusBadge status={job.status}/></td><td>{job.priority}</td><td>{job.retry_count}/{job.max_retries}</td><td>{new Date(job.created_at).toLocaleString()}</td>
    </tr>)}
  </tbody></table></div>;
}
