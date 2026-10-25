import { useAuth } from "../context/AuthContext.jsx";

export default function Header({ route }) {
  const { user, logout } = useAuth();
  const links = [
    { route: "lot", label: "The lot" },
    { route: "purchases", label: "My purchases" },
    ...(user?.is_admin
      ? [
          { route: "manage", label: "Manage stock" },
          { route: "insights", label: "Insights" },
        ]
      : []),
  ];

  return (
    <header className="bg-asphalt text-white">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-x-6 gap-y-2 px-4 py-3">
        <a href="#/lot" className="flex items-center gap-2 font-display text-2xl font-bold">
          <span className="flex h-7 items-center gap-1" aria-hidden="true">
            <span className="h-full w-1 bg-stripe" />
            <span className="h-4 w-3 rounded-sm bg-white" />
            <span className="h-full w-1 bg-stripe" />
          </span>
          LotLine
        </a>

        <nav className="order-3 -mx-1 flex w-full gap-1 overflow-x-auto sm:order-none sm:w-auto" aria-label="Main">
          {links.map((link) => (
            <a
              key={link.route}
              href={`#/${link.route}`}
              aria-current={route === link.route ? "page" : undefined}
              className={`whitespace-nowrap rounded-md px-3 py-1.5 text-sm font-medium ${
                route === link.route ? "bg-stripe text-asphalt" : "text-slate-200 hover:bg-asphalt-soft"
              }`}
            >
              {link.label}
            </a>
          ))}
        </nav>

        <div className="ml-auto flex items-center gap-3 text-sm">
          <span className="hidden text-slate-300 md:inline">
            {user?.full_name}
            {user?.is_admin && <span className="ml-2 rounded bg-stripe px-1.5 py-0.5 text-xs font-semibold text-asphalt">Admin</span>}
          </span>
          <button type="button" onClick={logout} className="rounded-md border border-slate-500 px-3 py-1.5 hover:bg-asphalt-soft">
            Log out
          </button>
        </div>
      </div>
    </header>
  );
}
