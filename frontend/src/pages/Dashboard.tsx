import { useCallback, useEffect, useMemo, useState } from "react";
import { api } from "../services/api";
import type { Job, JobStatus } from "../types/job";
import type { Worker } from "../types/worker";
import { JobTable } from "../components/JobTable";
import { StatusBadge } from "../components/StatusBadge";
import { usePolling } from "../hooks/usePolling";

const statuses: Array<JobStatus | "ALL"> = ["ALL", "QUEUED", "RUNNING", "RETRYING", "SUCCESS", "FAILED", "CANCELLED"];

export default function Dashboard() {
  const [jobs, setJobs] = useState<Job[]>([]); const [total, setTotal] = useState(0);
  const [workers, setWorkers] = useState<Worker[]>([]); const [selected, setSelected] = useState<Job | null>(null);
  const [filter, setFilter] = useState<JobStatus | "ALL">("ALL"); const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true); const [error, setError] = useState("");

  const refresh = useCallback(async () => { try { const [j, w] = await Promise.all([api.jobs(), api.workers()]); setJobs(j.items); setTotal(j.total); setWorkers(w); setError(""); } catch (e) { setError(e instanceof Error ? e.message : "Unable to load dashboard"); } finally { setLoading(false); } }, []);
  useEffect(() => { void refresh(); }, [refresh]); usePolling(refresh, 5000);
  const filtered = useMemo(() => jobs.filter(j => (filter === "ALL" || j.status === filter) && (!search || j.task_type.toLowerCase().includes(search.toLowerCase()) || j.id.includes(search))), [jobs, filter, search]);
  const counts = useMemo(() => Object.fromEntries(statuses.slice(1).map(s => [s, jobs.filter(j => j.status === s).length])), [jobs]);
  async function cancel() { if (!selected) return; try { const updated = await api.cancelJob(selected.id); setSelected(updated); await refresh(); } catch (e) { setError(e instanceof Error ? e.message : "Cancellation failed"); } }

  return <div className="shell"><header><div><span className="eyebrow">OPERATIONS</span><h1>JobFlow</h1><p>Distributed background job control plane</p></div><button onClick={() => void refresh()}>Refresh</button></header>
    {error && <div className="alert">{error}</div>}
    <section className="stats"><div><span>Total jobs</span><b>{total}</b></div><div><span>Running</span><b>{counts.RUNNING ?? 0}</b></div><div><span>Queued</span><b>{counts.QUEUED ?? 0}</b></div><div><span>Failed</span><b>{counts.FAILED ?? 0}</b></div><div><span>Workers online</span><b>{workers.filter(w => w.status === "ONLINE").length}/{workers.length}</b></div></section>
    <div className="content"><main className="panel"><div className="toolbar"><input placeholder="Search task or job ID" value={search} onChange={e => setSearch(e.target.value)}/><select value={filter} onChange={e => setFilter(e.target.value as JobStatus | "ALL")}>{statuses.map(s => <option key={s}>{s}</option>)}</select></div>{loading ? <div className="empty">Loading…</div> : <JobTable jobs={filtered} onSelect={setSelected}/>}</main>
      <aside className="panel workers"><div className="panel-title"><h2>Workers</h2><span>{workers.length}</span></div>{workers.map(w => <div className="worker" key={w.id}><div><strong>{w.worker_name}</strong><small>{w.hostname}</small></div><span className={`dot ${w.status.toLowerCase()}`}/></div>)}{!workers.length && <div className="empty">No registered workers.</div>}</aside></div>
    {selected && <div className="drawer-backdrop" onClick={() => setSelected(null)}><aside className="drawer" onClick={e => e.stopPropagation()}><button className="close" onClick={() => setSelected(null)}>×</button><span className="eyebrow">JOB DETAIL</span><h2>{selected.task_type}</h2><StatusBadge status={selected.status}/><dl><dt>ID</dt><dd>{selected.id}</dd><dt>Priority</dt><dd>{selected.priority}</dd><dt>Retries</dt><dd>{selected.retry_count} / {selected.max_retries}</dd><dt>Created</dt><dd>{new Date(selected.created_at).toLocaleString()}</dd><dt>Result</dt><dd><pre>{JSON.stringify(selected.result, null, 2)}</pre></dd>{selected.error && <><dt>Error</dt><dd className="error-text">{selected.error}</dd></>}</dl>{!["SUCCESS", "FAILED", "CANCELLED"].includes(selected.status) && <button className="danger" onClick={() => void cancel()}>Cancel job</button>}</aside></div>}
  </div>;
}
