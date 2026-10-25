import { useState } from "react";
import CarArt from "./CarArt.jsx";
import Modal from "./Modal.jsx";

const BLANK = { make: "", model: "", category: "", price: "", quantity: "", year: "", color: "", image_url: "", description: "" };

function toForm(vehicle) {
  if (!vehicle) return BLANK;
  return Object.fromEntries(Object.keys(BLANK).map((key) => [key, vehicle[key] ?? ""]));
}

// blank optional fields go to the api as null, numbers go as numbers
function toPayload(form) {
  const numbers = ["price", "quantity", "year"];
  return Object.fromEntries(
    Object.entries(form).map(([key, value]) => {
      const text = String(value).trim();
      if (text === "") return [key, null];
      return [key, numbers.includes(key) ? Number(text) : text];
    }),
  );
}

function validate(form) {
  const problems = {};
  for (const key of ["make", "model", "category"]) if (!String(form[key]).trim()) problems[key] = "Required";
  if (!(Number(form.price) > 0)) problems.price = "Enter a price above zero";
  if (form.quantity === "" || !Number.isInteger(Number(form.quantity)) || Number(form.quantity) < 0) problems.quantity = "Whole number, zero or more";
  if (form.year !== "" && (Number(form.year) < 1886 || Number(form.year) > 2100)) problems.year = "Year looks off";
  return problems;
}

export default function VehicleForm({ vehicle, categories, onCancel, onSave }) {
  const [form, setForm] = useState(() => toForm(vehicle));
  const [problems, setProblems] = useState({});
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const editing = Boolean(vehicle);

  const set = (key) => (event) => setForm({ ...form, [key]: event.target.value });

  const submit = async (event) => {
    event.preventDefault();
    const found = validate(form);
    setProblems(found);
    if (Object.keys(found).length) return;
    setBusy(true);
    setError("");
    try {
      await onSave(toPayload(form));
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  };

  const field = (key, label, props = {}) => (
    <div className={props.wide ? "sm:col-span-2" : ""}>
      <label htmlFor={`vf-${key}`} className="field-label">
        {label}
      </label>
      <input id={`vf-${key}`} className="w-full" value={form[key]} onChange={set(key)} aria-invalid={Boolean(problems[key])} {...props.input} />
      {problems[key] && <p className="mt-1 text-sm text-signal">{problems[key]}</p>}
    </div>
  );

  return (
    <Modal title={editing ? "Edit vehicle" : "Add a vehicle"} onClose={onCancel} wide>
      <form onSubmit={submit} noValidate>
        <div className="mb-4 rounded-md bg-paper px-6 py-2">
          <CarArt category={form.category} color={form.color} className="mx-auto h-24" />
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          {field("make", "Make", { input: { placeholder: "Toyota" } })}
          {field("model", "Model", { input: { placeholder: "Corolla" } })}
          <div>
            <label htmlFor="vf-category" className="field-label">
              Body style
            </label>
            <input id="vf-category" list="category-options" className="w-full" placeholder="Sedan, SUV, Pickup…" value={form.category} onChange={set("category")} />
            <datalist id="category-options">
              {categories.map((name) => (
                <option key={name} value={name} />
              ))}
            </datalist>
            {problems.category && <p className="mt-1 text-sm text-signal">{problems.category}</p>}
          </div>
          {field("year", "Year", { input: { type: "number", placeholder: "2025" } })}
          {field("price", "Price (USD)", { input: { type: "number", min: 0, step: 100 } })}
          {field("quantity", "Units in stock", { input: { type: "number", min: 0, step: 1 } })}
          {field("color", "Paint color", { input: { placeholder: "Blue" } })}
          {field("image_url", "Photo link (optional)", { input: { type: "url", placeholder: "https://…" } })}
          <div className="sm:col-span-2">
            <label htmlFor="vf-description" className="field-label">
              Notes (optional)
            </label>
            <textarea id="vf-description" rows={3} className="w-full" value={form.description} onChange={set("description")} />
          </div>
        </div>

        {error && <p className="mt-4 rounded-md bg-red-50 px-3 py-2 text-sm text-signal">{error}</p>}

        <div className="mt-6 flex justify-end gap-3">
          <button type="button" className="btn-quiet" onClick={onCancel}>
            Cancel
          </button>
          <button type="submit" className="btn-primary" disabled={busy}>
            {busy ? "Saving…" : editing ? "Save changes" : "Add vehicle"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
