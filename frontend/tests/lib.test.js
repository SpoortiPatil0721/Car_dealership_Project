import { describe, expect, it } from "vitest";
import { countActive, EMPTY_FILTERS, priceRangeError, toQueryString } from "../src/lib/filters.js";
import { formatPrice, isLowStock, stockLabel, vehicleTitle } from "../src/lib/format.js";
import { paintFor } from "../src/lib/paint.js";

describe("toQueryString", () => {
  it("drops empty values and the default sort", () => {
    expect(toQueryString(EMPTY_FILTERS)).toBe("");
  });

  it("keeps the filters that were filled in", () => {
    const query = toQueryString({ ...EMPTY_FILTERS, make: " toyota ", min_price: 1000, in_stock: true, sort: "price_desc" });
    expect(query).toBe("make=toyota&min_price=1000&in_stock=true&sort=price_desc");
  });
});

describe("priceRangeError", () => {
  it("is happy with a blank range", () => {
    expect(priceRangeError(EMPTY_FILTERS)).toBe("");
  });

  it("flags a min above the max", () => {
    expect(priceRangeError({ min_price: "500", max_price: "100" })).toBe("Min price is higher than max price");
  });

  it("flags negative prices", () => {
    expect(priceRangeError({ min_price: "-1", max_price: "" })).toBe("Prices can't be negative");
  });
});

describe("countActive", () => {
  it("ignores sort and blank fields", () => {
    expect(countActive({ ...EMPTY_FILTERS, sort: "price_asc" })).toBe(0);
    expect(countActive({ ...EMPTY_FILTERS, make: "kia", in_stock: true })).toBe(2);
  });
});

describe("format helpers", () => {
  it("formats prices without cents", () => {
    expect(formatPrice(21500)).toBe("$21,500");
  });

  it("builds a title and skips a missing year", () => {
    expect(vehicleTitle({ year: 2024, make: "Kia", model: "Seltos" })).toBe("2024 Kia Seltos");
    expect(vehicleTitle({ make: "Kia", model: "Seltos" })).toBe("Kia Seltos");
  });

  it("describes stock in plain words", () => {
    expect(stockLabel(0)).toBe("Sold out");
    expect(stockLabel(1)).toBe("Last one on the lot");
    expect(stockLabel(4)).toBe("4 on the lot");
  });

  it("treats only 1 and 2 as low stock by default", () => {
    expect([0, 1, 2, 3].map((n) => isLowStock(n))).toEqual([false, true, true, false]);
  });
});

describe("paintFor", () => {
  it("maps known color names and falls back to grey", () => {
    expect(paintFor("Red")).toBe("#b5302a");
    expect(paintFor("metallic blue")).toBe("#2a5db0");
    expect(paintFor("unicorn")).toBe("#9aa0a8");
    expect(paintFor(null)).toBe("#9aa0a8");
  });
});
