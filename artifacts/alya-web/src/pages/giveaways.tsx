import { useEffect, useState } from "react";
import { PageTransition } from "@/components/page-transition";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Gift, PartyPopper, CheckSquare, Clock } from "lucide-react";

export default function Giveaways() {
  const [data, setData] = useState<{ list: any[], active: number, completed: number } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/giveaways")
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
          <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Giveaways</h1>
          <p className="text-muted-foreground">Manage ongoing and past community giveaways.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="bg-card border-white/5 card-glow">
          <CardContent className="p-6 flex items-center gap-4">
            <div className="p-3 bg-primary/10 rounded-lg text-primary">
              <PartyPopper className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm font-semibold text-muted-foreground uppercase">Active Giveaways</p>
              <div className="text-2xl font-bold text-white font-mono">
                {loading ? <Skeleton className="h-8 w-16" /> : data?.active?.toLocaleString() || 0}
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-card border-white/5 card-glow">
          <CardContent className="p-6 flex items-center gap-4">
            <div className="p-3 bg-secondary/10 rounded-lg text-secondary">
              <CheckSquare className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm font-semibold text-muted-foreground uppercase">Completed</p>
              <div className="text-2xl font-bold text-white font-mono">
                {loading ? <Skeleton className="h-8 w-16" /> : data?.completed?.toLocaleString() || 0}
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
                  <TableHead className="text-muted-foreground font-semibold">Prize</TableHead>
                  <TableHead className="text-muted-foreground font-semibold w-[120px] text-center">Winners</TableHead>
                  <TableHead className="text-muted-foreground font-semibold w-[180px]">Guild</TableHead>
                  <TableHead className="text-right text-muted-foreground font-semibold w-[160px]">Ends/Ended At</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  Array.from({ length: 5 }).map((_, i) => (
                    <TableRow key={i} className="border-white/5">
                      <TableCell><Skeleton className="h-6 w-20 bg-white/10 rounded-full" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-48 bg-white/10" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-12 mx-auto bg-white/10" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-24 bg-white/10" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-24 bg-white/10 ml-auto" /></TableCell>
                    </TableRow>
                  ))
                ) : !data?.list || data.list.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center py-12 text-muted-foreground">
                      <Gift className="w-12 h-12 mx-auto mb-3 opacity-20" />
                      No giveaways found.
                    </TableCell>
                  </TableRow>
                ) : (
                  data.list.map((g) => (
                    <TableRow key={g.id} className="border-white/5 transition-colors">
                      <TableCell>
                        {!g.ended ? (
                          <Badge variant="outline" className="bg-primary/10 text-primary border-primary/20 animate-pulse">Active</Badge>
                        ) : (
                          <Badge variant="outline" className="bg-gray-500/10 text-gray-400 border-gray-500/20">Ended</Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        <span className="text-sm font-medium text-white">{g.prize}</span>
                      </TableCell>
                      <TableCell className="text-center">
                        <span className="font-mono text-muted-foreground text-sm">{g.winners}</span>
                      </TableCell>
                      <TableCell>
                        <span className="text-[10px] font-mono text-muted-foreground/60">{g.guild_id}</span>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-1.5 text-xs text-muted-foreground">
                          <Clock className="w-3.5 h-3.5" />
                          {new Date(g.ends_at).toLocaleDateString()}
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
