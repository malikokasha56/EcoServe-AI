import { AlertTriangle, Activity, CalendarDays } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from "recharts";
import { useFetch } from "../../lib/useFetch";
import { DataState } from "../../components/DataState";

interface Anomaly {
  id: number;
  value: number;
  expected: number;
  method: string;
  severity: string;
  date: string;
}

interface AnomalyData {
  anomalies: Anomaly[];
  series: { date: string; value: number; anomaly: boolean }[];
  summary: {
    flagged: number;
    highSeverity: number;
    days: number;
    flaggedPct: number;
    mean: number | null;
    iqrLower: number | null;
    iqrUpper: number | null;
  };
}

const METHOD_LABEL: Record<string, string> = {
  "zscore": "Z-score",
  "iqr": "IQR rule",
  "zscore+iqr": "Z-score and IQR rule"
};

export function AnomalyDetection() {
  const { data, loading, error } = useFetch<AnomalyData>("/anomalies");
  const points = (data?.series ?? []).map((p, i) => ({ ...p, index: i }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="flex items-center gap-2">
          <AlertTriangle className="w-8 h-8 text-[var(--warning-orange)]" />
          Anomaly Detection
        </h1>
        <p className="text-muted-foreground mt-1">
          Unusual days in total daily sales. A day is flagged when its Z-score exceeds 3 or it lies more than
          1.5 interquartile ranges below the first quartile (Q1) or above the third quartile (Q3).
        </p>
      </div>

      <DataState loading={loading} error={error}>
        {data && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">Days Flagged</CardTitle>
                  <AlertTriangle className="w-4 h-4 text-[var(--warning-orange)]" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-semibold">{data.summary.flagged}</div>
                  <p className="text-xs text-muted-foreground mt-1">of {data.summary.days} days ({data.summary.flaggedPct}%)</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">High Severity</CardTitle>
                  <Activity className="w-4 h-4 text-[var(--error-red)]" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-semibold">{data.summary.highSeverity}</div>
                  <p className="text-xs text-muted-foreground mt-1">more than 4 standard deviations from the mean</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">Normal Range (IQR rule)</CardTitle>
                  <CalendarDays className="w-4 h-4 text-[var(--eco-green)]" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-semibold">
                    {data.summary.iqrLower?.toLocaleString()} to {data.summary.iqrUpper?.toLocaleString()}
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">portions per day (Q1 - 1.5 IQR to Q3 + 1.5 IQR)</p>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Daily Sales with Flagged Days</CardTitle>
                <CardDescription>
                  Every day in the dataset. Red points are flagged; dashed lines mark the IQR bounds and the mean.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={320}>
                  <ScatterChart>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="index"
                      type="number"
                      domain={[0, Math.max(points.length - 1, 0)]}
                      tickFormatter={(i: number) => points[i]?.date.slice(0, 7) ?? ""}
                      name="Date"
                    />
                    <YAxis dataKey="value" name="Portions" />
                    <Tooltip
                      cursor={{ strokeDasharray: "3 3" }}
                      formatter={(v: number, n: string) => (n === "Date" ? points[v]?.date : v)}
                    />
                    {data.summary.iqrUpper !== null && <ReferenceLine y={data.summary.iqrUpper} stroke="#ef4444" strokeDasharray="4 4" />}
                    {data.summary.iqrLower !== null && <ReferenceLine y={data.summary.iqrLower} stroke="#ef4444" strokeDasharray="4 4" />}
                    {data.summary.mean !== null && <ReferenceLine y={data.summary.mean} stroke="#6b7280" strokeDasharray="2 2" />}
                    <Scatter isAnimationActive={false} data={points} fill="#10b981">
                      {points.map((entry, index) => (
                        <Cell key={index} fill={entry.anomaly ? "#ef4444" : "#10b981"} />
                      ))}
                    </Scatter>
                  </ScatterChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Flagged Days</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {data.anomalies.length === 0 && (
                  <p className="text-sm text-muted-foreground">No days flagged.</p>
                )}
                {data.anomalies.map((anomaly) => (
                  <div key={anomaly.id} className="p-4 rounded-lg border border-border">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <h4 className="font-medium">{anomaly.date}</h4>
                        <Badge variant={anomaly.severity === "high" ? "destructive" : "secondary"}>
                          {anomaly.severity}
                        </Badge>
                      </div>
                      <span className="text-sm text-muted-foreground">{METHOD_LABEL[anomaly.method] ?? anomaly.method}</span>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Total sales {anomaly.value.toLocaleString()} portions vs mean {anomaly.expected.toLocaleString()}
                    </p>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        )}
      </DataState>
    </div>
  );
}
