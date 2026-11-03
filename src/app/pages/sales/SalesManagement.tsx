import { Link } from "react-router";
import { Plus, TrendingUp, DollarSign, ShoppingBag, Calendar } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { useFetch } from "../../lib/useFetch";
import { DataState } from "../../components/DataState";

interface SalesOverview {
  stats: { unitsSold: number; records: number; totalRevenue: number; avgPricePerUnit: number; date: string };
  productPerformance: { product: string; sold: number; revenue: number }[];
}

export function SalesManagement() {
  const { data, loading, error } = useFetch<SalesOverview>("/sales/overview");

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1>Sales Management</h1>
          <p className="text-muted-foreground mt-1">Sales on the latest trading day in the data, across all restaurants</p>
        </div>
        <Button asChild className="bg-gradient-to-r from-[var(--eco-green)] to-[var(--eco-green-dark)]">
          <Link to="/app/sales/add">
            <Plus className="w-4 h-4 mr-2" />
            Add Sales Entry
          </Link>
        </Button>
      </div>

      <DataState loading={loading} error={error}>
        {data && data.stats && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Portions Sold
                  </CardTitle>
                  <ShoppingBag className="w-4 h-4 text-[var(--ai-blue)]" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-semibold">{data.stats.unitsSold.toLocaleString()}</div>
                  <p className="text-xs text-muted-foreground mt-1">{data.stats.records} records on the latest day</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Total Revenue
                  </CardTitle>
                  <DollarSign className="w-4 h-4 text-[var(--eco-green)]" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-semibold">
                    ${data.stats.totalRevenue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Avg Price per Portion
                  </CardTitle>
                  <TrendingUp className="w-4 h-4 text-[var(--ai-purple)]" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-semibold">${data.stats.avgPricePerUnit.toFixed(2)}</div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Latest Sales Day
                  </CardTitle>
                  <Calendar className="w-4 h-4 text-[var(--warning-orange)]" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-semibold">{data.stats.date}</div>
                </CardContent>
              </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Revenue by Product</CardTitle>
                  <CardDescription>Top 5 items on the latest day</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={data.productPerformance}>
                      <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                      <XAxis dataKey="product" className="text-xs" />
                      <YAxis className="text-xs" />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "var(--card)",
                          border: "1px solid var(--border)",
                          borderRadius: "8px"
                        }}
                      />
                      <Bar isAnimationActive={false} dataKey="revenue" fill="#3b82f6" name="Revenue" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Portions by Product</CardTitle>
                  <CardDescription>Portions sold, top 5 items on the latest day</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={data.productPerformance}>
                      <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                      <XAxis dataKey="product" className="text-xs" />
                      <YAxis className="text-xs" />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "var(--card)",
                          border: "1px solid var(--border)",
                          borderRadius: "8px"
                        }}
                      />
                      <Bar isAnimationActive={false} dataKey="sold" fill="#10b981" name="Units Sold" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Sales History</CardTitle>
                  <Button variant="outline" size="sm" asChild>
                    <Link to="/app/sales/history">View All</Link>
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  View all recorded sales transactions in the sales history.
                </p>
              </CardContent>
            </Card>
          </>
        )}
      </DataState>
    </div>
  );
}
