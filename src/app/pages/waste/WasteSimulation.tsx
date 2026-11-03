import { useState } from "react";
import { FlaskConical, TrendingDown, Target, Scale, Info } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Slider } from "../../components/ui/slider";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, ReferenceLine } from "recharts";
import { useFetch } from "../../lib/useFetch";
import { DataState } from "../../components/DataState";

interface Row {
  policy: string;
  margin: number;
  prepared: number;
  overproduction: number;
  shortfall: number;
  fill_rate: number;
  short_days_pct: number;
  waste_cost: number;
  lost_margin: number;
}

interface Summary {
  baseline: string;
  model: string;
  default_margin: number;
  baseline_overproduction: number;
  baseline_fill_rate: number;
  baseline_waste_cost: number;
  same_margin_overproduction: number;
  same_margin_fill_rate: number;
  same_margin_waste_cost: number;
  same_margin_reduction_pct: number;
  same_margin_reduction_ci: [number, number];
  same_margin_fill_gain: number;
  same_margin_fill_gain_ci: [number, number];
  matched_margin: number;
  matched_overproduction: number;
  matched_fill_rate: number;
  matched_reduction_pct: number;
  matched_reduction_ci: [number, number];
  test_records: number;
  test_days: number;
  actual_demand: number;
}

interface SimulationData {
  summary: Summary | null;
  policies: Record<string, Row[]>;
  assumptions: string[];
}

const TOOLTIP_STYLE = { backgroundColor: "var(--card)", border: "1px solid var(--border)", borderRadius: "8px" };
const n0 = (v: number) => Math.round(v).toLocaleString();
const p1 = (v: number) => v.toFixed(1);

