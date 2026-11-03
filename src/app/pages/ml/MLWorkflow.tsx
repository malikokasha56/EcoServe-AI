import { Database, Cpu, Brain, BarChart3, Sparkles, ArrowRight } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { useFetch } from "../../lib/useFetch";

const workflowSteps = [
  {
    icon: Database,
    title: "Data",
    description: "Public Kaggle dataset: Restaurant Sales Report 2024-2025 (CC BY-SA 4.0)",
    details: ["10,000 item-level daily records", "50 restaurants, 14 menu items", "January 2024 to January 2025", "No personal data"]
  },
  {
    icon: Cpu,
    title: "Preparation",
    description: "Two comparison tracks built from the same records",
    details: ["Track A: 367 daily totals with calendar and covariates", "Track B: item-level table with prior-sales feature", "History features use earlier days only", "Chronological 80/20 train/test split"]
  },
  {
    icon: Brain,
    title: "Model Training",
    description: "Trained offline by precompute.py with equal information per track",
    details: ["Track A: Prophet, LSTM, Random Forest, 2 baselines", "Each run with information sets A1 and A2", "Track B: linear, MLP, Random Forest, boosting", "Track B baselines: mean and historical average"]
  },
  {
    icon: BarChart3,
    title: "Evaluation",
    description: "Errors on unseen test days",
    details: ["WAPE, MAE, RMSE, MAPE and R²", "Rolling-origin check over 4 windows", "Diebold-Mariano significance tests", "Same test days for every model"]
  },
  {
    icon: Sparkles,
    title: "Outputs",
    description: "Stored in the database and served by the API",
    details: ["Forecasts vs actual demand", "Preparation simulation (0-20% margins)", "Preparation plan per menu item", "Anomaly flags (Z-score and IQR)"]
  }
];

interface Result {
  track: string;
  label: string;
  r2: number | null;
  wape: number | null;
}

export function MLWorkflow() {
  const { data, error } = useFetch<{ results: Result[]; best: { A: string | null; B: string | null } }>("/forecast/compare");
  const models = data?.results ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h1>Machine Learning Workflow</h1>
        <p className="text-muted-foreground mt-1">
          How the data flows from the public dataset to forecasts and suggestions
        </p>
      </div>

      <Card className="bg-gradient-to-br from-[var(--ai-purple)]/5 to-[var(--eco-green)]/5">
        <CardHeader>
          <CardTitle>AI Pipeline Architecture</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {workflowSteps.map((step, index) => (
              <div key={index}>
                <div className="flex items-start gap-6">
                  <div className="flex flex-col items-center">
                    <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-[var(--eco-green)] to-[var(--ai-purple)] flex items-center justify-center shrink-0">
                      <step.icon className="w-8 h-8 text-white" />
                    </div>
                    {index < workflowSteps.length - 1 && (
                      <div className="w-0.5 h-16 bg-gradient-to-b from-[var(--eco-green)] to-[var(--ai-purple)] my-2" />
                    )}
                  </div>
                  <div className="flex-1 pt-3">
                    <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
                    <p className="text-muted-foreground mb-4">{step.description}</p>
                    <div className="grid grid-cols-2 gap-2">
                      {step.details.map((detail, i) => (
                        <div key={i} className="flex items-center gap-2 text-sm">
                          <ArrowRight className="w-4 h-4 text-[var(--eco-green)]" />
                          <span>{detail}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Technologies Used</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {[
              { name: "TensorFlow/Keras", purpose: "LSTM model implementation" },
              { name: "Prophet", purpose: "Time series forecasting" },
              { name: "Pandas", purpose: "Data manipulation" },
              { name: "NumPy", purpose: "Numerical computations" },
              { name: "Scikit-learn", purpose: "Random Forest, gradient boosting, neural network, linear model, metrics" }
            ].map((tech, index) => (
              <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                <span className="font-medium">{tech.name}</span>
                <span className="text-sm text-muted-foreground">{tech.purpose}</span>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Model Performance</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {models.length === 0 && (
              <p className="text-sm text-muted-foreground">{error ? `Could not load model results: ${error}` : "Loading model results..."}</p>
            )}
            {models.map((m, index) => (
              <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                <span className="font-medium">
                  <span className="text-muted-foreground mr-2">{m.track === "A" ? "Daily" : "Item"}</span>
                  {m.label}
                  {(data?.best.A === m.label || data?.best.B === m.label) && (
                    <span className="ml-2 text-xs text-[var(--eco-green)]">(lowest error)</span>
                  )}
                </span>
                <span className="text-sm text-muted-foreground">
                  WAPE <span className="font-semibold text-[var(--eco-green)]">{m.wape ?? "-"}%</span>
                  {"  ·  "}R² <span className="font-semibold">{m.r2 ?? "-"}</span>
                </span>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
