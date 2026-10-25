import { useState } from "react";
import { api } from "../api/client.js";
import Modal from "../components/Modal.jsx";
import VehicleForm from "../components/VehicleForm.jsx";
import { useToast } from "../context/ToastContext.jsx";
import { useAsync } from "../hooks/useAsync.js";
import { formatPrice, isLowStock, vehicleTitle } from "../lib/format.js";

function RestockControl({ vehicle, onDone }) {
  const notify = useToast();
  const [amount, setAmount] = useState(5);
  const [busy, setBusy] = useState(false);

  const restock = async () => {
    setBusy(true);
    try {
      await api.restock(vehicle.id, Number(amount));
      notify(`Restocked ${vehicleTitle(vehicle)} with ${amount}`);
      onDone();
    } catch (err) {
      notify(err.message, "error");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="flex items-center gap-1">
      <input
        type="number"
        min="1"
        aria-label={`Units to add to ${vehicleTitle(vehicle)}`}
        className="w-16 px-2 py-1"
        value={amount}
        onChange={(event) => setAmount(event.target.value)}
      />
      <button type="button" className="btn-quiet px-3 py-1 text-sm" onClick={restock} disabled={busy || !(Number(amount) >= 1)}>
        Restock
      </button>
    </div>
  );
}

export default function ManagePage() {
  const notify = useToast();
  const vehicles = useAsync(() => api.listVehicles(), []);
  const categories = useAsync(() => api.categories(), []);
  const [editing, setEditing] = useState(null);
  const [deleting, setDeleting] = useState(null);
  const list = vehicles.data || [];

  const refresh = () => {
    vehicles.reload();
    categories.reload();
  };

  const save = async (payload) => {
    if (editing === "new") {
      await api.addVehicle(payload);
      notify(`Added ${vehicleTitle(payload)}`);
    } else {
      await api.updateVehicle(editing.id, payload);
      notify(`Saved ${vehicleTitle(payload)}`);
    }
    setEditing(null);
    refresh();
  };

  const confirmDelete = async () => {
    try {
      await api.deleteVehicle(deleting.id);
      notify(`Deleted ${vehicleTitle(deleting)}`);
      refresh();
    } catch (err) {
      notify(err.message, "error");
    }
    setDeleting(null);
  };

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:py-8">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="font-display text-4xl font-bold sm:text-5xl">Manage stock</h1>
          <p className="text-concrete">Add new arrivals, fix details, restock or remove cars.</p>
        </div>
        <button type="button" className="btn-primary" onClick={() => setEditing("new")}>
          Add vehicle
        </button>
      </div>

      {vehicles.error && <p className="mt-6 text-signal">{vehicles.error.message}</p>}

      <div className="mt-6 overflow-x-auto rounded-lg bg-white shadow-sm">
        <table className="w-full min-w-[46rem] text-left text-sm">
          <thead className="border-b-4 border-stripe bg-asphalt text-slate-200">
            <tr>
              <th scope="col" className="px-4 py-3 font-medium">Vehicle</th>
              <th scope="col" className="px-4 py-3 font-medium">Body</th>
              <th scope="col" className="px-4 py-3 text-right font-medium">Price</th>
              <th scope="col" className="px-4 py-3 text-right font-medium">In stock</th>
              <th scope="col" className="px-4 py-3 font-medium">Add units</th>
              <th scope="col" className="px-4 py-3"><span className="sr-only">Actions</span></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {list.map((vehicle) => (
              <tr key={vehicle.id} className="hover:bg-paper">
                <td className="px-4 py-3 font-medium">{vehicleTitle(vehicle)}</td>
                <td className="px-4 py-3 text-concrete">{vehicle.category}</td>
                <td className="px-4 py-3 text-right tabular-nums">{formatPrice(vehicle.price)}</td>
                <td className="px-4 py-3 text-right tabular-nums">
                  <span
                    className={`rounded px-2 py-0.5 font-semibold ${
                      vehicle.quantity === 0 ? "bg-red-50 text-signal" : isLowStock(vehicle.quantity) ? "bg-amber-50 text-amber-800" : ""
                    }`}
                  >
                    {vehicle.quantity}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <RestockControl vehicle={vehicle} onDone={vehicles.reload} />
                </td>
                <td className="px-4 py-3">
                  <div className="flex justify-end gap-2">
                    <button type="button" className="btn-quiet px-3 py-1 text-sm" onClick={() => setEditing(vehicle)}>
                      Edit
                    </button>
                    <button type="button" className="btn px-3 py-1 text-sm text-signal hover:bg-red-50" onClick={() => setDeleting(vehicle)}>
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {!vehicles.loading && list.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-10 text-center text-concrete">
                  The lot is empty. Add your first vehicle to get started.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {editing && (
        <VehicleForm
          vehicle={editing === "new" ? null : editing}
          categories={categories.data || []}
          onCancel={() => setEditing(null)}
          onSave={save}
        />
      )}

      {deleting && (
        <Modal title={`Delete ${vehicleTitle(deleting)}?`} onClose={() => setDeleting(null)}>
          <p className="text-concrete">It comes off the lot for good. Past purchases of this car stay in the sales log.</p>
          <div className="mt-6 flex justify-end gap-3">
            <button type="button" className="btn-quiet" onClick={() => setDeleting(null)}>
              Keep it
            </button>
            <button type="button" className="btn-danger" onClick={confirmDelete}>
              Delete vehicle
            </button>
          </div>
        </Modal>
      )}
    </div>
  );
}
