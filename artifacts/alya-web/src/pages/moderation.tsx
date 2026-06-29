import { useEffect, useState } from "react";
import { PageTransition } from "@/components/page-transition";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { AlertTriangle, ShieldOff, Clock } from "lucide-react";

function truncateId(id: string) {
  if (!id) return "";
  return id.length > 6 ? id.substring(0, 6) + "..." : id;
}

export default function Moderation() {
  const [warnings, setWarnings] = useState<{ list: any[], total: number } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/warnings")
      .then(r => r.json())
      .then(data => {
        setWarnings(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <PageTransition className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Moderation</h1>
          <p className="text-muted-foreground">Recent infractions and warning logs across all servers.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="bg-card border-white/5 card-glow">
          <CardContent className="p-6 flex items-center gap-4">
            <div className="p-3 bg-red-500/10 rounded-lg text-red-500">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm font-semibold text-muted-foreground uppercase">Total Warnings</p>
              <div className="text-2xl font-bold text-white font-mono">
                {loading ? <Skeleton className="h-8 w-16" /> : warnings?.total?.toLocaleString() || 0}
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-card border-white/5 card-glow">
          <CardContent className="p-6 flex items-center gap-4">
            <div className="p-3 bg-orange-500/10 rounded-lg text-orange-500">
              <ShieldOff className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm font-semibold text-muted-foreground uppercase">Active Mutes</p>
              <div className="text-2xl font-bold text-white font-mono">
                {loading ? <Skeleton className="h-8 w-16" /> : "0"}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="bg-card border-white/5 card-glow">
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <Table className="table-zebra">
              <TableHeader>
                <TableRow className="border-white/5 hover:bg-transparent">
                  <TableHead className="text-muted-foreground font-semibold w-[180px]">User</TableHead>
                  <TableHead className="text-muted-foreground font-semibold w-[180px]">Moderator</TableHead>
                  <TableHead className="text-muted-foreground font-semibold">Reason</TableHead>
                  <TableHead className="text-right text-muted-foreground font-semibold w-[160px]">Time</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  Array.from({ length: 5 }).map((_, i) => (
                    <TableRow key={i} className="border-white/5">
                      <TableCell><Skeleton className="h-4 w-24 bg-white/10" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-24 bg-white/10" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-48 bg-white/10" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-24 bg-white/10 ml-auto" /></TableCell>
                    </TableRow>
                  ))
                ) : !warnings?.list || warnings.list.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={4} className="text-center py-12 text-muted-foreground">
                      <ShieldOff className="w-12 h-12 mx-auto mb-3 opacity-20" />
                      No warnings recorded yet.
                    </TableCell>
                  </TableRow>
                ) : (
                  warnings.list.map((w) => (
                    <TableRow key={w.id} className="border-white/5 transition-colors">
                      <TableCell>
                        <div className="flex flex-col">
                          <span className="font-mono text-white text-sm">{truncateId(w.user_id)}</span>
                          <span className="text-[10px] text-muted-foreground">{w.guild_id}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <span className="font-mono text-muted-foreground text-sm">{truncateId(w.moderator_id)}</span>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm text-foreground/90">{w.reason}</span>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-1.5 text-xs text-muted-foreground">
                          <Clock className="w-3.5 h-3.5" />
                          {new Date(w.timestamp).toLocaleDateString()}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </PageTransition>
  );
}