export function WasteSimulation() {
  const { data, loading, error } = useFetch<SimulationData>("/simulation");
  const [margin, setMargin] = useState(10);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="flex items-center gap-2">
          <FlaskConical className="w-8 h-8 text-[var(--ai-purple)]" />
          Preparation Simulation
        </h1>
        <p className="text-muted-foreground mt-1">
          Two preparation plans replayed on the test period: how much would be over-prepared, and how much demand would be missed
        </p>
      </div>

      <DataState loading={loading} error={error}>
        {data && data.summary && (() => {
          const s = data.summary;
          const base = data.policies[s.baseline] ?? [];
          const model = data.policies[s.model] ?? [];
          const at = (rows: Row[]) => rows.find((r) => Math.round(r.margin * 100) === margin);
          const b = at(base);
          const m = at(model);
          const curve = base.map((r, i) => ({
            margin: Math.round(r.margin * 100),
            [`${s.baseline} overproduction`]: r.overproduction,
            [`${s.model} overproduction`]: model[i]?.overproduction,
            [`${s.baseline} fill`]: r.fill_rate,
            [`${s.model} fill`]: model[i]?.fill_rate,
          }));
          const tradeoff = [
            ...base.map((r) => ({ fill: r.fill_rate, [s.baseline]: r.overproduction })),
            ...model.map((r) => ({ fill: r.fill_rate, [s.model]: r.overproduction })),
          ].sort((x, y) => x.fill - y.fill);
          const pct = Math.round(s.default_margin * 100);

          return (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Same {pct}% safety margin</CardTitle>
                    <TrendingDown className="w-4 h-4 text-[var(--eco-green)]" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-semibold">{p1(s.same_margin_reduction_pct)}% less overproduction</div>
                    <p className="text-xs text-muted-foreground mt-1">
                      95% CI {p1(s.same_margin_reduction_ci[0])} to {p1(s.same_margin_reduction_ci[1])}%, while serving{" "}
                      {p1(s.same_margin_fill_gain)} points more demand (CI {p1(s.same_margin_fill_gain_ci[0])} to {p1(s.same_margin_fill_gain_ci[1])})
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Same share of demand served</CardTitle>
                    <Target className="w-4 h-4 text-[var(--ai-purple)]" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-semibold">{p1(s.matched_reduction_pct)}% less overproduction</div>
                    <p className="text-xs text-muted-foreground mt-1">
                      Both plans serve {p1(s.baseline_fill_rate)}% of demand (model margin {(s.matched_margin * 100).toFixed(1)}%);
                      95% CI {p1(s.matched_reduction_ci[0])} to {p1(s.matched_reduction_ci[1])}%. Optimistic, because the margin is
                      chosen on the test days.
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Simulated ingredient cost wasted</CardTitle>
                    <Scale className="w-4 h-4 text-[var(--warning-orange)]" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-semibold">${n0(s.baseline_waste_cost)} &rarr; ${n0(s.same_margin_waste_cost)}</div>
                    <p className="text-xs text-muted-foreground mt-1">
                      Historical average rule vs {s.model} at {pct}% margin, {s.test_days} test days across all 50 restaurants
                    </p>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>Compare at a Safety Margin</CardTitle>
                  <CardDescription>
                    Move the slider to change the margin added to both plans. A bigger margin wastes more but misses less demand.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="flex items-center gap-4 max-w-xl">
                    <span className="text-sm w-28">Margin: <span className="font-semibold">{margin}%</span></span>
                    <Slider value={[margin]} min={0} max={20} step={1} onValueChange={(v) => setMargin(v[0])} />
                  </div>
                  {b && m && (
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b border-border text-left">
                            <th className="py-2 px-3 font-medium">Plan</th>
                            <th className="py-2 px-3 font-medium text-right">Overproduction (portions)</th>
                            <th className="py-2 px-3 font-medium text-right">Unmet demand (portions)</th>
                            <th className="py-2 px-3 font-medium text-right">Demand served</th>
                            <th className="py-2 px-3 font-medium text-right">Ingredient cost wasted</th>
                            <th className="py-2 px-3 font-medium text-right">Margin lost on unmet demand</th>
                          </tr>
                        </thead>
                        <tbody>
                          {[b, m].map((r) => (
                            <tr key={r.policy} className="border-b border-border">
                              <td className="py-2 px-3 font-medium">{r.policy}</td>
                              <td className="py-2 px-3 text-right">{n0(r.overproduction)}</td>
                              <td className="py-2 px-3 text-right">{n0(r.shortfall)}</td>
                              <td className="py-2 px-3 text-right">{p1(r.fill_rate)}%</td>
                              <td className="py-2 px-3 text-right">${n0(r.waste_cost)}</td>
                              <td className="py-2 px-3 text-right">${n0(r.lost_margin)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </CardContent>
              </Card>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Overproduction by Safety Margin</CardTitle>
                    <CardDescription>Portions prepared but not sold over the test period</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={curve}>
                        <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                        <XAxis dataKey="margin" unit="%" className="text-xs" />
                        <YAxis className="text-xs" tickFormatter={(v) => `${Math.round(v / 1000)}k`} />
                        <Tooltip contentStyle={TOOLTIP_STYLE} formatter={(v: number) => n0(v)} labelFormatter={(l) => `Margin ${l}%`} />
                        <Legend />
                        <ReferenceLine x={margin} stroke="#9ca3af" strokeDasharray="3 3" />
                        <Line isAnimationActive={false} dataKey={`${s.baseline} overproduction`} name={s.baseline} stroke="#ef4444" dot={false} strokeWidth={2} />
                        <Line isAnimationActive={false} dataKey={`${s.model} overproduction`} name={s.model} stroke="#10b981" dot={false} strokeWidth={2} />
                      </LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Waste vs Service Trade-off</CardTitle>
                    <CardDescription>
                      Each point is one margin from 0% to 20%. Lower and further right is better.
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={tradeoff}>
                        <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                        <XAxis dataKey="fill" type="number" domain={["dataMin", "dataMax"]} unit="%" className="text-xs"
                          tickFormatter={(v) => v.toFixed(0)} name="Demand served" />
                        <YAxis className="text-xs" tickFormatter={(v) => `${Math.round(v / 1000)}k`} />
                        <Tooltip contentStyle={TOOLTIP_STYLE} formatter={(v: number) => n0(v)} labelFormatter={(l) => `${Number(l).toFixed(1)}% of demand served`} />
                        <Legend />
                        <Line isAnimationActive={false} dataKey={s.baseline} stroke="#ef4444" connectNulls dot={{ r: 2 }} />
                        <Line isAnimationActive={false} dataKey={s.model} stroke="#10b981" connectNulls dot={{ r: 2 }} />
                      </LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>

              <Card className="border-[var(--warning-orange)]/40 bg-[var(--warning-orange)]/5">
                <CardHeader className="pb-2">
                  <CardTitle className="flex items-center gap-2 text-base">
                    <Info className="w-5 h-5 text-[var(--warning-orange)]" />
                    Assumptions
                  </CardTitle>
                  <CardDescription>
                    {s.test_records.toLocaleString()} item-level records on {s.test_days} test days, {n0(s.actual_demand)} portions of demand.
                    95% confidence intervals come from resampling the test days 1,000 times.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="list-disc pl-5 space-y-1 text-sm">
                    {data.assumptions.map((a) => <li key={a}>{a}</li>)}
                  </ul>
                </CardContent>
              </Card>
            </div>
          );
        })()}
        {data && !data.summary && <p className="text-sm text-muted-foreground">No simulation results. Run precompute.py.</p>}
      </DataState>
    </div>
  );
}
