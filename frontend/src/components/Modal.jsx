import { useEffect, useRef } from "react";

export default function Modal({ title, onClose, children, wide = false }) {
  const panel = useRef(null);
  const closeRef = useRef(onClose);
  closeRef.current = onClose;

  // focus once on open, not on every re-render while typing
  useEffect(() => {
    const onKey = (event) => event.key === "Escape" && closeRef.current();
    document.addEventListener("keydown", onKey);
    panel.current?.querySelector("input, select, textarea, button:not([aria-label='Close'])")?.focus();
    return () => document.removeEventListener("keydown", onKey);
  }, []);

  return (
    <div className="fixed inset-0 z-40 flex items-end justify-center bg-asphalt/60 p-0 sm:items-center sm:p-4" onMouseDown={onClose}>
      <div
        ref={panel}
        role="dialog"
        aria-modal="true"
        aria-label={title}
        onMouseDown={(event) => event.stopPropagation()}
        className={`max-h-[92vh] w-full overflow-y-auto rounded-t-xl bg-white p-6 shadow-2xl sm:rounded-xl ${wide ? "sm:max-w-2xl" : "sm:max-w-md"}`}
      >
        <div className="mb-4 flex items-start justify-between gap-4">
          <h2 className="font-display text-2xl font-semibold leading-tight">{title}</h2>
          <button type="button" onClick={onClose} className="rounded-md px-2 text-2xl leading-none text-concrete hover:text-asphalt" aria-label="Close">
            ×
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}
