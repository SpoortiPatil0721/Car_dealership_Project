import { useEffect, useState } from "react";

// hash routing so the build works on github pages without any server rewrites
function readHash() {
  return window.location.hash.replace(/^#\/?/, "") || "lot";
}

export function useHashRoute() {
  const [route, setRoute] = useState(readHash);

  useEffect(() => {
    const onChange = () => setRoute(readHash());
    window.addEventListener("hashchange", onChange);
    return () => window.removeEventListener("hashchange", onChange);
  }, []);

  return route;
}

export function goTo(route) {
  window.location.hash = `/${route}`;
}
