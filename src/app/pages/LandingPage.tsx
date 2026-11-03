import { Link } from "react-router";
import { Brain, BarChart3, Lightbulb, Shield, ClipboardList, FileDown, ArrowRight, Database, AlertCircle } from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { useFetch } from "../lib/useFetch";

const features = [
  {
    icon: Brain,
    title: "Demand forecasting",
    description: "LSTM, Prophet, Random Forest and other models compared under equal information on unseen days"
  },
  {
    icon: Lightbulb,
    title: "Preparation suggestions",
    description: "Preparation quantities from the item-level forecast plus a safety margin"
  },
  {
    icon: BarChart3,
    title: "Preparation simulation",
    description: "Replays preparation plans on unseen days to compare over-preparation and unmet demand (simulated, not measured)"
  },
  {
    icon: Shield,
    title: "Anomaly detection",
    description: "Flags unusual sales days with a Z-score test combined with the interquartile range rule"
  },
  {
    icon: ClipboardList,
    title: "Sales and waste logging",
    description: "Record sales and waste entries, which appear in the dashboards and reports"
  },
  {
    icon: FileDown,
    title: "Reports",
    description: "Export sales, waste and forecast results as CSV files"
  }
];

interface PublicModel {
  label: string;
  model: string;
  info_set: string;
  mae: number | null;
  wape: number | null;
  r2: number | null;
}

interface PublicOverview {
  dataset: {
    title: string;
    author: string;
    publisher: string;
    url: string;
    licence: string;
    description: string;
    records: number;
    from: string | null;
    to: string | null;
  };
  trackA: PublicModel[];
  trackB: PublicModel[];
}

const fmt = (n: number | null | undefined, d = 1) => (n === null || n === undefined ? "-" : n.toFixed(d));

