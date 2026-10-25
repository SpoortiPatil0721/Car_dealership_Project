export const EMPTY_FILTERS = {
  q: "",
  make: "",
  category: "",
  min_price: "",
  max_price: "",
  in_stock: false,
  sort: "name",
};

export const SORT_OPTIONS = [
  { value: "name", label: "Make and model" },
  { value: "price_asc", label: "Price, low to high" },
  { value: "price_desc", label: "Price, high to low" },
  { value: "newest", label: "Newest arrivals" },
  { value: "stock_desc", label: "Most in stock" },
];

// turns the filter form into a query string and skips anything left blank
export function toQueryString(filters) {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (value === "" || value === false || value === null || value === undefined) continue;
    if (key === "sort" && value === "name") continue;
    params.set(key, String(value).trim());
  }
  return params.toString();
}

export function priceRangeError(filters) {
  const min = filters.min_price === "" ? null : Number(filters.min_price);
  const max = filters.max_price === "" ? null : Number(filters.max_price);
  if ((min !== null && min < 0) || (max !== null && max < 0)) return "Prices can't be negative";
  if (min !== null && max !== null && min > max) return "Min price is higher than max price";
  return "";
}

export function countActive(filters) {
  return Object.entries(filters).filter(([key, value]) => key !== "sort" && value !== "" && value !== false).length;
}
