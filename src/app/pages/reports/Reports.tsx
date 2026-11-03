import { useState } from "react";
import { FileText, Download, Database } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Badge } from "../../components/ui/badge";
import { useFetch } from "../../lib/useFetch";
import { api } from "../../lib/api";

interface Report {
  id: string;
  name: string;
  type: string;
  records: number;
}

interface ReportsData {
  reports: Report[];
  summary: {
    available: number;
    totalRecords: number;
  };
}

export function Reports() {
  const { data, loading, error } = useFetch<ReportsData>("/reports");
  const [downloadingId, setDownloadingId] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const handleDownload = async (id: string) => {
    setActionError(null);
    setDownloadingId(id);
    try {
      const res = await api.get(`/reports/${id}/download`, { responseType: "blob" });
      const url = URL.createObjectURL(res.data);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${id}_report.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (e: any) {
      setActionError(e.response?.data?.message || e.message || "Download failed");
    } finally {
      setDownloadingId(null);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1>Reports</h1>
        <p className="text-muted-foreground mt-1">Download the data behind the dashboards as CSV files</p>
      </div>

      {actionError && (
        <p className="text-sm text-[var(--error-red)]">{actionError}</p>
      )}

      {data && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Available Reports
              </CardTitle>
              <FileText className="w-4 h-4 text-[var(--ai-blue)]" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-semibold">{data.summary.available}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Records
              </CardTitle>
              <Database className="w-4 h-4 text-[var(--ai-purple)]" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-semibold">{data.summary.totalRecords}</div>
            </CardContent>
          </Card>
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Available Reports</CardTitle>
          <CardDescription>Each file contains every record of that type currently in the database</CardDescription>
        </CardHeader>
        <CardContent>
          {loading && <p className="text-sm text-muted-foreground">Loading reports...</p>}
          {error && <p className="text-sm text-[var(--error-red)]">{error}</p>}
          <div className="space-y-4">
            {data?.reports.map((report) => (
              <div key={report.id} className="flex items-center justify-between p-4 rounded-lg border border-border hover:bg-accent/50 transition-colors">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-lg bg-[var(--eco-green)]/10 flex items-center justify-center">
                    <FileText className="w-5 h-5 text-[var(--eco-green)]" />
                  </div>
                  <div>
                    <h4 className="font-medium">{report.name}</h4>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant="outline" className="text-xs">{report.type}</Badge>
                      <span className="text-xs text-muted-foreground">{report.records} records</span>
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    onClick={() => handleDownload(report.id)}
                    disabled={downloadingId === report.id}
                  >
                    <Download className="w-4 h-4 mr-2" />
                    {downloadingId === report.id ? "Downloading..." : "Download"}
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
