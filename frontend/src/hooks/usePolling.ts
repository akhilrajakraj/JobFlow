import { useEffect, useRef } from "react";

export function usePolling(callback: () => void | Promise<void>, intervalMs: number) {
  const callbackRef = useRef(callback);
  useEffect(() => { callbackRef.current = callback; }, [callback]);
  useEffect(() => {
    const run = () => { void callbackRef.current(); };
    const timer = window.setInterval(run, intervalMs);
    return () => window.clearInterval(timer);
  }, [intervalMs]);
}
