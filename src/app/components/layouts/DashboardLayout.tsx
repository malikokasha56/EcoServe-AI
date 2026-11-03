import { Outlet, Link, useLocation, useNavigate } from "react-router";
import { useAuth } from "../../context/AuthContext";
import {
  LayoutDashboard,
  ShoppingCart,
  Trash2,
  Package,
  Brain,
  Lightbulb,
  AlertTriangle,
  FileText,
  Workflow,
  Network,
  Menu,
  X,
  Sun,
  Moon,
  LogOut,
  User
} from "lucide-react";
import { useState } from "react";
import { Button } from "../ui/button";
import { useTheme } from "next-themes";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "../ui/dropdown-menu";
import { Avatar, AvatarFallback } from "../ui/avatar";

const navigation = [
  { name: "Dashboard", href: "/app", icon: LayoutDashboard },
  {
    name: "Sales",
    icon: ShoppingCart,
    children: [
      { name: "Overview", href: "/app/sales" },
      { name: "Add Sales", href: "/app/sales/add" },
      { name: "History", href: "/app/sales/history" },
    ]
  },
  {
    name: "Waste Management",
    icon: Trash2,
    children: [
      { name: "Overview", href: "/app/waste" },
      { name: "Log Waste", href: "/app/waste/log" },
      { name: "Simulation", href: "/app/waste/simulation" },
    ]
  },
  { name: "Inventory", href: "/app/inventory", icon: Package },
  {
    name: "AI Forecasting",
    icon: Brain,
    children: [
      { name: "Models", href: "/app/ai/forecasting" },
      { name: "Preparation", href: "/app/ai/recommendations" },
      { name: "Anomaly Detection", href: "/app/ai/anomaly-detection" },
    ]
  },
  { name: "Reports", href: "/app/reports", icon: FileText },
  { name: "ML Workflow", href: "/app/ml-workflow", icon: Workflow },
  { name: "Architecture", href: "/app/architecture", icon: Network },
];

export function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const { theme, setTheme } = useTheme();
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const initials = (user?.username || "Restaurant Manager")
    .split(" ")
    .map((w) => w[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  const isActive = (href: string) => {
    if (href === "/app") {
      return location.pathname === href;
    }
    return location.pathname.startsWith(href);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed top-0 left-0 z-50 h-screen w-64 bg-card border-r border-border
        transform transition-transform duration-300 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0
      `}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="h-16 flex items-center justify-between px-6 border-b border-border">
            <Link to="/app" className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--eco-green)] to-[var(--ai-purple)] flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <span className="font-semibold">EcoServe AI</span>
            </Link>
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden"
              onClick={() => setSidebarOpen(false)}
            >
              <X className="w-5 h-5" />
            </Button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto p-4 space-y-1">
            {navigation.map((item) => (
              <div key={item.name}>
                {item.children ? (
                  <div className="space-y-1">
                    <div className="px-3 py-2 text-sm text-muted-foreground flex items-center gap-2">
                      <item.icon className="w-4 h-4" />
                      <span>{item.name}</span>
                    </div>
                    {item.children.map((child) => (
                      <Link
                        key={child.href}
                        to={child.href}
                        className={`
                          block px-3 py-2 ml-6 text-sm rounded-lg transition-colors
                          ${location.pathname === child.href
                            ? 'bg-primary text-primary-foreground'
                            : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                          }
                        `}
                      >
                        {child.name}
                      </Link>
                    ))}
                  </div>
                ) : (
                  <Link
                    to={item.href!}
                    className={`
                      flex items-center gap-2 px-3 py-2 text-sm rounded-lg transition-colors
                      ${isActive(item.href!)
                        ? 'bg-primary text-primary-foreground'
                        : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                      }
                    `}
                  >
                    <item.icon className="w-4 h-4" />
                    <span>{item.name}</span>
                  </Link>
                )}
              </div>
            ))}
          </nav>

          {/* User section */}
          <div className="p-4 border-t border-border">
            <div className="text-xs text-muted-foreground mb-1">MSc Computing Project</div>
            <div className="text-xs text-muted-foreground">
              Data:{" "}
              <a
                href="https://www.kaggle.com/datasets/alexandchen/restaurant-sales-report-2024-2025"
                target="_blank"
                rel="noreferrer"
                className="hover:underline"
              >
                Restaurant Sales Report 2024-2025
              </a>{" "}
              (Kaggle, CC BY-SA 4.0)
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <header className="h-16 bg-card border-b border-border sticky top-0 z-30 flex items-center justify-between px-6">
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="w-5 h-5" />
          </Button>

          <div className="flex-1" />

          <div className="flex items-center gap-4">
            {/* Theme toggle */}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            >
              {theme === "dark" ? (
                <Sun className="w-5 h-5" />
              ) : (
                <Moon className="w-5 h-5" />
              )}
            </Button>

            {/* User menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="rounded-full">
                  <Avatar>
                    <AvatarFallback>{initials}</AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>{user?.username || "Restaurant Manager"}</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem>
                  <User className="mr-2 h-4 w-4" />
                  {user?.role || "Manager"}
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout}>
                  <LogOut className="mr-2 h-4 w-4" />
                  Logout
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        {/* Page content */}
        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
