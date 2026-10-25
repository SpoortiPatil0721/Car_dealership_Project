import { useEffect, useState } from "react";
import { api } from "../api/client.js";
import FilterPanel from "../components/FilterPanel.jsx";
import PurchaseDialog from "../components/PurchaseDialog.jsx";
import VehicleCard from "../components/VehicleCard.jsx";
import { useAsync } from "../hooks/useAsync.js";
import { EMPTY_FILTERS, priceRangeError, toQueryString } from "../lib/filters.js";

function useDebounced(value, delay = 300) {
  const [settled, setSettled] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setSettled(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  return settled;
}

export default function LotPage() {
  const [filters, setFilters] = useState(EMPTY_FILTERS);
  const [buying, setBuying] = useState(null);
  const [showFilters, setShowFilters] = useState(false);
  const query = useDebounced(toQueryString(filters));
  const rangeIsBad = Boolean(priceRangeError(filters));

  const categories = useAsync(() => api.categories(), []);
  // skip the request while the price range is impossible, the panel already says why
  const vehicles = useAsync(() => (rangeIsBad ? Promise.resolve([]) : api.searchVehicles(query)), [query, rangeIsBad]);
  const list = vehicles.data || [];
  const inStock = list.filter((v) => v.quantity > 0).length;

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:py-8">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="font-display text-4xl font-bold sm:text-5xl">The lot</h1>
          <p className="text-concrete">
            {vehicles.loading && !vehicles.data
              ? "Checking the lot…"
              : `${list.length} ${list.length === 1 ? "car" : "cars"} shown, ${inStock} ready to drive away`}
          </p>
        </div>
        <button type="button" className="btn-quiet lg:hidden" onClick={() => setShowFilters(!showFilters)} aria-expanded={showFilters}>
          {showFilters ? "Hide filters" : "Filters"}
        </button>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-[16rem_1fr]">
        <aside className={`${showFilters ? "block" : "hidden"} self-start rounded-lg bg-white p-4 shadow-sm lg:sticky lg:top-4 lg:block`}>
          <FilterPanel filters={filters} onChange={setFilters} categories={categories.data || []} />
        </aside>

        <section aria-label="Vehicles" aria-busy={vehicles.loading}>
          {vehicles.error && (
            <div className="rounded-lg bg-white p-6">
              <p className="font-medium text-signal">{vehicles.error.message}</p>
              <button type="button" className="btn-quiet mt-3" onClick={vehicles.reload}>
                Try again
              </button>
            </div>
          )}

          {!vehicles.error && vehicles.data && list.length === 0 && (
            <div className="rounded-lg border-2 border-dashed border-slate-300 p-10 text-center">
              <p className="font-display text-2xl font-semibold">No cars match those filters</p>
              <p className="mt-1 text-concrete">Widen the price range or clear a filter to see more of the lot.</p>
              <button type="button" className="btn-quiet mt-4" onClick={() => setFilters(EMPTY_FILTERS)}>
                Clear filters
              </button>
            </div>
          )}

          {list.length > 0 && (
            <div className={`grid gap-y-1 rounded-lg bg-asphalt p-3 pr-0 sm:grid-cols-2 xl:grid-cols-3 ${vehicles.loading ? "opacity-70" : ""}`}>
              {list.map((vehicle) => (
                <VehicleCard key={vehicle.id} vehicle={vehicle} onBuy={setBuying} />
              ))}
            </div>
          )}
        </section>
      </div>

      {buying && (
        <PurchaseDialog
          vehicle={buying}
          onClose={() => setBuying(null)}
          onDone={() => {
            setBuying(null);
            vehicles.reload();
          }}
        />
      )}
    </div>
  );
}
