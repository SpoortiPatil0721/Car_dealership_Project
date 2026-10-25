import { countActive, EMPTY_FILTERS, priceRangeError, SORT_OPTIONS } from "../lib/filters.js";

export default function FilterPanel({ filters, onChange, categories }) {
  const set = (key) => (event) => {
    const value = event.target.type === "checkbox" ? event.target.checked : event.target.value;
    onChange({ ...filters, [key]: value });
  };
  const rangeError = priceRangeError(filters);
  const active = countActive(filters);

  return (
    <form className="flex flex-col gap-4" onSubmit={(event) => event.preventDefault()} role="search">
      <div>
        <label htmlFor="q" className="field-label">
          Search the lot
        </label>
        <input id="q" type="search" className="w-full" placeholder="Make, model or body style" value={filters.q} onChange={set("q")} />
      </div>

      <div>
        <label htmlFor="make" className="field-label">
          Make
        </label>
        <input id="make" className="w-full" placeholder="Any make" value={filters.make} onChange={set("make")} />
      </div>

      <div>
        <label htmlFor="category" className="field-label">
          Body style
        </label>
        <select id="category" className="w-full" value={filters.category} onChange={set("category")}>
          <option value="">All body styles</option>
          {categories.map((name) => (
            <option key={name} value={name}>
              {name}
            </option>
          ))}
        </select>
      </div>

      <fieldset>
        <legend className="field-label">Price range</legend>
        <div className="flex items-center gap-2">
          <input type="number" min="0" step="500" aria-label="Minimum price" className="w-full min-w-0" placeholder="Min" value={filters.min_price} onChange={set("min_price")} />
          <span className="text-concrete">to</span>
          <input type="number" min="0" step="500" aria-label="Maximum price" className="w-full min-w-0" placeholder="Max" value={filters.max_price} onChange={set("max_price")} />
        </div>
        {rangeError && <p className="mt-1 text-sm text-signal">{rangeError}</p>}
      </fieldset>

      <div>
        <label htmlFor="sort" className="field-label">
          Sort by
        </label>
        <select id="sort" className="w-full" value={filters.sort} onChange={set("sort")}>
          {SORT_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      <label className="flex cursor-pointer items-center gap-2 text-sm font-medium">
        <input type="checkbox" className="size-4 accent-ink" checked={filters.in_stock} onChange={set("in_stock")} />
        Hide sold out cars
      </label>

      {active > 0 && (
        <button type="button" className="btn-quiet" onClick={() => onChange(EMPTY_FILTERS)}>
          Clear {active} {active === 1 ? "filter" : "filters"}
        </button>
      )}
    </form>
  );
}
