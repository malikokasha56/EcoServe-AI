import {
  ShoppingBag,
  Target,
  DollarSign,
  Gauge,
  Trash2,
  Package,
  AlertTriangle,
  Clock,
  Lightbulb,
  Sparkles
} from "lucide-react";
import { Link } from "react-router";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { LineChart, Line, BarChart, Bar, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { useFetch } from "../../lib/useFetch";
import { DataState } from "../../components/DataState";

const KPI_STYLE: Record<string, { icon: any; color: string; bgColor: string }> = {
  "Sales (latest day)": { icon: ShoppingBag, color: "text-[var(--ai-blue)]", bgColor: "bg-[var(--ai-blue)]/10" },
  "Forecast (latest day)": { icon: Target, color: "text-[var(--ai-purple)]", bgColor: "bg-[var(--ai-purple)]/10" },
  "Revenue (latest day)": { icon: DollarSign, color: "text-[var(--eco-green)]", bgColor: "bg-[var(--eco-green)]/10" },
  "Best model error (WAPE)": { icon: Gauge, color: "text-[var(--ai-purple)]", bgColor: "bg-[var(--ai-purple)]/10" },
  "Simulated overproduction": { icon: Trash2, color: "text-[var(--warning-orange)]", bgColor: "bg-[var(--warning-orange)]/10" },
  "Inventory health": { icon: Package, color: "text-[var(--eco-green)]", bgColor: "bg-[var(--eco-green)]/10" },
};

const TOOLTIP_STYLE = { backgroundColor: "var(--card)", border: "1px solid var(--border)", borderRadius: "8px" };

interface Summary {
  kpis: { title: string; value: string; note: string }[];
  forecastModel: string | null;
  salesTrend: { day: string; sales: number; predicted: number | null; waste: number }[];
  modelErrors: { model: string; wape: number }[];
  revenue: { day: string; revenue: number }[];
  recommendations: { id: number; title: string; description: string; category: string }[];
  lowStock: { name: string; quantity: string; status: string }[];
  expiring: { name: string; quantity: string; days: number }[];
}

export function Dashboard() {
  const { data, loading, error } = useFetch<Summary>("/dashboard/summary");

  return (
    <div className="space-y-6">
      <div>
        <h1>Dashboard Overview</h1>
        <p className="text-muted-foreground mt-1">
          Latest trading days in the dataset, with model forecasts and estimates
        </p>
      </div>

      <DataState loading={loading} error={error}>
        {data && data.kpis && (
          <div className="space-y-6">
            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {data.kpis.map((kpi, index) => {
                const style = KPI_STYLE[kpi.title] || { icon: Sparkles, color: "text-muted-foreground", bgColor: "bg-muted" };
                const Icon = style.icon;
                return (
                  <Card key={index} className="hover:shadow-lg transition-shadow">
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                      <CardTitle className="text-sm font-medium text-muted-foreground">{kpi.title}</CardTitle>
                      <div className={`p-2 rounded-lg ${style.bgColor}`}>
                        <Icon className={`w-4 h-4 ${style.color}`} />
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-semibold">{kpi.value}</div>
                      <p className="text-xs text-muted-foreground mt-1">{kpi.note}</p>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            {/* Charts Row 1 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Daily Demand vs Forecast</CardTitle>
                  <CardDescription>
                    Actual portions sold vs {data.forecastModel ?? "model"} forecast (last 7 days)
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={data.salesTrend}>
                      <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                      <XAxis dataKey="day" className="text-xs" />
                      <YAxis className="text-xs" />
                      <Tooltip contentStyle={TOOLTIP_STYLE} />
                      <Legend />
                      <Line isAnimationActive={false} type="monotone" dataKey="sales" stroke="#10b981" strokeWidth={2} name="Actual demand" />
                      <Line isAnimationActive={false} type="monotone" dataKey="predicted" stroke="#8b5cf6" strokeWidth={2} strokeDasharray="5 5" name="Forecast" />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Forecast Error by Model</CardTitle>
                  <CardDescription>WAPE on the held-out test period, lower is better</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={data.modelErrors}>
                      <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                      <XAxis dataKey="model" className="text-xs" interval={0} angle={-25} textAnchor="end" height={70} />
                      <YAxis className="text-xs" unit="%" />
                      <Tooltip contentStyle={TOOLTIP_STYLE} />
                      <Bar isAnimationActive={false} dataKey="wape" fill="#8b5cf6" name="WAPE (%)" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>

            {/* Charts Row 2 */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <Card className="lg:col-span-2">
                <CardHeader>
                  <CardTitle>Revenue</CardTitle>
                  <CardDescription>Daily revenue across all restaurants (last 7 days)</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={250}>
                    <AreaChart data={data.revenue}>
                      <defs>
                        <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                      <XAxis dataKey="day" className="text-xs" />
                      <YAxis className="text-xs" />
                      <Tooltip contentStyle={TOOLTIP_STYLE} />
                      <Area isAnimationActive={false} type="monotone" dataKey="revenue" stroke="#10b981" fillOpacity={1} fill="url(#colorRevenue)" name="Revenue ($)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Simulated Overproduction</CardTitle>
                  <CardDescription>Portions from the model preparation plan (not measured)</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={250}>
                    <LineChart data={data.salesTrend}>
                      <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                      <XAxis dataKey="day" className="text-xs" />
                      <YAxis className="text-xs" />
                      <Tooltip contentStyle={TOOLTIP_STYLE} />
                      <Line isAnimationActive={false} type="monotone" dataKey="waste" stroke="#ef4444" strokeWidth={2} name="Simulated portions" />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>

            {/* Recommendations & Alerts */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <Card className="lg:col-span-2">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-[var(--ai-purple)]" />
                    Preparation Plan
                  </CardTitle>
                  <CardDescription>
                    Highest-volume items on the last test day. <Link to="/app/ai/recommendations" className="text-[var(--eco-green)] hover:underline">See all</Link>
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {data.recommendations.map((rec) => (
                    <div key={rec.id} className="flex items-start gap-4 p-4 rounded-lg border border-border hover:bg-accent/50 transition-colors">
                      <div className="p-2 rounded-lg bg-[var(--ai-purple)]/10">
                        <Lightbulb className="w-5 h-5 text-[var(--ai-purple)]" />
                      </div>
                      <div className="flex-1 space-y-1">
                        <h4 className="font-medium">{rec.title}</h4>
                        <p className="text-sm text-muted-foreground">{rec.description}</p>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>

              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-base">
                      <AlertTriangle className="w-4 h-4 text-[var(--warning-orange)]" />
                      Low Inventory
                    </CardTitle>
                    <CardDescription>Illustrative demo data</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {data.lowStock.length === 0 && <p className="text-sm text-muted-foreground">All stock levels healthy.</p>}
                    {data.lowStock.map((item, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <div>
                          <p className="font-medium text-sm">{item.name}</p>
                          <p className="text-xs text-muted-foreground">{item.quantity}</p>
                        </div>
                        <Badge variant={item.status === "critical" ? "destructive" : "secondary"} className="text-xs">{item.status}</Badge>
                      </div>
                    ))}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-base">
                      <Clock className="w-4 h-4 text-[var(--warning-orange)]" />
                      Expiring Soon
                    </CardTitle>
                    <CardDescription>Illustrative demo data</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {data.expiring.length === 0 && <p className="text-sm text-muted-foreground">Nothing expiring soon.</p>}
                    {data.expiring.map((item, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <div>
                          <p className="font-medium text-sm">{item.name}</p>
                          <p className="text-xs text-muted-foreground">{item.quantity}</p>
                        </div>
                        <Badge variant={item.days <= 1 ? "destructive" : "secondary"} className="text-xs">{item.days}d</Badge>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        )}
      </DataState>
    </div>
  );
}
