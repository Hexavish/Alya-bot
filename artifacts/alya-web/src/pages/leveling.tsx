import { useEffect, useState } from "react";
import { PageTransition } from "@/components/page-transition";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Progress } from "@/components/ui/progress";
import { Trophy, Star, Users } from "lucide-react";

function truncateId(id: string) {
  if (!id) return "";
  return id.length > 6 ? id.substring(0, 6) + "..." : id;
}

export default function Leveling() {
  const [leaderboard, setLeaderboard] = useState<any[]>([]);
  const [members, setMembers] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch("/api/leveling/leaderboard").then(r => r.json()),
      fetch("/api/members").then(r => r.json())
    ]).then(([lb, mem]) => {
      setLeaderboard(lb || []);
      setMembers(mem);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  return (
    <PageTransition className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Leveling</h1>
          <p className="text-muted-foreground">Global experience and leveling leaderboards.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-card border-white/5 card-glow">
          <CardContent className="p-6 flex items-center gap-4">
            <div className="p-3 bg-purple-500/10 rounded-lg text-purple-500">
              <Star className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm font-semibold text-muted-foreground uppercase">Avg Level</p>
              <div className="text-2xl font-bold text-white font-mono">
                {loading ? <Skeleton className="h-8 w-16" /> : members?.avgLevel?.toLocaleString() || 0}
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-card border-white/5 card-glow">
          <CardContent className="p-6 flex items-center gap-4">
            <div className="p-3 bg-indigo-500/10 rounded-lg text-indigo-500">
              <Trophy className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm font-semibold text-muted-foreground uppercase">Leveled Users</p>
              <div className="text-2xl font-bold text-white font-mono">
                {loading ? <Skeleton className="h-8 w-24" /> : members?.leveled?.toLocaleString() || 0}
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-card border-white/5 card-glow">
          <CardContent className="p-6 flex items-center gap-4">
            <div className="p-3 bg-blue-500/10 rounded-lg text-blue-500">
              <Users className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm font-semibold text-muted-foreground uppercase">Total Members</p>
              <div className="text-2xl font-bold text-white font-mono">
                {loading ? <Skeleton className="h-8 w-16" /> : members?.total?.toLocaleString() || 0}
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
                  <TableHead className="w-16 text-center text-muted-foreground font-semibold">Rank</TableHead>
                  <TableHead className="text-muted-foreground font-semibold">User</TableHead>
                  <TableHead className="text-center text-muted-foreground font-semibold">Level</TableHead>
                  <TableHead className="text-right text-muted-foreground font-semibold w-1/3">Progress</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  Array.from({ length: 5 }).map((_, i) => (
                    <TableRow key={i} className="border-white/5">
                      <TableCell><Skeleton className="h-4 w-8 mx-auto bg-white/10" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-32 bg-white/10" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-12 mx-auto bg-white/10" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-full bg-white/10" /></TableCell>
                    </TableRow>
                  ))
                ) : leaderboard.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={4} className="text-center py-8 text-muted-foreground">
                      No leveling data available.
                    </TableCell>
                  </TableRow>
                ) : (
                  leaderboard.map((u, i) => {
                    // Simple mock progress calculation for viz
                    const progress = (u.xp % 1000) / 10;
                    return (
                      <TableRow key={u.user_id} className="border-white/5 transition-colors">
                        <TableCell className="text-center font-bold">
                          {i === 0 ? <span className="text-yellow-400">1</span> :
                           i === 1 ? <span className="text-gray-300">2</span> :
                           i === 2 ? <span className="text-amber-600">3</span> :
                           <span className="text-muted-foreground">{i + 1}</span>}
                        </TableCell>
                        <TableCell>
                          <div className="flex flex-col">
                            <span className="font-mono text-white text-sm">{truncateId(u.user_id)}</span>
                            <span className="text-[10px] text-muted-foreground">{u.guild_id}</span>
                          </div>
                        </TableCell>
                        <TableCell className="text-center">
                          <span className="inline-flex items-center justify-center w-8 h-8 rounded bg-primary/20 text-primary font-bold font-mono text-sm shadow-[0_0_10px_rgba(244,114,182,0.2)]">
                            {u.level}
                          </span>
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="flex flex-col gap-1.5 w-full">
                            <div className="flex justify-between text-[10px] font-mono text-muted-foreground">
                              <span>{u.xp?.toLocaleString()} XP</span>
                              <span>Next Lvl</span>
                            </div>
                            <Progress value={progress} className="h-2 bg-white/5" />
                          </div>
                        </TableCell>
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </PageTransition>
  );
}
