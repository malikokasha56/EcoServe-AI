import { Link } from "react-router";
import { Brain, ArrowLeft } from "lucide-react";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";

// Password reset by email is out of scope for this prototype, so the page says so instead of simulating it.
export function ForgotPassword() {
  return (
    <div className="min-h-screen w-full flex items-center justify-center p-6 bg-gradient-to-br from-[var(--eco-green)]/10 via-background to-[var(--ai-purple)]/10">
      <div className="w-full max-w-md">
        <div className="flex items-center justify-center gap-3 mb-8">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[var(--eco-green)] to-[var(--ai-purple)] flex items-center justify-center shadow-lg">
            <Brain className="w-7 h-7 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-semibold">EcoServe AI</h1>
            <p className="text-sm text-muted-foreground">Demand Forecasting Prototype</p>
          </div>
        </div>

        <Card className="backdrop-blur-sm bg-card/95 border-border/50 shadow-2xl">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl">Reset password</CardTitle>
            <CardDescription>Not available in this prototype</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Password reset by email is not implemented, because the prototype runs locally without an email
              service. Sign in with the demo account (manager@restaurant.com / password123) or create a new account.
            </p>
            <Button asChild variant="outline" className="w-full">
              <Link to="/login">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to sign in
              </Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
