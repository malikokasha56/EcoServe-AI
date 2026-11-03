import { Loader2, AlertTriangle } from "lucide-react";
import { ReactNode } from "react";

interface DataStateProps {
  loading: boolean;
  error: string | null;
  children: ReactNode;
}

// Wraps page content so every data-driven page shows a consistent loading/error state.
export function DataState({ loading, error, children }: DataStateProps) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-24 text-muted-foreground">
        <Loader2 className="w-6 h-6 animate-spin mr-2" />
        Loading data...
      </div>
    );
  }
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center">
        <AlertTriangle className="w-8 h-8 text-[var(--warning-orange)] mb-3" />
        <p className="font-medium">Could not load data</p>
        <p className="text-sm text-muted-foreground mt-1">{error}</p>
      </div>
    );
  }
  return <>{children}</>;
}
