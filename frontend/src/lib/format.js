const money = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });

export function formatPrice(value) {
  return money.format(Number(value) || 0);
}

export function vehicleTitle(vehicle) {
  return [vehicle.year, vehicle.make, vehicle.model].filter(Boolean).join(" ");
}

export function stockLabel(quantity) {
  if (quantity <= 0) return "Sold out";
  if (quantity === 1) return "Last one on the lot";
  return `${quantity} on the lot`;
}

export function isLowStock(quantity, threshold = 2) {
  return quantity > 0 && quantity <= threshold;
}

export function formatDate(iso) {
  return new Date(iso).toLocaleDateString("en-US", { day: "numeric", month: "short", year: "numeric" });
}
