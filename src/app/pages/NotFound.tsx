import { Link } from "react-router";
import { Home, ArrowLeft } from "lucide-react";
import { Button } from "../components/ui/button";

export function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[var(--eco-green)]/10 via-background to-[var(--ai-purple)]/10">
      <div className="text-center space-y-6 p-8">
        <h1 className="text-9xl font-bold bg-gradient-to-r from-[var(--eco-green)] to-[var(--ai-purple)] bg-clip-text text-transparent">
          404
        </h1>
        <h2 className="text-3xl font-semibold">Page Not Found</h2>
        <p className="text-muted-foreground max-w-md mx-auto">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <div className="flex items-center justify-center gap-4">
          <Button variant="outline" asChild>
            <Link to="/" className="flex items-center gap-2">
              <ArrowLeft className="w-4 h-4" />
              Go Back
            </Link>
          </Button>
          <Button asChild className="bg-gradient-to-r from-[var(--eco-green)] to-[var(--eco-green-dark)]">
            <Link to="/app" className="flex items-center gap-2">
              <Home className="w-4 h-4" />
              Dashboard
            </Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
