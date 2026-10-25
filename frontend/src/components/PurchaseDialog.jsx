import { useState } from "react";
import Modal from "./Modal.jsx";
import { api } from "../api/client.js";
import { useToast } from "../context/ToastContext.jsx";
import { formatPrice, vehicleTitle } from "../lib/format.js";

export default function PurchaseDialog({ vehicle, onClose, onDone }) {
  const notify = useToast();
  const maxUnits = Math.min(vehicle.quantity, 100);
  const [units, setUnits] = useState(1);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const confirm = async () => {
    setBusy(true);
    setError("");
    try {
      await api.purchase(vehicle.id, units);
      notify(`Purchased ${units} × ${vehicleTitle(vehicle)}`);
      onDone();
    } catch (err) {
      // stock may have changed since the page loaded, so show the server's answer
      setError(err.message);
      setBusy(false);
    }
  };

  return (
    <Modal title={`Purchase ${vehicleTitle(vehicle)}`} onClose={onClose}>
      <p className="text-concrete">
        {formatPrice(vehicle.price)} each. {vehicle.quantity} available.
      </p>

      <div className="mt-5 flex items-center justify-between gap-4">
        <span className="font-medium">How many</span>
        <div className="flex items-center rounded-md border border-slate-300">
          <button type="button" className="px-4 py-2 text-xl disabled:opacity-30" onClick={() => setUnits(units - 1)} disabled={units <= 1} aria-label="One fewer">
            −
          </button>
          <span className="w-10 text-center font-display text-2xl font-semibold tabular-nums" aria-live="polite">
            {units}
          </span>
          <button type="button" className="px-4 py-2 text-xl disabled:opacity-30" onClick={() => setUnits(units + 1)} disabled={units >= maxUnits} aria-label="One more">
            +
          </button>
        </div>
      </div>

      <div className="mt-5 flex items-baseline justify-between border-t border-slate-200 pt-4">
        <span className="text-concrete">Total</span>
        <span className="font-display text-3xl font-bold tabular-nums">{formatPrice(vehicle.price * units)}</span>
      </div>

      {error && <p className="mt-3 rounded-md bg-red-50 px-3 py-2 text-sm text-signal">{error}</p>}

      <div className="mt-6 flex gap-3">
        <button type="button" className="btn-quiet flex-1" onClick={onClose}>
          Cancel
        </button>
        <button type="button" className="btn-primary flex-1" onClick={confirm} disabled={busy}>
          {busy ? "Purchasing…" : `Purchase for ${formatPrice(vehicle.price * units)}`}
        </button>
      </div>
    </Modal>
  );
}
