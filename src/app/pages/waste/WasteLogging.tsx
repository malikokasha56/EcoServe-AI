import { useState } from "react";
import { Link } from "react-router";
import { ArrowLeft, CheckCircle2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/select";
import { Textarea } from "../../components/ui/textarea";
import { useFetch } from "../../lib/useFetch";
import { api } from "../../lib/api";

const today = () => new Date().toISOString().split("T")[0];

export function WasteLogging() {
  const { data: foodData } = useFetch<{ foodItems: string[] }>("/waste/food-items");

  const [date, setDate] = useState(today());
  const [foodItem, setFoodItem] = useState("");
  const [quantity, setQuantity] = useState("");
  const [unit, setUnit] = useState("");
  const [reason, setReason] = useState("");
  const [costImpact, setCostImpact] = useState("");
  const [notes, setNotes] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const resetForm = () => {
    setDate(today());
    setFoodItem("");
    setQuantity("");
    setUnit("");
    setReason("");
    setCostImpact("");
    setNotes("");
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    setError(null);
    setSuccess(false);
    try {
      await api.post("/waste", {
        date,
        foodItem,
        quantity: parseFloat(quantity) || 0,
        unit,
        reason,
        costImpact: parseFloat(costImpact) || 0,
        notes,
      });
      setSuccess(true);
      resetForm();
    } catch (e: any) {
      setError(e.response?.data?.message || e.message || "Failed to log waste entry");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild>
          <Link to="/app/waste">
            <ArrowLeft className="w-5 h-5" />
          </Link>
        </Button>
        <div>
          <h1>Log Food Waste</h1>
          <p className="text-muted-foreground mt-1">Record a waste entry. Logged entries are kept separate from the simulated overproduction.</p>
        </div>
      </div>

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>Waste Entry Details</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {success && (
            <div className="flex items-center gap-2 rounded-lg border border-[var(--success-green)]/30 bg-[var(--success-green)]/10 p-3 text-sm text-[var(--success-green)]">
              <CheckCircle2 className="w-4 h-4" />
              Waste entry logged successfully.
            </div>
          )}
          {error && (
            <div className="rounded-lg border border-[var(--error-red)]/30 bg-[var(--error-red)]/10 p-3 text-sm text-[var(--error-red)]">
              {error}
            </div>
          )}

          <div className="space-y-2">
            <Label>Date</Label>
            <Input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
          </div>

          <div className="space-y-2">
            <Label>Food Item</Label>
            <Select value={foodItem} onValueChange={setFoodItem}>
              <SelectTrigger>
                <SelectValue placeholder="Select item" />
              </SelectTrigger>
              <SelectContent>
                {foodData?.foodItems.map((item) => (
                  <SelectItem key={item} value={item}>
                    {item}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Quantity Wasted</Label>
              <Input
                type="number"
                placeholder="0"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>Unit</Label>
              <Select value={unit} onValueChange={setUnit}>
                <SelectTrigger>
                  <SelectValue placeholder="Select unit" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="kg">Kilograms (kg)</SelectItem>
                  <SelectItem value="g">Grams (g)</SelectItem>
                  <SelectItem value="L">Liters (L)</SelectItem>
                  <SelectItem value="units">Units</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label>Waste Reason</Label>
            <Select value={reason} onValueChange={setReason}>
              <SelectTrigger>
                <SelectValue placeholder="Select reason" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="expired">Expired</SelectItem>
                <SelectItem value="overproduction">Overproduction</SelectItem>
                <SelectItem value="spoiled">Spoiled</SelectItem>
                <SelectItem value="damaged">Damaged</SelectItem>
                <SelectItem value="customer-return">Customer Return</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Cost of the wasted food ($, optional)</Label>
            <Input
              type="number"
              placeholder="0.00"
              step="0.01"
              value={costImpact}
              onChange={(e) => setCostImpact(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label>Notes (Optional)</Label>
            <Textarea
              placeholder="Additional details about the waste..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
          </div>

          <Button
            onClick={handleSubmit}
            disabled={submitting}
            className="w-full bg-gradient-to-r from-[var(--eco-green)] to-[var(--eco-green-dark)]"
          >
            {submitting ? "Logging..." : "Log Waste Entry"}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
