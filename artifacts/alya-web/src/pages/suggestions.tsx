import { useEffect, useState } from "react";
import { PageTransition } from "@/components/page-transition";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { MessageSquare, Clock, Check, X } from "lucide-react";

function truncateId(id: string) {
  if (!id) return "";
  return id.length > 6 ? id.substring(0, 6) + "..." : id;
}

export default function Suggestions() {
  const [data, setData] = useState<{ list: any[], pending: number, approved: number, denied: number } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/suggestions")
      .then(r => r.json())
      .then(d => {
        setData(d);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <PageTransition className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Suggestions</h1>
          <p className="text-muted-foreground">Community ideas and feedback across servers.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-card border-white/5 card-glow">
          <CardContent className="p-6 flex items-center gap-4">
            <div className="p-3 bg-yellow-500/10 rounded-lg text-yellow-500">
              <Clock className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm font-semibold text-muted-foreground uppercase">Pending</p>
              <div className="text-2xl font-bold text-white font-mono">
                {loading ? <Skeleton className="h-8 w-16" /> : data?.pending?.toLocaleString() || 0}
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-card border-white/5 card-glow">
          <CardContent className="p-6 flex items-center gap-4">
            <div className="p-3 bg-emerald-500/10 rounded-lg text-emerald-500">
              <Check className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm font-semibold text-muted-foreground uppercase">Approved</p>
              <div className="text-2xl font-bold text-white font-mono">
                {loading ? <Skeleton className="h-8 w-16" /> : data?.approved?.toLocaleString() || 0}
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-card border-white/5 card-glow">
          <CardContent className="p-6 flex items-center gap-4">
            <div className="p-3 bg-red-500/10 rounded-lg text-red-500">
              <X className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm font-semibold text-muted-foreground uppercase">Denied</p>
              <div className="text-2xl font-bold text-white font-mono">
                {loading ? <Skeleton className="h-8 w-16" /> : data?.denied?.toLocaleString() || 0}
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
                  <TableHead className="text-muted-foreground font-semibold w-[120px]">Status</TableHead>
                  <TableHead className="text-muted-foreground font-semibold">Suggestion</TableHead>
                  <TableHead className="text-muted-foreground font-semibold w-[180px]">User / Guild</TableHead>
                  <TableHead className="text-right text-muted-foreground font-semibold w-[160px]">Date</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  Array.from({ length: 5 }).map((_, i) => (
                    <TableRow key={i} className="border-white/5">
                      <TableCell><Skeleton className="h-6 w-20 bg-white/10 rounded-full" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-full max-w-md bg-white/10" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-24 bg-white/10" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-24 bg-white/10 ml-auto" /></TableCell>
                    </TableRow>
                  ))
                ) : !data?.list || data.list.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={4} className="text-center py-12 text-muted-foreground">
                      <MessageSquare className="w-12 h-12 mx-auto mb-3 opacity-20" />
                      No suggestions found.
                    </TableCell>
                  </TableRow>
                ) : (
                  data.list.map((s) => (
                    <TableRow key={s.id} className="border-white/5 transition-colors">
                      <TableCell>
                        {s.status === "pending" && <Badge variant="outline" className="bg-yellow-500/10 text-yellow-500 border-yellow-500/20">Pending</Badge>}
                        {s.status === "approved" && <Badge variant="outline" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20">Approved</Badge>}
                        {s.status === "denied" && <Badge variant="outline" className="bg-red-500/10 text-red-500 border-red-500/20">Denied</Badge>}
                      </TableCell>
                      <TableCell>
                        <span className="text-sm text-foreground/90">{s.suggestion}</span>
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-col">
                          <span className="font-mono text-muted-foreground text-sm">{truncateId(s.user_id)}</span>
                          <span className="text-[10px] text-muted-foreground/60">{s.guild_id}</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-1.5 text-xs text-muted-foreground">
                          <Clock className="w-3.5 h-3.5" />
                          {new Date(s.created_at).toLocaleDateString()}
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
