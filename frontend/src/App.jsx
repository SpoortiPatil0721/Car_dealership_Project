import Header from "./components/Header.jsx";
import { useAuth } from "./context/AuthContext.jsx";
import { useHashRoute } from "./hooks/useHashRoute.js";
import AuthPage from "./pages/AuthPage.jsx";
import InsightsPage from "./pages/InsightsPage.jsx";
import LotPage from "./pages/LotPage.jsx";
import ManagePage from "./pages/ManagePage.jsx";
import PurchasesPage from "./pages/PurchasesPage.jsx";

const PAGES = {
  lot: { component: LotPage },
  purchases: { component: PurchasesPage },
  manage: { component: ManagePage, adminOnly: true },
  insights: { component: InsightsPage, adminOnly: true },
};

export default function App() {
  const { user, checking } = useAuth();
  const route = useHashRoute();

  if (checking) return <p className="p-8 text-concrete">Opening the lot…</p>;
  if (!user) return <AuthPage />;

  // unknown routes and admin pages for non-admins both land on the lot
  const page = PAGES[route] && (!PAGES[route].adminOnly || user.is_admin) ? PAGES[route] : PAGES.lot;
  const Page = page.component;

  return (
    <div className="min-h-screen pb-16">
      <Header route={PAGES[route] === page ? route : "lot"} />
      <main>
        <Page />
      </main>
    </div>
  );
}
