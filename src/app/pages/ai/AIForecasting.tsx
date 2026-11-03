import { useState } from "react";
import { Brain, Activity, Info, FlaskConical, Lightbulb } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Badge } from "../../components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../components/ui/tabs";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, BarChart, Bar, ErrorBar, Cell } from "recharts";
import { useFetch } from "../../lib/useFetch";
import { DataState } from "../../components/DataState";
import { api } from "../../lib/api";
import { toast } from "sonner";

interface Result {
  track: "A" | "B";
  info_set: string;
  model: string;
  label: string;
  mae: number | null;
  rmse: number | null;
  mape: number | null;
  wape: number | null;
  r2: number | null;
  cv_wape_mean: number | null;
  cv_wape_sd: number | null;
  p_vs_baseline: number | null;
  p_vs_best: number | null;
  n_test: number | null;
}

interface ForecastData {
  design: { splitDate: string | null; trainDays: number; testDays: number; testRecords: number | null; cvFolds: number };
  trackA: Result[];
  trackB: Result[];
  best: { A: string | null; B: string | null };
  series: Record<string, number | string>[];
  itemAverages: { item: string; avgQty: number; records: number }[];
}

const TOOLTIP_STYLE = { backgroundColor: "var(--card)", border: "1px solid var(--border)", borderRadius: "8px" };
const LINE_COLORS: Record<string, string> = {
  "Prophet": "#3b82f6",
  "LSTM": "#8b5cf6",
  "Random Forest": "#f59e0b",
  "Mean baseline": "#9ca3af",
  "Seasonal naive": "#6b7280",
};
const INFO_LABEL: Record<string, string> = {
  baseline: "Baseline",
  A1: "A1: history + calendar",
  A2: "A2: + promotion, event, weather",
  B: "Same feature table",
  reference: "Reference only",
};

const fmt = (n: number | null | undefined, d = 1) => (n === null || n === undefined || !Number.isFinite(n) ? "-" : n.toFixed(d));
const fmtP = (p: number | null | undefined) => (p === null || p === undefined ? "-" : p < 0.001 ? "<0.001" : p.toFixed(3));

function PValue({ p }: { p: number | null }) {
  if (p === null || p === undefined) return <span className="text-muted-foreground">-</span>;
  return <span className={p < 0.05 ? "font-medium" : "text-muted-foreground"}>{fmtP(p)}{p < 0.05 ? " *" : ""}</span>;
}

