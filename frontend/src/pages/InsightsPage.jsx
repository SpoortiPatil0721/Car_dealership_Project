import { api } from "../api/client.js";
import { useAsync } from "../hooks/useAsync.js";
import { formatDate, formatPrice } from "../lib/format.js";

function Figure({ label, value, note }) {
  return (
    <div className="stall rounded-r-lg bg-white px-4 py-3 shadow-sm">
      <p className="text-sm text-concrete">{label}</p>
      <p className="font-display text-3xl font-bold tabular-nums">{value}</p>
      {note && <p className="text-sm text-concrete">{note}</p>}
    </div>
  );
}

export default function InsightsPage() {
  const stats = useAsync(() => api.stats(), []);
  const sales = useAsync(() => api.allSales(), []);
  const s = stats.data;
  const biggestCategory = Math.max(1, ...(s?.by_category || []).map((row) => row.units));

  if (stats.error) return <p className="mx-auto max-w-7xl px-4 py-8 text-signal">{stats.error.message}</p>;
  if (!s) return <p className="mx-auto max-w-7xl px-4 py-8 text-concrete">Adding up the lot…</p>;

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:py-8">
      <h1 className="font-display text-4xl font-bold sm:text-5xl">Insights</h1>
      <p className="text-concrete">Stock and sales across the whole lot.</p>

      <div className="mt-6 grid grid-cols-2 gap-3 lg:grid-cols-4">
        <Figure label="Stock value" value={formatPrice(s.inventory_value)} note={`${s.units_in_stock} units on the lot`} />
        <Figure label="Revenue" value={formatPrice(s.revenue)} note={`${s.units_sold} units sold`} />
        <Figure label="Models listed" value={s.total_models} note={`${s.out_of_stock} sold out`} />
        <Figure label="Running low" value={s.low_stock.length} note="at or below the restock line" />
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-3">
        <section className="rounded-lg bg-white p-5 shadow-sm">
          <h2 className="font-display text-2xl font-semibold">Restock soon</h2>
          {s.low_stock.length === 0 ? (
            <p className="mt-2 text-concrete">Every model has healthy stock.</p>
          ) : (
            <ul className="mt-3 divide-y divide-slate-100">
              {s.low_stock.map((v) => (
                <li key={v.id} className="flex justify-between py-2">
                  <span>
                    {v.make} {v.model}
                  </span>
                  <span className={`font-semibold tabular-nums ${v.quantity === 0 ? "text-signal" : "text-amber-700"}`}>
                    {v.quantity === 0 ? "Sold out" : `${v.quantity} left`}
                  </span>
                </li>
              ))}
            </ul>
          )}
          <a href="#/manage" className="btn-quiet mt-4 w-full">
            Go to stock
          </a>
        </section>

        <section className="rounded-lg bg-white p-5 shadow-sm">
          <h2 className="font-display text-2xl font-semibold">Best sellers</h2>
          {s.top_sellers.length === 0 ? (
            <p className="mt-2 text-concrete">No sales yet. Best sellers show up after the first purchase.</p>
          ) : (
            <ol className="mt-3 flex flex-col gap-2">
              {s.top_sellers.map((t, index) => (
                <li key={`${t.make}-${t.model}`} className="flex items-baseline gap-3">
                  <span className="font-display text-xl font-bold text-concrete">{index + 1}</span>
                  <span className="flex-1">
                    {t.make} {t.model}
                  </span>
                  <span className="text-sm text-concrete tabular-nums">{t.units_sold} sold</span>
                </li>
              ))}
            </ol>
          )}
        </section>

        <section className="rounded-lg bg-white p-5 shadow-sm">
          <h2 className="font-display text-2xl font-semibold">Units by body style</h2>
          <ul className="mt-3 flex flex-col gap-3">
            {s.by_category.map((row) => (
              <li key={row.category}>
                <div className="flex justify-between text-sm">
                  <span className="font-medium">{row.category}</span>
                  <span className="text-concrete tabular-nums">
                    {row.units} {row.units === 1 ? "unit" : "units"}, {row.models} {row.models === 1 ? "model" : "models"}
                  </span>
                </div>
                <div className="mt-1 h-2 rounded-full bg-paper">
                  <div className="h-2 rounded-full bg-ink" style={{ width: `${(row.units / biggestCategory) * 100}%` }} />
                </div>
              </li>
            ))}
          </ul>
        </section>
      </div>

      <section className="mt-8 overflow-x-auto rounded-lg bg-white shadow-sm">
        <h2 className="px-5 pt-5 font-display text-2xl font-semibold">Sales log</h2>
        {sales.data?.length ? (
          <table className="mt-3 w-full min-w-[36rem] text-left text-sm">
            <thead className="border-b border-slate-200 text-concrete">
              <tr>
                <th scope="col" className="px-5 py-2 font-medium">Date</th>
                <th scope="col" className="px-5 py-2 font-medium">Buyer</th>
                <th scope="col" className="px-5 py-2 font-medium">Vehicle</th>
                <th scope="col" className="px-5 py-2 text-right font-medium">Units</th>
                <th scope="col" className="px-5 py-2 text-right font-medium">Total</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {sales.data.map((sale) => (
                <tr key={sale.id}>
                  <td className="px-5 py-2">{formatDate(sale.purchased_at)}</td>
                  <td className="px-5 py-2">{sale.buyer_email}</td>
                  <td className="px-5 py-2">
                    {sale.make} {sale.model}
                  </td>
                  <td className="px-5 py-2 text-right tabular-nums">{sale.quantity}</td>
                  <td className="px-5 py-2 text-right tabular-nums">{formatPrice(sale.total_price)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="px-5 pb-5 pt-2 text-concrete">No sales recorded yet.</p>
        )}
      </section>
    </div>
  );
}
