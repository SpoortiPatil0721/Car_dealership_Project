import { useState } from "react";
import CarArt from "../components/CarArt.jsx";
import { useAuth } from "../context/AuthContext.jsx";

const PARKED = [
  { category: "SUV", color: "Green" },
  { category: "Sedan", color: "Red" },
  { category: "Pickup", color: "Bronze" },
];

export default function AuthPage() {
  const { login, register } = useAuth();
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ full_name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const isLogin = mode === "login";

  const set = (key) => (event) => setForm({ ...form, [key]: event.target.value });

  const submit = async (event) => {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      if (isLogin) await login({ email: form.email, password: form.password });
      else await register(form);
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  };

  const switchMode = () => {
    setMode(isLogin ? "register" : "login");
    setError("");
  };

  return (
    <div className="grid min-h-screen lg:grid-cols-[1.1fr_1fr]">
      <section className="flex flex-col justify-between bg-asphalt px-6 py-8 text-white sm:px-12 sm:py-12">
        <p className="font-display text-2xl font-bold">LotLine</p>

        <div className="my-10">
          <h1 className="max-w-md font-display text-5xl font-bold leading-[0.95] sm:text-6xl">Every car on the lot, accounted for.</h1>
          <p className="mt-4 max-w-sm text-lg text-slate-300">Browse what's parked, buy what you like, and keep stock honest.</p>
        </div>

        <div className="grid grid-cols-3" aria-hidden="true">
          {PARKED.map((car) => (
            <div key={car.color} className="stall border-r-[5px] border-r-stripe px-1 pb-2 pt-6 first:border-r-0 last:border-r-[5px]">
              <CarArt category={car.category} color={car.color} className="w-full" />
            </div>
          ))}
        </div>
      </section>

      <section className="flex items-center justify-center px-6 py-12">
        <form onSubmit={submit} className="w-full max-w-sm" noValidate>
          <h2 className="font-display text-4xl font-bold">{isLogin ? "Log in" : "Create an account"}</h2>
          <p className="mt-1 text-concrete">{isLogin ? "Welcome back to the lot." : "It takes about ten seconds."}</p>

          <div className="mt-8 flex flex-col gap-4">
            {!isLogin && (
              <div>
                <label htmlFor="full_name" className="field-label">
                  Full name
                </label>
                <input id="full_name" className="w-full" autoComplete="name" value={form.full_name} onChange={set("full_name")} required />
              </div>
            )}
            <div>
              <label htmlFor="email" className="field-label">
                Email
              </label>
              <input id="email" type="email" className="w-full" autoComplete="email" value={form.email} onChange={set("email")} required />
            </div>
            <div>
              <label htmlFor="password" className="field-label">
                Password
              </label>
              <input
                id="password"
                type="password"
                className="w-full"
                autoComplete={isLogin ? "current-password" : "new-password"}
                value={form.password}
                onChange={set("password")}
                minLength={6}
                required
              />
              {!isLogin && <p className="mt-1 text-sm text-concrete">At least 6 characters.</p>}
            </div>
          </div>

          {error && (
            <p role="alert" className="mt-4 rounded-md bg-red-50 px-3 py-2 text-sm text-signal">
              {error}
            </p>
          )}

          <button type="submit" className="btn-primary mt-6 w-full py-2.5" disabled={busy}>
            {busy ? "One moment…" : isLogin ? "Log in" : "Create account"}
          </button>

          <p className="mt-6 text-center text-sm text-concrete">
            {isLogin ? "New here?" : "Already have an account?"}{" "}
            <button type="button" onClick={switchMode} className="font-semibold text-ink underline-offset-2 hover:underline">
              {isLogin ? "Create an account" : "Log in instead"}
            </button>
          </p>
        </form>
      </section>
    </div>
  );
}
