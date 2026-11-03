import { useState } from "react";
import { Link } from "react-router";
import { ArrowLeft, Download, Search } from "lucide-react";
import { Card, CardContent, CardHeader } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { useFetch } from "../../lib/useFetch";
import { DataState } from "../../components/DataState";
import { api } from "../../lib/api";
import { toast } from "sonner";

interface SaleRow {
  id: number;
  date: string;
  item: string;
  mealType: string | null;
  quantity: number;
  revenue: number;
}

interface HistoryResponse {
  history?: SaleRow[];
  sales?: { id: number; date: string; menu_item_name: string; meal_type: string | null; quantity_sold: number; revenue: number }[];
}

// Searches run on the server over every record: a YYYY-MM-DD term filters by date, anything else by menu item.
function searchUrl(term: string) {
  if (!term) return "/sales/history";
  if (/^\d{4}-\d{2}-\d{2}$/.test(term)) return `/sales?date=${term}&limit=500`;
  return `/sales?search=${encodeURIComponent(term)}&limit=500`;
}

export function SalesHistory() {
  const [input, setInput] = useState("");
  const [term, setTerm] = useState("");
  const [exporting, setExporting] = useState(false);
  const { data, loading, error } = useFetch<HistoryResponse>(searchUrl(term));

  const rows: SaleRow[] = data?.history ?? (data?.sales ?? []).map((s) => ({
    id: s.id, date: s.date, item: s.menu_item_name, mealType: s.meal_type, quantity: s.quantity_sold, revenue: s.revenue,
  }));

  async function handleExport() {
    setExporting(true);
    try {
      const res = await api.get("/reports/sales/download", { responseType: "blob" });
      const url = URL.createObjectURL(res.data);
      const link = document.createElement("a");
      link.href = url;
      link.download = "sales_report.csv";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch {
      toast.error("Export failed");
    } finally {
      setExporting(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild>
          <Link to="/app/sales">
            <ArrowLeft className="w-5 h-5" />
          </Link>
        </Button>
        <div className="flex-1">
          <h1>Sales History</h1>
          <p className="text-muted-foreground mt-1">
            {term ? `Records matching "${term}" (up to 500)` : "Most recent 200 sales records (one record = one menu item at one restaurant on one day)"}
          </p>
        </div>
        <Button variant="outline" onClick={handleExport} disabled={exporting}>
          <Download className="w-4 h-4 mr-2" />
          {exporting ? "Exporting..." : "Export All (CSV)"}
        </Button>
      </div>

      <Card>
        <CardHeader>
          <form
            className="flex gap-2"
            onSubmit={(e) => {
              e.preventDefault();
              setTerm(input.trim());
            }}
          >
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search all records by menu item, or by date as YYYY-MM-DD, then press Enter"
                className="pl-10"
                value={input}
                onChange={(e) => setInput(e.target.value)}
              />
            </div>
            <Button type="submit" variant="outline">Search</Button>
            {term && (
              <Button type="button" variant="ghost" onClick={() => { setInput(""); setTerm(""); }}>Clear</Button>
            )}
          </form>
        </CardHeader>
        <CardContent>
          <DataState loading={loading} error={error}>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left py-3 px-4 font-medium text-sm">Record</th>
                    <th className="text-left py-3 px-4 font-medium text-sm">Date</th>
                    <th className="text-left py-3 px-4 font-medium text-sm">Menu Item</th>
                    <th className="text-left py-3 px-4 font-medium text-sm">Meal</th>
                    <th className="text-right py-3 px-4 font-medium text-sm">Quantity</th>
                    <th className="text-right py-3 px-4 font-medium text-sm">Revenue</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((sale) => (
                    <tr key={sale.id} className="border-b border-border hover:bg-accent/50 transition-colors">
                      <td className="py-3 px-4 text-sm text-muted-foreground">#{sale.id}</td>
                      <td className="py-3 px-4 text-sm">{sale.date}</td>
                      <td className="py-3 px-4 text-sm font-medium">{sale.item}</td>
                      <td className="py-3 px-4 text-sm text-muted-foreground">{sale.mealType ?? "-"}</td>
                      <td className="py-3 px-4 text-sm text-right">{sale.quantity}</td>
                      <td className="py-3 px-4 text-sm text-right font-medium">${sale.revenue.toFixed(2)}</td>
                    </tr>
                  ))}
                  {rows.length === 0 && (
                    <tr>
                      <td colSpan={6} className="py-8 text-center text-sm text-muted-foreground">
                        No sales records found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </DataState>
        </CardContent>
      </Card>
    </div>
  );
}
