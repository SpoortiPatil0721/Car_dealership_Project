import { api } from "../api/client.js";
import { useAsync } from "../hooks/useAsync.js";
import { formatDate, formatPrice } from "../lib/format.js";

export default function PurchasesPage() {
  const { data, error, loading } = useAsync(() => api.myPurchases(), []);
  const purchases = data || [];
  const spent = purchases.reduce((sum, p) => sum + p.total_price, 0);

  return (
    <div className="mx-auto max-w-3xl px-4 py-6 sm:py-8">
      <h1 className="font-display text-4xl font-bold sm:text-5xl">My purchases</h1>
      {purchases.length > 0 && (
        <p className="text-concrete">
          {purchases.length} {purchases.length === 1 ? "order" : "orders"}, {formatPrice(spent)} in total
        </p>
      )}

      {loading && <p className="mt-6 text-concrete">Loading your purchases…</p>}
      {error && <p className="mt-6 text-signal">{error.message}</p>}

      {!loading && !error && purchases.length === 0 && (
        <div className="mt-6 rounded-lg border-2 border-dashed border-slate-300 p-10 text-center">
          <p className="font-display text-2xl font-semibold">Nothing bought yet</p>
          <p className="mt-1 text-concrete">Cars you purchase from the lot will be listed here.</p>
          <a href="#/lot" className="btn-primary mt-4">
            Browse the lot
          </a>
        </div>
      )}

      <ol className="mt-6 flex flex-col gap-3">
        {purchases.map((p) => (
          <li key={p.id} className="stall flex items-center gap-4 rounded-r-lg bg-white p-4 shadow-sm">
            <div className="min-w-0 flex-1">
              <p className="font-display text-xl font-semibold leading-tight">{[p.year, p.make, p.model].filter(Boolean).join(" ")}</p>
              <p className="text-sm text-concrete">
                {formatDate(p.purchased_at)}, {p.quantity} × {formatPrice(p.unit_price)}
                {p.vehicle_id === null && ", no longer listed"}
              </p>
            </div>
            <p className="font-display text-2xl font-bold tabular-nums">{formatPrice(p.total_price)}</p>
          </li>
        ))}
      </ol>
    </div>
  );
}
