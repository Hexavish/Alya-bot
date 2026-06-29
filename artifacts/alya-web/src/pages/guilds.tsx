import { useEffect, useState } from "react";
import { Server, Users, Settings2, ShieldAlert, MessageSquare, Ticket, FileText } from "lucide-react";
import { PageTransition } from "@/components/page-transition";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

export default function Guilds() {
  const [guilds, setGuilds] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/guilds")
      .then(res => res.json())
      .then(data => {
        setGuilds(data || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <PageTransition className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Guilds</h1>
        <p className="text-muted-foreground">Manage and view all servers Alya is currently in.</p>
      </div>

      <Card className="bg-card border-white/5 card-glow">
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <Table className="table-zebra">
              <TableHeader>
                <TableRow className="border-white/5 hover:bg-transparent">
                  <TableHead className="text-muted-foreground font-semibold">Guild ID</TableHead>
                  <TableHead className="text-muted-foreground font-semibold text-right">Members</TableHead>
                  <TableHead className="text-muted-foreground font-semibold text-right">Warnings</TableHead>
                  <TableHead className="text-muted-foreground font-semibold text-right">Tickets</TableHead>
                  <TableHead className="text-muted-foreground font-semibold">Features</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  Array.from({ length: 5 }).map((_, i) => (
                    <TableRow key={i} className="border-white/5">
                      <TableCell><Skeleton className="h-4 w-32 bg-white/10" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-12 bg-white/10 ml-auto" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-12 bg-white/10 ml-auto" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-12 bg-white/10 ml-auto" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-48 bg-white/10" /></TableCell>
                    </TableRow>
                  ))
                ) : guilds.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                      No guilds found. Add Alya to a server first!
                    </TableCell>
                  </TableRow>
                ) : (
                  guilds.map((g) => (
                    <TableRow key={g.guild_id} className="border-white/5 transition-colors">
                      <TableCell className="font-mono text-white text-sm">{g.guild_id}</TableCell>
                      <TableCell className="text-right font-mono text-sm text-muted-foreground">
                        <span className="flex items-center justify-end gap-1.5"><Users className="w-3.5 h-3.5"/> {g.member_count?.toLocaleString() || 0}</span>
                      </TableCell>
                      <TableCell className="text-right font-mono text-sm text-yellow-500/80">
                        {g.warning_count || 0}
                      </TableCell>
                      <TableCell className="text-right font-mono text-sm text-emerald-500/80">
                        {g.ticket_count || 0}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2 flex-wrap">
                          {g.welcome_enabled ? (
                            <Badge variant="outline" className="bg-primary/10 text-primary border-primary/20"><Settings2 className="w-3 h-3 mr-1"/> Welcome</Badge>
                          ) : null}
                          {g.has_logging ? (
                            <Badge variant="outline" className="bg-blue-500/10 text-blue-400 border-blue-500/20"><FileText className="w-3 h-3 mr-1"/> Logging</Badge>
                          ) : null}
                          {g.has_suggestions ? (
                            <Badge variant="outline" className="bg-purple-500/10 text-purple-400 border-purple-500/20"><MessageSquare className="w-3 h-3 mr-1"/> Suggest</Badge>
                          ) : null}
                          {g.has_tickets ? (
                            <Badge variant="outline" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20"><Ticket className="w-3 h-3 mr-1"/> Tickets</Badge>
                          ) : null}
                          {!g.welcome_enabled && !g.has_logging && !g.has_suggestions && !g.has_tickets && (
                            <span className="text-xs text-muted-foreground italic">None active</span>
                          )}
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