export function LandingPage() {
  const { data } = useFetch<PublicOverview>("/public/overview");

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border sticky top-0 z-50 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[var(--eco-green)] to-[var(--ai-purple)] flex items-center justify-center">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <span className="font-semibold text-xl">EcoServe AI</span>
          </div>
          <nav className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-sm hover:text-[var(--eco-green)] transition-colors">Features</a>
            <a href="#models" className="text-sm hover:text-[var(--eco-green)] transition-colors">Models</a>
            <a href="#data" className="text-sm hover:text-[var(--eco-green)] transition-colors">Data</a>
          </nav>
          <div className="flex items-center gap-4">
            <Button variant="ghost" asChild>
              <Link to="/login">Sign In</Link>
            </Button>
            <Button asChild className="bg-gradient-to-r from-[var(--eco-green)] to-[var(--eco-green-dark)]">
              <Link to="/register">Create Account</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden py-20 md:py-28">
        <div className="absolute inset-0 bg-gradient-to-br from-[var(--eco-green)]/5 via-transparent to-[var(--ai-purple)]/5" />
        <div className="container mx-auto px-6 relative z-10">
          <div className="max-w-4xl mx-auto text-center space-y-8">
            <Badge className="bg-[var(--eco-green)]/10 text-[var(--eco-green)] border-[var(--eco-green)]/20">
              MSc Computing Project &middot; Research Prototype
            </Badge>
            <h1 className="text-4xl md:text-6xl font-bold leading-tight">
              Restaurant Demand Forecasting
              <br />
              <span className="bg-gradient-to-r from-[var(--eco-green)] to-[var(--ai-purple)] bg-clip-text text-transparent">
                and Preparation Planning
              </span>
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              A decision-support prototype that compares forecasting models on a public restaurant sales
              dataset and turns forecasts into preparation suggestions, with the aim of reducing food overproduction.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button size="lg" asChild className="bg-gradient-to-r from-[var(--eco-green)] to-[var(--eco-green-dark)]">
                <Link to="/login" className="flex items-center gap-2">
                  Open the Demo
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" asChild>
                <a href="#models">See Model Results</a>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Facts from the data */}
      <section className="py-12 border-y border-border bg-muted/30">
        <div className="container mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-3xl font-bold">{data ? data.dataset.records.toLocaleString() : "-"}</div>
              <div className="text-sm text-muted-foreground mt-2">Sales records</div>
            </div>
            <div>
              <div className="text-3xl font-bold">50</div>
              <div className="text-sm text-muted-foreground mt-2">Restaurants in the dataset</div>
            </div>
            <div>
              <div className="text-3xl font-bold">{data?.dataset.from ? `${data.dataset.from.slice(0, 7)} to ${data.dataset.to?.slice(0, 7)}` : "-"}</div>
              <div className="text-sm text-muted-foreground mt-2">Period covered</div>
            </div>
            <div>
              <div className="text-3xl font-bold">{data ? new Set([...data.trackA, ...data.trackB].map((m) => m.model)).size : "-"}</div>
              <div className="text-sm text-muted-foreground mt-2">Models and baselines compared</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20">
        <div className="container mx-auto px-6">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">What the System Does</h2>
            <p className="text-muted-foreground">
              A Flask API, a database and a React dashboard around a machine learning layer
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <Card key={index} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6 space-y-4">
                  <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-[var(--eco-green)]/20 to-[var(--ai-purple)]/20 flex items-center justify-center">
                    <feature.icon className="w-6 h-6 text-[var(--eco-green)]" />
                  </div>
                  <h3 className="font-semibold text-lg">{feature.title}</h3>
                  <p className="text-sm text-muted-foreground">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Model results, read live from the system */}
      <section id="models" className="py-20 bg-muted/30">
        <div className="container mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Measured Model Results</h2>
            <p className="text-muted-foreground">
              Errors on the held-out test period (the last 20% of days). Within each table every model receives the same
              information. Lower WAPE is better; an R&sup2; of 0 means no better than always predicting the average.
            </p>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-6xl mx-auto">
            {[
              { title: "Daily total demand", note: "All restaurants combined, one forecast per day", rows: data?.trackA ?? [] },
              { title: "Item-level demand", note: "One forecast per restaurant, menu item and day", rows: data?.trackB ?? [] },
            ].map((t) => (
              <Card key={t.title}>
                <CardContent className="p-6 space-y-4">
                  <div>
                    <h3 className="text-xl font-bold">{t.title}</h3>
                    <p className="text-sm text-muted-foreground">{t.note}</p>
                  </div>
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-border text-left text-muted-foreground">
                        <th className="py-2 font-medium">Model</th>
                        <th className="py-2 font-medium text-right">WAPE</th>
                        <th className="py-2 font-medium text-right">R&sup2;</th>
                      </tr>
                    </thead>
                    <tbody>
                      {t.rows.map((m) => (
                        <tr key={m.label} className="border-b border-border">
                          <td className="py-2">{m.label}</td>
                          <td className="py-2 text-right font-medium">{fmt(m.wape)}%</td>
                          <td className="py-2 text-right">{fmt(m.r2, 2)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </CardContent>
              </Card>
            ))}
          </div>
          <p className="text-sm text-muted-foreground text-center max-w-3xl mx-auto mt-8">
            A1 uses demand history and the calendar; A2 also uses the day's promotion, event and weather mix. The
            significance tests and the full method are shown in the application.
          </p>
        </div>
      </section>

      {/* Data and limitations */}
      <section id="data" className="py-20">
        <div className="container mx-auto px-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-5xl mx-auto">
            <Card>
              <CardContent className="p-8 space-y-4">
                <div className="flex items-center gap-3">
                  <Database className="w-6 h-6 text-[var(--eco-green)]" />
                  <h3 className="text-xl font-bold">Data Source</h3>
                </div>
                <p className="text-sm">
                  {data ? (
                    <>
                      <a href={data.dataset.url} target="_blank" rel="noreferrer" className="text-[var(--eco-green)] hover:underline font-medium">
                        {data.dataset.title}
                      </a>{" "}
                      by {data.dataset.author}, published on {data.dataset.publisher} under the {data.dataset.licence} licence.
                    </>
                  ) : (
                    "Restaurant Sales Report 2024-2025 by Alexand Chen, published on Kaggle under the CC BY-SA 4.0 licence."
                  )}
                </p>
                <p className="text-sm text-muted-foreground">
                  A publicly available secondary dataset with no personal data. No human participants were
                  involved in this project.
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-8 space-y-4">
                <div className="flex items-center gap-3">
                  <AlertCircle className="w-6 h-6 text-[var(--warning-orange)]" />
                  <h3 className="text-xl font-bold">Limitations</h3>
                </div>
                <p className="text-sm text-muted-foreground">
                  This prototype has been evaluated on historical public data only. It has not been deployed in a
                  restaurant, and the dataset contains no waste measurements, so food waste reduction has not been
                  measured. Waste figures in the application are estimates derived from forecasts.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-12">
        <div className="container mx-auto px-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--eco-green)] to-[var(--ai-purple)] flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <span className="font-semibold">EcoServe AI</span>
            </div>
            <p className="text-sm text-muted-foreground">
              MSc Computing Project &middot; Data: Restaurant Sales Report 2024-2025 (Kaggle, CC BY-SA 4.0)
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
