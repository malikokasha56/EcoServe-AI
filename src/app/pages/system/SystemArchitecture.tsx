import { Code, Server, Database, Brain, Globe, Shield } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";

const techStack = {
  frontend: [
    { name: "React.js 18", description: "UI library" },
    { name: "TypeScript", description: "Type safety" },
    { name: "TailwindCSS v4", description: "Styling" },
    { name: "Recharts", description: "Data visualization" },
    { name: "React Router", description: "Navigation" }
  ],
  backend: [
    { name: "Flask", description: "Python web framework" },
    { name: "SQLAlchemy", description: "ORM" },
    { name: "SQLite", description: "Default database (PostgreSQL optional)" },
    { name: "JWT + Bcrypt", description: "Auth & hashing" }
  ],
  ai: [
    { name: "TensorFlow/Keras", description: "LSTM model" },
    { name: "Prophet", description: "Time series forecasting" },
    { name: "Scikit-learn", description: "Random Forest, gradient boosting, MLP, linear model" },
    { name: "Pandas", description: "Data processing" },
    { name: "NumPy", description: "Numerical computing" }
  ],
  deployment: [
    { name: "Waitress", description: "Serves API and built frontend on one port" },
    { name: "START.bat / EcoServe.exe", description: "One-click local start" },
    { name: "Local single-tenant", description: "Runs on one machine" }
  ]
};

export function SystemArchitecture() {
  return (
    <div className="space-y-6">
      <div>
        <h1>System Architecture</h1>
        <p className="text-muted-foreground mt-1">
          Technical stack and infrastructure overview
        </p>
      </div>

      <Card className="bg-gradient-to-br from-[var(--ai-purple)]/5 to-[var(--eco-green)]/5">
        <CardHeader>
          <CardTitle>Architecture Diagram</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-8 p-6">
            <div className="flex items-center justify-center gap-8">
              <div className="text-center">
                <div className="w-32 h-32 rounded-xl bg-gradient-to-br from-[var(--eco-green)] to-[var(--eco-green-dark)] flex items-center justify-center mb-3">
                  <Code className="w-16 h-16 text-white" />
                </div>
                <p className="font-semibold">Frontend</p>
                <p className="text-sm text-muted-foreground">React + TailwindCSS</p>
              </div>

              <div className="text-4xl text-muted-foreground">→</div>

              <div className="text-center">
                <div className="w-32 h-32 rounded-xl bg-gradient-to-br from-[var(--ai-blue)] to-[var(--ai-purple)] flex items-center justify-center mb-3">
                  <Server className="w-16 h-16 text-white" />
                </div>
                <p className="font-semibold">Backend</p>
                <p className="text-sm text-muted-foreground">Flask REST API</p>
              </div>

              <div className="text-4xl text-muted-foreground">→</div>

              <div className="text-center">
                <div className="w-32 h-32 rounded-xl bg-gradient-to-br from-[var(--ai-purple)] to-[var(--warning-orange)] flex items-center justify-center mb-3">
                  <Brain className="w-16 h-16 text-white" />
                </div>
                <p className="font-semibold">AI Engine</p>
                <p className="text-sm text-muted-foreground">ML Models</p>
              </div>
            </div>

            <div className="text-4xl text-center text-muted-foreground">↓</div>

            <div className="flex items-center justify-center gap-8">
              <div className="text-center">
                <div className="w-32 h-32 rounded-xl bg-gradient-to-br from-[var(--warning-orange)] to-[var(--error-red)] flex items-center justify-center mb-3">
                  <Database className="w-16 h-16 text-white" />
                </div>
                <p className="font-semibold">Database</p>
                <p className="text-sm text-muted-foreground">SQLite / PostgreSQL</p>
              </div>

              <div className="text-center">
                <div className="w-32 h-32 rounded-xl bg-gradient-to-br from-[var(--eco-green)] to-[var(--ai-blue)] flex items-center justify-center mb-3">
                  <Globe className="w-16 h-16 text-white" />
                </div>
                <p className="font-semibold">Deployment</p>
                <p className="text-sm text-muted-foreground">Local, one port</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Code className="w-5 h-5 text-[var(--eco-green)]" />
              <CardTitle>Frontend Stack</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {techStack.frontend.map((tech, index) => (
              <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                <span className="font-medium">{tech.name}</span>
                <Badge variant="outline">{tech.description}</Badge>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Server className="w-5 h-5 text-[var(--ai-blue)]" />
              <CardTitle>Backend Stack</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {techStack.backend.map((tech, index) => (
              <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                <span className="font-medium">{tech.name}</span>
                <Badge variant="outline">{tech.description}</Badge>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-[var(--ai-purple)]" />
              <CardTitle>AI/ML Stack</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {techStack.ai.map((tech, index) => (
              <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                <span className="font-medium">{tech.name}</span>
                <Badge variant="outline">{tech.description}</Badge>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Shield className="w-5 h-5 text-[var(--success-green)]" />
              <CardTitle>Deployment</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {techStack.deployment.map((tech, index) => (
              <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                <span className="font-medium">{tech.name}</span>
                <Badge variant="outline">{tech.description}</Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