function ResultsTable({ rows, best, baselineName, showInfo, showCv }: {
  rows: Result[]; best: string | null; baselineName: string; showInfo: boolean; showCv: boolean;
}) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border text-left">
            <th className="py-2 px-3 font-medium">Model</th>
            {showInfo && <th className="py-2 px-3 font-medium">Information</th>}
            <th className="py-2 px-3 font-medium text-right">WAPE</th>
            <th className="py-2 px-3 font-medium text-right">MAE</th>
            <th className="py-2 px-3 font-medium text-right">R&sup2;</th>
            {showCv && <th className="py-2 px-3 font-medium text-right">Rolling WAPE</th>}
            <th className="py-2 px-3 font-medium text-right">p vs {baselineName}</th>
            <th className="py-2 px-3 font-medium text-right">p vs best</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.label} className={`border-b border-border ${r.label === best ? "bg-[var(--eco-green)]/10" : ""}`}>
              <td className="py-2 px-3 font-medium">
                {r.model}
                {r.label === best && <Badge className="ml-2 bg-[var(--eco-green)]">lowest error</Badge>}
              </td>
              {showInfo && <td className="py-2 px-3 text-muted-foreground">{INFO_LABEL[r.info_set] ?? r.info_set}</td>}
              <td className="py-2 px-3 text-right">{fmt(r.wape)}%</td>
              <td className="py-2 px-3 text-right">{fmt(r.mae, 0)}</td>
              <td className="py-2 px-3 text-right">{fmt(r.r2, 2)}</td>
              {showCv && (
                <td className="py-2 px-3 text-right">
                  {r.cv_wape_mean !== null ? `${fmt(r.cv_wape_mean)} ± ${fmt(r.cv_wape_sd)}%` : "-"}
                </td>
              )}
              <td className="py-2 px-3 text-right"><PValue p={r.p_vs_baseline} /></td>
              <td className="py-2 px-3 text-right"><PValue p={r.p_vs_best} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function AIForecasting() {
  const { data, loading, error, refetch } = useFetch<ForecastData>("/forecast");
  const [training, setTraining] = useState(false);
  const [infoSet, setInfoSet] = useState<"A1" | "A2">("A2");

  async function handleTrain() {
    setTraining(true);
    try {
      const res = await api.post("/forecast/train");
      toast.success(res.data?.message || "Retraining started");
      refetch();
    } catch (e: any) {
      toast.error(e.response?.data?.message || "Could not start retraining");
    } finally {
      setTraining(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="flex items-center gap-2">
            <Brain className="w-8 h-8 text-[var(--ai-purple)]" />
            Model Comparison
          </h1>
          <p className="text-muted-foreground mt-1">
            Every model in a track receives the same information and is tested on the same unseen days
          </p>
        </div>
        <Button variant="outline" onClick={handleTrain} disabled={training}>
          <Activity className="w-4 h-4 mr-2" />
          {training ? "Starting..." : "Retrain Models"}
        </Button>
      </div>

      <DataState loading={loading} error={error}>
        {data && (() => {
          const forecasts = data.trackA.filter((r) => r.info_set !== "reference");
          const reference = data.trackA.find((r) => r.info_set === "reference");
          const bestA = forecasts.find((r) => r.label === data.best.A);
          const bestB = data.trackB.find((r) => r.label === data.best.B);
          const ruleB = data.trackB.find((r) => r.model.startsWith("Historical average"));
          const meanA = forecasts.find((r) => r.model === "Mean baseline");
          const otherModels = forecasts.filter((r) => r.label !== data.best.A && r.info_set !== "baseline");
          const tiedWithBest = otherModels.filter((r) => (r.p_vs_best ?? 0) >= 0.05);
          const lineKeys = forecasts.filter((r) => r.info_set === "baseline" || r.info_set === infoSet).map((r) => r.label);
          const barA = forecasts.map((r) => ({ label: r.label, wape: r.cv_wape_mean, sd: r.cv_wape_sd }));
          const barB = data.trackB.map((r) => ({ label: r.model, wape: r.wape }));

          return (
            <div className="space-y-6">
              <Card className="border-[var(--ai-purple)]/40 bg-[var(--ai-purple)]/5">
                <CardHeader className="pb-2">
                  <CardTitle className="flex items-center gap-2 text-base">
                    <Lightbulb className="w-5 h-5 text-[var(--ai-purple)]" />
                    Key findings
                  </CardTitle>
                </CardHeader>
                <CardContent className="text-sm space-y-2">
                  {bestA && meanA && (
                    <p>
                      <span className="font-medium">Daily total demand:</span> the lowest error is {bestA.label} at {fmt(bestA.wape)}% WAPE,
                      against {fmt(meanA.wape)}% for always predicting the average.
                      {tiedWithBest.length > 0 && tiedWithBest.length === otherModels.length
                        && ` None of the other ${otherModels.length} forecasting models differs significantly from it (Diebold-Mariano p ≥ 0.05), so no algorithm clearly wins when the information is equal.`}
                      {tiedWithBest.length > 0 && tiedWithBest.length < otherModels.length
                        && ` ${tiedWithBest.length} of the other ${otherModels.length} forecasting models do not differ significantly from it (Diebold-Mariano p ≥ 0.05).`}
                    </p>
                  )}
                  {bestB && ruleB && (
                    <p>
                      <span className="font-medium">Item level:</span> {bestB.label} reduces the error from {fmt(ruleB.wape)}% (historical
                      average rule) to {fmt(bestB.wape)}% WAPE, with R&sup2; {fmt(bestB.r2, 2)}.
                    </p>
                  )}
                  {reference && (
                    <p className="text-muted-foreground">
                      The earlier design summed item-level predictions over the records that actually occurred each day and reached{" "}
                      {fmt(reference.wape)}% WAPE, but the number of records per day is not known in advance, so that figure is not a forecast.
                    </p>
                  )}
                </CardContent>
              </Card>

              <Tabs defaultValue="daily" className="space-y-6">
                <TabsList className="grid w-full max-w-2xl grid-cols-4">
                  <TabsTrigger value="daily">Daily Total</TabsTrigger>
                  <TabsTrigger value="items">Item Level</TabsTrigger>
                  <TabsTrigger value="method">Method</TabsTrigger>
                  <TabsTrigger value="menu">Menu Items</TabsTrigger>
                </TabsList>

                <TabsContent value="daily" className="space-y-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>Track A: Daily Total Demand</CardTitle>
                      <CardDescription>
                        Test period of {data.design.testDays} days from {data.design.splitDate}. Rolling WAPE is the mean and
                        standard deviation over {data.design.cvFolds} later windows. * marks p &lt; 0.05 (Diebold-Mariano).
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <ResultsTable rows={forecasts} best={data.best.A} baselineName="mean" showInfo showCv />
                      {reference && (
                        <div className="rounded-lg border border-dashed border-border p-3 text-sm text-muted-foreground">
                          <span className="font-medium text-foreground">Reference, not a forecast:</span> {reference.label} reaches{" "}
                          {fmt(reference.wape)}% WAPE (R&sup2; {fmt(reference.r2, 2)}) because it sums predictions over the records that
                          actually occurred on each day.
                        </div>
                      )}
                    </CardContent>
                  </Card>

                  <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
                    <Card className="lg:col-span-3">
                      <CardHeader>
                        <div className="flex items-center justify-between gap-4">
                          <div>
                            <CardTitle>Forecasts vs Actual Demand</CardTitle>
                            <CardDescription>Daily total portions over the test period</CardDescription>
                          </div>
                          <div className="flex gap-1">
                            {(["A1", "A2"] as const).map((k) => (
                              <Button key={k} size="sm" variant={infoSet === k ? "default" : "outline"} onClick={() => setInfoSet(k)}>{k}</Button>
                            ))}
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <ResponsiveContainer width="100%" height={340}>
                          <LineChart data={data.series}>
                            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                            <XAxis dataKey="day" className="text-xs" minTickGap={24} />
                            <YAxis className="text-xs" />
                            <Tooltip contentStyle={TOOLTIP_STYLE} />
                            <Legend />
                            <Line isAnimationActive={false} type="monotone" dataKey="actual" stroke="#10b981" strokeWidth={2.5} name="Actual" dot={false} />
                            {lineKeys.map((key) => (
                              <Line key={key} isAnimationActive={false} type="monotone" dataKey={key} name={key} dot={false}
                                stroke={LINE_COLORS[key.replace(/ \(A[12]\)$/, "")] ?? "#999"} strokeWidth={1.5}
                                strokeDasharray={key.includes("baseline") || key.includes("naive") ? "4 4" : undefined} />
                            ))}
                          </LineChart>
                        </ResponsiveContainer>
                      </CardContent>
                    </Card>

                    <Card className="lg:col-span-2">
                      <CardHeader>
                        <CardTitle>Rolling WAPE</CardTitle>
                        <CardDescription>Mean over {data.design.cvFolds} windows, bars show one standard deviation</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <ResponsiveContainer width="100%" height={340}>
                          <BarChart data={barA} layout="vertical" margin={{ left: 40 }}>
                            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                            <XAxis type="number" unit="%" className="text-xs" />
                            <YAxis type="category" dataKey="label" width={120} className="text-xs" />
                            <Tooltip contentStyle={TOOLTIP_STYLE} formatter={(v: number) => `${fmt(v)}%`} />
                            <Bar isAnimationActive={false} dataKey="wape" name="Rolling WAPE">
                              {barA.map((b) => <Cell key={b.label} fill={b.label === data.best.A ? "#10b981" : "#8b5cf6"} />)}
                              <ErrorBar dataKey="sd" width={4} strokeWidth={1.5} stroke="#374151" direction="x" />
                            </Bar>
                          </BarChart>
                        </ResponsiveContainer>
                      </CardContent>
                    </Card>
                  </div>
                </TabsContent>

                <TabsContent value="items" className="space-y-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>Track B: Item-Level Demand</CardTitle>
                      <CardDescription>
                        One prediction per restaurant, menu item and day ({data.design.testRecords?.toLocaleString()} test records).
                        Every model uses the same features; * marks p &lt; 0.05 (Diebold-Mariano).
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ResultsTable rows={data.trackB} best={data.best.B} baselineName="historical average rule" showInfo={false} showCv={false} />
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader>
                      <CardTitle>Item-Level Error</CardTitle>
                      <CardDescription>WAPE on the test records, lower is better</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={barB}>
                          <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                          <XAxis dataKey="label" className="text-xs" interval={0} />
                          <YAxis unit="%" className="text-xs" />
                          <Tooltip contentStyle={TOOLTIP_STYLE} formatter={(v: number) => `${fmt(v)}%`} />
                          <Bar isAnimationActive={false} dataKey="wape" name="WAPE">
                            {barB.map((b) => <Cell key={b.label} fill={b.label === data.best.B ? "#10b981" : "#8b5cf6"} />)}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="method" className="space-y-6">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <FlaskConical className="w-5 h-5 text-[var(--ai-purple)]" />
                        How the comparison is controlled
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4 text-sm">
                      <p>
                        <span className="font-medium">Same split for everything.</span> The first {data.design.trainDays} days train the models
                        and the last {data.design.testDays} days (from {data.design.splitDate}) test them. No test day is used in training.
                      </p>
                      <p>
                        <span className="font-medium">Track A, daily total demand.</span> Every model forecasts one day ahead from the demand
                        history up to the previous day, and is run twice: A1 adds the calendar, A2 also adds the share of records on promotion,
                        at a special event and in each weather type (treated as known in advance). LSTM reads the previous 28 days, Prophet is
                        refitted every day with weekly seasonality, and the Random Forest uses lagged demand. The number of records on a day is
                        never used, because it is not known in advance.
                      </p>
                      <p>
                        <span className="font-medium">Track B, item level.</span> One prediction for each restaurant, menu item and day in the data
                        (the items on each restaurant's menu that day). Every model gets the same table: restaurant, restaurant type,
                        menu item, meal type, prices, promotion, event, weather, calendar, and the average of that restaurant's earlier sales of
                        the item (earlier days only). LSTM and Prophet are not used here, because each restaurant and item pair has only a few
                        dozen irregular observations, too few for a per-series time-series model.
                      </p>
                      <p>
                        <span className="font-medium">Robustness and significance.</span> Track A is repeated over {data.design.cvFolds} rolling
                        windows. The Diebold-Mariano test checks whether the difference between two models' errors is larger than chance would
                        explain. At item level the test uses one value per test day, because records on the same day are not independent.
                      </p>
                      <div className="flex gap-2 rounded-lg bg-muted/50 p-3">
                        <Info className="w-4 h-4 mt-0.5 shrink-0" />
                        <p className="text-muted-foreground">
                          WAPE is total absolute error divided by total demand. R&sup2; compares against always predicting the average:
                          0 means no better, 1 means perfect.
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="menu" className="space-y-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>Average Demand per Menu Item</CardTitle>
                      <CardDescription>
                        Historical average portions per restaurant per day across the whole dataset (descriptive, not a forecast)
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b border-border">
                              <th className="text-left py-2 px-3 font-medium">Menu item</th>
                              <th className="text-right py-2 px-3 font-medium">Average portions</th>
                              <th className="text-right py-2 px-3 font-medium">Records</th>
                            </tr>
                          </thead>
                          <tbody>
                            {data.itemAverages.map((row) => (
                              <tr key={row.item} className="border-b border-border">
                                <td className="py-2 px-3">{row.item}</td>
                                <td className="py-2 px-3 text-right">{row.avgQty}</td>
                                <td className="py-2 px-3 text-right text-muted-foreground">{row.records}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>
              </Tabs>
            </div>
          );
        })()}
      </DataState>
    </div>
  );
}
