import { useCallback, useEffect, useRef, useState } from "react";

// runs a loader whenever deps change and ignores answers that come back out of order
export function useAsync(loader, deps) {
  const [state, setState] = useState({ data: null, error: null, loading: true });
  const latest = useRef(0);

  const run = useCallback(() => {
    const ticket = ++latest.current;
    setState((current) => ({ ...current, loading: true, error: null }));
    loader()
      .then((data) => ticket === latest.current && setState({ data, error: null, loading: false }))
      .catch((error) => ticket === latest.current && setState((current) => ({ ...current, error, loading: false })));
  }, deps);

  useEffect(run, [run]);

  return { ...state, reload: run };
}
