/**
 * AEGISCORE — usePolling Hook
 * Polls a callback at a specified interval with cleanup.
 */
import { useCallback, useEffect, useRef } from 'react';

export function usePolling(callback, interval = 10000, enabled = true) {
  const savedCallback = useRef(callback);
  const intervalRef = useRef(null);

  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  const start = useCallback(() => {
    if (intervalRef.current) return;
    intervalRef.current = setInterval(() => {
      savedCallback.current();
    }, interval);
  }, [interval]);

  const stop = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  useEffect(() => {
    if (enabled) {
      savedCallback.current();
      start();
    } else {
      stop();
    }

    return () => stop();
  }, [enabled, start, stop]);

  return { start, stop };
}

export default usePolling;
