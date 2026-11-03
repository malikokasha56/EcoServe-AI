import { Package, AlertTriangle, Clock, HeartPulse, Info } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Progress } from "../../components/ui/progress";
import { Badge } from "../../components/ui/badge";
import { useFetch } from "../../lib/useFetch";
import { DataState } from "../../components/DataState";

interface InventoryItem {
  id: number;
  name: string;
  unit: string;
  current_cost: number;
  stock: number;
  reorder_point: number;
  expiry_days: number;
  status: "good" | "low" | "critical";
}

interface InventoryData {
  items: InventoryItem[];
  stats: {
    totalItems: number;
    criticalStock: number;
    expiringSoon: number;
    healthScore: number;
  };
  illustrative: boolean;
  note: string;
}

export function Inventory() {
  const { data, loading, error } = useFetch<InventoryData>("/inventory");

  return (
    <div className="space-y-6">
      <div>
        <h1>Inventory Management</h1>
        <p className="text-muted-foreground mt-1">Stock levels and expiry dates</p>
      </div>

      <DataState loading={loading} error={error}>
        {data && (
          <div className="space-y-6">
            {data.illustrative && (
              <Card className="border-[var(--warning-orange)]/40 bg-[var(--warning-orange)]/5">
                <CardContent className="p-4 flex gap-3 text-sm">
                  <Info className="w-5 h-5 shrink-0 text-[var(--warning-orange)]" />
                  <p>{data.note}</p>
                </CardContent>
              </Card>
            )}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Total Items
                  </CardTitle>
                  <Package className="w-4 h-4 text-[var(--ai-blue)]" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-semibold">{data.stats.totalItems}</div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Critical Stock
                  </CardTitle>
                  <AlertTriangle className="w-4 h-4 text-[var(--error-red)]" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-semibold">{data.stats.criticalStock}</div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Expiring Soon
                  </CardTitle>
                  <Clock className="w-4 h-4 text-[var(--warning-orange)]" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-semibold">{data.stats.expiringSoon}</div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Health Score
                  </CardTitle>
                  <HeartPulse className="w-4 h-4 text-[var(--eco-green)]" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-semibold">{data.stats.healthScore}/100</div>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Current Inventory</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {data.items.map((item) => (
                    <div key={item.id} className="flex items-center justify-between p-4 rounded-lg border border-border">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <h4 className="font-medium">{item.name}</h4>
                          <Badge
                            variant={item.status === "critical" ? "destructive" : item.status === "low" ? "secondary" : "outline"}
                          >
                            {item.status}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mt-1">
                          {item.stock} {item.unit} in stock • Reorder at {item.reorder_point} {item.unit}
                        </p>
                        <Progress value={Math.min((item.stock / item.reorder_point) * 100, 100)} className="mt-2 h-2" />
                      </div>
                      <div className="text-right ml-4">
                        <Badge variant={item.expiry_days <= 2 ? "destructive" : "outline"}>
                          Expires in {item.expiry_days}d
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </DataState>
    </div>
  );
}
