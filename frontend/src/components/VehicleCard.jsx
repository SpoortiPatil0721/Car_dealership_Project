import CarArt from "./CarArt.jsx";
import { formatPrice, isLowStock, stockLabel, vehicleTitle } from "../lib/format.js";
import { paintFor } from "../lib/paint.js";

// each card reads like the price sticker you'd see in a car window
export default function VehicleCard({ vehicle, onBuy }) {
  const soldOut = vehicle.quantity <= 0;
  const low = isLowStock(vehicle.quantity);

  return (
    <article className="stall flex flex-col bg-asphalt-soft pl-3">
      <div className="relative px-2 pt-4">
        {vehicle.image_url ? (
          <img src={vehicle.image_url} alt={vehicleTitle(vehicle)} className="h-32 w-full rounded-md object-cover" loading="lazy" />
        ) : (
          <CarArt category={vehicle.category} color={vehicle.color} soldOut={soldOut} className="h-32 w-full" />
        )}
        {soldOut && (
          <span className="absolute right-3 top-4 rotate-6 rounded-sm border-2 border-signal bg-white px-2 font-display text-lg font-bold text-signal">
            Sold out
          </span>
        )}
      </div>

      <div className="mx-2 mb-3 mt-2 flex flex-1 flex-col overflow-hidden rounded-sm border-2 border-asphalt bg-white">
        <div className="bg-ink px-3 py-2 text-white">
          <h3 className="font-display text-xl font-semibold leading-tight">{vehicleTitle(vehicle)}</h3>
        </div>

        <dl className="grid grid-cols-2 gap-x-3 gap-y-1 border-b border-dashed border-slate-300 px-3 py-2 text-sm">
          <dt className="text-concrete">Body</dt>
          <dd className="text-right font-medium">{vehicle.category}</dd>
          <dt className="text-concrete">Paint</dt>
          <dd className="flex items-center justify-end gap-1.5 font-medium">
            <span className="inline-block size-3 rounded-full border border-slate-400" style={{ background: paintFor(vehicle.color) }} />
            {vehicle.color || "Not listed"}
          </dd>
        </dl>

        <div className="flex flex-1 flex-col justify-end gap-3 px-3 py-3">
          <div className="flex items-end justify-between gap-2">
            <p className="font-display text-3xl font-bold tabular-nums leading-none">{formatPrice(vehicle.price)}</p>
            <p className={`text-right text-sm font-medium ${soldOut ? "text-signal" : low ? "text-amber-700" : "text-concrete"}`}>
              {stockLabel(vehicle.quantity)}
            </p>
          </div>
          <button type="button" className="btn-primary w-full" disabled={soldOut} onClick={() => onBuy(vehicle)}>
            {soldOut ? "Sold out" : "Purchase"}
          </button>
        </div>
      </div>
    </article>
  );
}
