import { Link } from "react-router";
import { Plus, Calculator, ClipboardList, AlertCircle, DollarSign, Info } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Progress } from "../../components/ui/progress";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from "recharts";
import { useFetch } from "../../lib/useFetch";
import { DataState } from "../../components/DataState";

const CATEGORY_COLORS = ["#10b981", "#3b82f6", "#f59e0b", "#8b5cf6", "#ef4444", "#06b6d4", "#ec4899"];
const TOOLTIP_STYLE = { backgroundColor: "var(--card)", border: "1px solid var(--border)", borderRadius: "8px" };

interface Overview {
  estimated: {
    portions: number;
    cost: number;
    days: number;
    method: string | null;
    daily: { day: string; portions: number }[];
    byItem: { name: string; portions: number; cost: number }[];
  };
  logged: {
    entries: number;
    cost: number;
    byReason: { name: string; entries: number; cost: number }[];
    byItem: { name: string; entries: number; cost: number }[];
  };
  salesAnomalies: number;
}

export function WasteManagement() {
  const { data, loading, error } = useFetch<Overview>("/waste/overview");

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1>Waste Management</h1>
          <p className="text-muted-foreground mt-1">Simulated overproduction and manually logged waste</p>
        </div>
        <Button asChild className="bg-gradient-to-r from-[var(--eco-green)] to-[var(--eco-green-dark)]">
          <Link to="/app/waste/log">
            <Plus className="w-4 h-4 mr-2" />
            Log Waste
          </Link>
        </Button>
      </div>

      <DataState loading={loading} error={error}>
        {data && (
          <div className="space-y-6">
            <Card className="border-[var(--warning-orange)]/40 bg-[var(--warning-orange)]/5">
              <CardContent className="p-4 flex gap-3 text-sm">
                <Info className="w-5 h-5 shrink-0 text-[var(--warning-orange)]" />
                <p>
                  The public dataset records sales only, so waste is not measured. Overproduction here is simulated: the
                  model's preparation plan (forecast plus safety margin) minus actual sales, for each restaurant, item and
                  test day. See <Link to="/app/waste/simulation" className="underline">Simulation</Link> for the comparison
                  with the historical average rule. Logged waste comes only from entries made in this application and is kept separate.
                </p>
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">Simulated Overproduction</CardTitle>
                  <Calculator className="w-4 h-4 text-[var(--warning-orange)]" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-semibold">{Math.round(data.estimated.portions).toLocaleString()} portions</div>
                  <p className="text-xs text-muted-foreground mt-1">over {data.estimated.days} test-period days</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">Simulated Ingredient Cost</CardTitle>
                  <DollarSign className="w-4 h-4 text-[var(--error-red)]" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-semibold">${Math.round(data.estimated.cost).toLocaleString()}</div>
                  <p className="text-xs text-muted-foreground mt-1">wasted portions x ingredient cost</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">Logged Waste Entries</CardTitle>
                  <ClipboardList className="w-4 h-4 text-[var(--eco-green)]" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-semibold">{data.logged.entries}</div>
                  <p className="text-xs text-muted-foreground mt-1">${data.logged.cost.toLocaleString()} cost entered</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">Unusual Sales Days</CardTitle>
                  <AlertCircle className="w-4 h-4 text-[var(--warning-orange)]" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-semibold">{data.salesAnomalies}</div>
                  <p className="text-xs text-muted-foreground mt-1">
                    <Link to="/app/ai/anomaly-detection" className="hover:underline">see Anomaly Detection</Link>
                  </p>
                </CardContent>
              </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Simulated Overproduction by Day</CardTitle>
                  <CardDescription>Last 14 days of the test period, in portions</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={data.estimated.daily}>
                      <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                      <XAxis dataKey="day" className="text-xs" />
                      <YAxis className="text-xs" />
                      <Tooltip contentStyle={TOOLTIP_STYLE} />
                      <Bar isAnimationActive={false} dataKey="portions" fill="#ef4444" name="Estimated portions" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Logged Waste by Reason</CardTitle>
                  <CardDescription>Number of entries made in the application</CardDescription>
                </CardHeader>
                <CardContent>
                  {data.logged.byReason.length === 0 ? (
                    <div className="h-[300px] flex flex-col items-center justify-center text-center text-sm text-muted-foreground">
                      <p>No waste has been logged yet.</p>
                      <Link to="/app/waste/log" className="text-[var(--eco-green)] hover:underline mt-1">Log a waste entry</Link>
                    </div>
                  ) : (
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie isAnimationActive={false}
                          data={data.logged.byReason}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                          outerRadius={100}
                          dataKey="entries"
                        >
                          {data.logged.byReason.map((_, index) => (
                            <Cell key={`cell-${index}`} fill={CATEGORY_COLORS[index % CATEGORY_COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip contentStyle={TOOLTIP_STYLE} />
                      </PieChart>
                    </ResponsiveContainer>
                  )}
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Simulated Overproduction by Menu Item</CardTitle>
                <CardDescription>Whole test period, all restaurants, in portions</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={320}>
                  <BarChart data={data.estimated.byItem} layout="vertical" margin={{ left: 40 }}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                    <XAxis type="number" className="text-xs" />
                    <YAxis type="category" dataKey="name" width={130} className="text-xs" />
                    <Tooltip contentStyle={TOOLTIP_STYLE} />
                    <Bar isAnimationActive={false} dataKey="portions" fill="#f59e0b" name="Portions" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Logged Waste by Item</CardTitle>
                <CardDescription>Items with the highest cost entered</CardDescription>
              </CardHeader>
              <CardContent>
                {data.logged.byItem.length === 0 && (
                  <p className="text-sm text-muted-foreground">No waste has been logged yet.</p>
                )}
                <div className="space-y-4">
                  {(() => {
                    const maxCost = Math.max(...data.logged.byItem.map((i) => i.cost), 1);
                    return data.logged.byItem.map((item, index) => (
                      <div key={index} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="font-medium">{item.name}</span>
                          <div className="flex items-center gap-4">
                            <span className="text-sm text-muted-foreground">{item.entries} entries</span>
                            <span className="text-sm font-medium text-[var(--error-red)]">${item.cost}</span>
                          </div>
                        </div>
                        <Progress value={(item.cost / maxCost) * 100} className="h-2" />
                      </div>
                    ));
                  })()}
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </DataState>
    </div>
  );
}
