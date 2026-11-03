import { useState } from "react";
import { Link } from "react-router";
import { ArrowLeft, Plus, Minus, CheckCircle2 } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { useFetch } from "../../lib/useFetch";
import { DataState } from "../../components/DataState";
import { api } from "../../lib/api";

interface MenuItem {
  id: number;
  name: string;
  price: number;
}

interface MenuItemsResponse {
  menuItems: MenuItem[];
  latestDate: string | null;
}

type CartItem = { id: number; name: string; quantity: number; price: number };

export function AddSales() {
  const { data, loading, error } = useFetch<MenuItemsResponse>("/sales/menu-items");
  const [orderItems, setOrderItems] = useState<CartItem[]>([]);
  const [date, setDate] = useState<string | null>(null);
  // Default to the latest trading day in the data, so a demo entry joins the existing timeline
  // instead of starting a new day far after the dataset ends.
  const entryDate = date ?? data?.latestDate ?? new Date().toISOString().split("T")[0];
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const addItem = (item: MenuItem) => {
    const existing = orderItems.find(i => i.id === item.id);
    if (existing) {
      setOrderItems(orderItems.map(i =>
        i.id === item.id ? { ...i, quantity: i.quantity + 1 } : i
      ));
    } else {
      setOrderItems([...orderItems, { ...item, quantity: 1 }]);
    }
  };

  const updateQuantity = (id: number, delta: number) => {
    setOrderItems(orderItems.map(item =>
      item.id === id ? { ...item, quantity: Math.max(0, item.quantity + delta) } : item
    ).filter(item => item.quantity > 0));
  };

  const total = orderItems.reduce((sum, item) => sum + item.price * item.quantity, 0);

  const completeSale = async () => {
    if (orderItems.length === 0) return;
    setSubmitting(true);
    setSuccessMsg(null);
    setErrorMsg(null);
    try {
      await api.post("/sales", {
        date: entryDate,
        items: orderItems.map(i => ({ name: i.name, quantity: i.quantity, price: i.price })),
      });
      setOrderItems([]);
      setSuccessMsg("Sale recorded successfully.");
    } catch (e: any) {
      setErrorMsg(e.response?.data?.message || e.message || "Failed to record sale");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild>
          <Link to="/app/sales">
            <ArrowLeft className="w-5 h-5" />
          </Link>
        </Button>
        <div>
          <h1>Add Sales Entry</h1>
          <p className="text-muted-foreground mt-1">Record items sold. Prices are the average selling price in the dataset.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Order Details</CardTitle>
              <CardDescription>Date of the sale</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Date</Label>
                <Input type="date" value={entryDate} onChange={(e) => setDate(e.target.value)} />
                <p className="text-xs text-muted-foreground">
                  Defaults to the latest day in the data so the entry appears in the dashboards.
                </p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Menu Items</CardTitle>
              <CardDescription>Add items to the order</CardDescription>
            </CardHeader>
            <CardContent>
              <DataState loading={loading} error={error}>
                <div className="grid grid-cols-2 gap-3">
                  {data?.menuItems.map(item => (
                    <Button
                      key={item.id}
                      variant="outline"
                      className="h-auto flex flex-col items-start p-4"
                      onClick={() => addItem(item)}
                    >
                      <span className="font-medium">{item.name}</span>
                      <span className="text-sm text-muted-foreground">${item.price.toFixed(2)}</span>
                    </Button>
                  ))}
                </div>
              </DataState>
            </CardContent>
          </Card>
        </div>

        <div>
          <Card className="sticky top-20">
            <CardHeader>
              <CardTitle>Order Summary</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {orderItems.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-8">
                  No items added yet
                </p>
              ) : (
                <>
                  <div className="space-y-3">
                    {orderItems.map(item => (
                      <div key={item.id} className="flex items-center justify-between">
                        <div className="flex-1">
                          <p className="font-medium text-sm">{item.name}</p>
                          <p className="text-xs text-muted-foreground">${item.price.toFixed(2)}</p>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button
                            size="icon"
                            variant="outline"
                            className="h-6 w-6"
                            onClick={() => updateQuantity(item.id, -1)}
                          >
                            <Minus className="w-3 h-3" />
                          </Button>
                          <span className="w-6 text-center text-sm">{item.quantity}</span>
                          <Button
                            size="icon"
                            variant="outline"
                            className="h-6 w-6"
                            onClick={() => updateQuantity(item.id, 1)}
                          >
                            <Plus className="w-3 h-3" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="border-t border-border pt-4 flex justify-between">
                    <span className="font-semibold">Total</span>
                    <span className="font-semibold text-lg">${total.toFixed(2)}</span>
                  </div>

                  <Button
                    className="w-full bg-gradient-to-r from-[var(--eco-green)] to-[var(--eco-green-dark)]"
                    onClick={completeSale}
                    disabled={submitting}
                  >
                    {submitting ? "Recording..." : "Complete Sale"}
                  </Button>
                </>
              )}

              {successMsg && (
                <div className="flex items-center gap-2 text-sm text-[var(--success-green)]">
                  <CheckCircle2 className="w-4 h-4" />
                  {successMsg}
                </div>
              )}
              {errorMsg && (
                <p className="text-sm text-[var(--error-red)]">{errorMsg}</p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
