import { useState } from "react";
import { Link } from "react-router";
import { Lightbulb, CheckCircle2, Info } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { useFetch } from "../../lib/useFetch";
import { DataState } from "../../components/DataState";
import { api } from "../../lib/api";
import { toast } from "sonner";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/select";

interface Recommendation {
  id: number;
  title: string;
  description: string;
  menu_item_name: string;
  recommended_quantity: number;
  rule_quantity: number | null;
  actual_quantity: number | null;
  restaurants: number | null;
  status: "pending" | "applied";
}

interface RecommendationsData {
  recommendations: Recommendation[];
  dates: string[];
  period: { days: number; modelCloserDays: number; modelItemError: number; ruleItemError: number } | null;
  summary: null | {
    date: string;
    model: string | null;
    planned: number;
    rule: number;
    actual: number;
    pending: number;
    applied: number;
    safetyMarginPct: number;
  };
}

const TOOLTIP_STYLE = { backgroundColor: "var(--card)", border: "1px solid var(--border)", borderRadius: "8px" };

export function Recommendations() {
  const [day, setDay] = useState<string | null>(null);
  const { data, loading, error, refetch } = useFetch<RecommendationsData>(day ? `/recommendations?date=${day}` : "/recommendations");
  const [applyingId, setApplyingId] = useState<number | null>(null);

  const handleApply = async (id: number) => {
    setApplyingId(id);
    try {
      await api.post(`/recommendations/${id}/apply`);
      refetch();
    } catch (e: any) {
      toast.error(e.response?.data?.message || "Could not mark as applied");
    } finally {
      setApplyingId(null);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="flex items-center gap-2">
          <Lightbulb className="w-8 h-8 text-[var(--ai-purple)]" />
          Preparation Plan
        </h1>
        <p className="text-muted-foreground mt-1">
          Suggested preparation quantities per menu item for any day of the test period
        </p>
      </div>

      <DataState loading={loading} error={error}>
        {data && !data.summary && <p className="text-sm text-muted-foreground">No preparation plans yet. Run precompute.py.</p>}
        {data && data.summary && (() => {
          const s = data.summary;
          const p = data.period;
          const off = (planned: number) => (s.actual ? ((planned - s.actual) / s.actual) * 100 : 0);
          const chart = data.recommendations.map((r) => ({
            item: r.menu_item_name,
            Model: r.recommended_quantity,
            "Historical average rule": r.rule_quantity,
            Sold: r.actual_quantity,
          }));
          return (
            <div className="space-y-6">
              <Card className="border-[var(--ai-blue)]/40 bg-[var(--ai-blue)]/5">
                <CardContent className="p-4 flex gap-3 text-sm">
                  <Info className="w-5 h-5 shrink-0 text-[var(--ai-blue)]" />
                  <p>
                    Each quantity is the {s.model ?? "model"} forecast for every restaurant with the item on its menu that day, plus a{" "}
                    {s.safetyMarginPct}% safety margin. The dataset ends on {data.dates[data.dates.length - 1]}, so plans are shown for past
                    test days (which the model never saw), next to what the historical-average rule would have prepared and what was
                    actually sold. A single day can go either way; the{" "}
                    <Link to="/app/waste/simulation" className="underline">Simulation</Link> page compares both plans over the whole period.
                  </p>
                </CardContent>
              </Card>

              <div className="flex flex-col md:flex-row md:items-center gap-4">
                <div className="flex items-center gap-3">
                  <span className="text-sm font-medium">Test day</span>
                  <Select value={s.date} onValueChange={(v) => setDay(v)}>
                    <SelectTrigger className="w-44">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {[...data.dates].reverse().map((d) => <SelectItem key={d} value={d}>{d}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                {p && (
                  <p className="text-sm text-muted-foreground">
                    Across all {p.days} test days the model plan was closer to actual sales on{" "}
                    <span className="font-medium text-foreground">{p.modelCloserDays} days</span>, and its total item-level
                    error was {p.modelItemError.toLocaleString()} portions against {p.ruleItemError.toLocaleString()} for the rule.
                  </p>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Model plan</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-semibold">{s.planned.toLocaleString()} portions</div>
                    <p className="text-xs text-muted-foreground mt-1">{off(s.planned) >= 0 ? "+" : ""}{off(s.planned).toFixed(0)}% vs portions sold</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Historical-average rule</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-semibold">{s.rule.toLocaleString()} portions</div>
                    <p className="text-xs text-muted-foreground mt-1">{off(s.rule) >= 0 ? "+" : ""}{off(s.rule).toFixed(0)}% vs portions sold</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Actually sold</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-semibold">{s.actual.toLocaleString()} portions</div>
                    <p className="text-xs text-muted-foreground mt-1">{s.applied} of {s.applied + s.pending} items marked applied</p>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>Planned vs Sold by Menu Item</CardTitle>
                  <CardDescription>Portions on {s.date}</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={320}>
                    <BarChart data={chart}>
                      <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                      <XAxis dataKey="item" className="text-xs" interval={0} angle={-20} textAnchor="end" height={60} />
                      <YAxis className="text-xs" />
                      <Tooltip contentStyle={TOOLTIP_STYLE} />
                      <Legend />
                      <Bar isAnimationActive={false} dataKey="Model" fill="#10b981" />
                      <Bar isAnimationActive={false} dataKey="Historical average rule" fill="#ef4444" />
                      <Bar isAnimationActive={false} dataKey="Sold" fill="#6b7280" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Suggestions</CardTitle>
                  <CardDescription>Mark a suggestion as applied once the preparation quantity has been set</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {data.recommendations.map((rec) => (
                    <div key={rec.id} className="p-4 rounded-lg border border-border hover:bg-accent/50 transition-colors">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 space-y-1">
                          <div className="flex items-center gap-3">
                            <h4 className="font-medium">{rec.title}</h4>
                            {rec.status === "applied" && (
                              <Badge variant="outline" className="bg-[var(--success-green)]/10 text-[var(--success-green)]">
                                <CheckCircle2 className="w-3 h-3 mr-1" />
                                Applied
                              </Badge>
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground">{rec.description}</p>
                          <p className="text-xs text-muted-foreground">
                            Historical-average rule: {rec.rule_quantity?.toLocaleString() ?? "-"} &middot; Actually sold: {rec.actual_quantity?.toLocaleString() ?? "-"}
                          </p>
                        </div>
                        {rec.status === "pending" && (
                          <Button
                            size="sm"
                            className="bg-gradient-to-r from-[var(--eco-green)] to-[var(--eco-green-dark)]"
                            disabled={applyingId === rec.id}
                            onClick={() => handleApply(rec.id)}
                          >
                            {applyingId === rec.id ? "Saving..." : "Mark Applied"}
                          </Button>
                        )}
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          );
        })()}
      </DataState>
    </div>
  );
}
